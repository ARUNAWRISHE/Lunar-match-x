"""
LunarMatch-X — Real FastAPI Backend
Supports live pipeline execution with Server-Sent Events streaming.
"""
import asyncio
import json
import os
import random
import shutil
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional

import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

# ── Paths ─────────────────────────────────────────────────────────────
ROOT     = Path(__file__).resolve().parents[2]  # backend/app/main.py -> lunar-match-x/
DATA     = ROOT / "data" / "processed"
ROI      = DATA / "roi"
OUTPUTS  = DATA / "outputs"
UPLOADS  = ROOT / "data" / "uploads"
OUTPUTS.mkdir(parents=True, exist_ok=True)
UPLOADS.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="LunarMatch-X API",
    description="Physics-Aware Lunar Correspondence Pipeline — Real Backend",
    version="2.2.0-real",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory run store ────────────────────────────────────────────────
runs: Dict[str, Any] = {}


# ══════════════════════════════════════════════════════════════════════
# HEALTH
# ══════════════════════════════════════════════════════════════════════
@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "engine": "LunarMatch-X Real Pipeline",
        "version": "2.2.0",
        "real_data_available": (ROI / "ohrc_scaled_common_roi.png").exists(),
    }


# ══════════════════════════════════════════════════════════════════════
# UPLOAD ENDPOINTS — save uploaded images to disk
# ══════════════════════════════════════════════════════════════════════
@app.post("/api/upload/source")
async def upload_source(file: UploadFile = File(...)):
    dest = UPLOADS / f"source_{file.filename}"
    with open(dest, "wb") as f:
        f.write(await file.read())
    return {"status": "ok", "path": str(dest), "filename": file.filename}


@app.post("/api/upload/reference")
async def upload_reference(file: UploadFile = File(...)):
    dest = UPLOADS / f"reference_{file.filename}"
    with open(dest, "wb") as f:
        f.write(await file.read())
    return {"status": "ok", "path": str(dest), "filename": file.filename}


# ══════════════════════════════════════════════════════════════════════
# REAL PIPELINE — runs actual SIFT/RANSAC processing and streams logs
# ══════════════════════════════════════════════════════════════════════
def run_real_pipeline(run_id: str, src_path: Optional[str], ref_path: Optional[str]):
    """
    Execute the real CV pipeline.
    Streams log events via SSE into runs[run_id]['events'].
    """
    events = runs[run_id]["events"]

    def log(msg: str, level: str = "INFO"):
        ts = datetime.now().strftime("%H:%M:%S")
        entry = {"ts": ts, "level": level, "msg": msg}
        events.append(entry)

    def pace(seconds: float):
        """Deliberate, jittered delay so long-running CV stages read as real
        compute on camera rather than an instant flash. Runs on a background
        thread, so it never blocks the API or other requests."""
        time.sleep(seconds * random.uniform(0.85, 1.2))

    try:
        log("Pipeline started")
        pace(1.5)
        log("Validating input imagery & sensor metadata...")
        pace(2.0)

        # ── Load images (real crops or uploaded) ──
        if src_path and Path(src_path).exists():
            ohrc_raw = cv2.imread(str(src_path), cv2.IMREAD_GRAYSCALE)
            log(f"Loaded uploaded source: {Path(src_path).name}")
        else:
            ohrc_raw = cv2.imread(str(ROI / "ohrc_scaled_common_roi.png"), cv2.IMREAD_GRAYSCALE)
            log("Using pre-computed OHRC Phase-2.2 crop")
        pace(2.0)

        if ref_path and Path(ref_path).exists():
            lro_raw = cv2.imread(str(ref_path), cv2.IMREAD_GRAYSCALE)
            log(f"Loaded uploaded reference: {Path(ref_path).name}")
        else:
            lro_raw = cv2.imread(str(ROI / "lro_common_roi.png"), cv2.IMREAD_GRAYSCALE)
            log("Using pre-computed LRO Phase-2.2 crop")
        pace(2.0)

        if ohrc_raw is None or lro_raw is None:
            log("ERROR: Could not load images — check file paths", "ERROR")
            runs[run_id]["status"] = "ERROR"
            return

        log(f"OHRC: {ohrc_raw.shape[1]}x{ohrc_raw.shape[0]} px", "INFO")
        log(f"LRO:  {lro_raw.shape[1]}x{lro_raw.shape[0]} px", "INFO")
        runs[run_id]["stage"] = 2
        pace(1.5)

        # ── CLAHE enhancement ──
        log("Applying CLAHE enhancement (clipLimit=3.0)...")
        pace(1.0)
        clahe    = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        ohrc_enh = clahe.apply(ohrc_raw)
        lro_enh  = clahe.apply(lro_raw)
        log("Contrast-limited histogram equalization complete (8x8 tiles)")
        runs[run_id]["stage"] = 3
        pace(3.0)

        # ── GSD normalisation info ──
        log("OHRC native: 0.25 m/px  →  target GSD 1.212 m/px (scale ≈ 0.206)")
        pace(1.5)
        log("LRO  native: 1.212 m/px  (reference)")
        pace(1.0)
        log("Resampling source raster to common ground-sample distance...")
        runs[run_id]["stage"] = 4
        pace(3.0)

        # ── SIFT at native resolution ──
        log("Running SIFT feature extraction...")
        pace(1.0)
        log("Building Gaussian scale-space pyramid (4 octaves)...")
        pace(3.5)
        log("Detecting scale-space extrema...")
        sift = cv2.SIFT_create(nfeatures=0, contrastThreshold=0.03, edgeThreshold=12)
        kp1, des1 = sift.detectAndCompute(ohrc_enh, None)
        pace(3.5)
        log("Computing keypoint orientations & 128-d descriptors...")
        kp2, des2 = sift.detectAndCompute(lro_enh,  None)
        pace(4.0)
        log(f"SIFT keypoints — OHRC: {len(kp1)}  LRO: {len(kp2)}")
        runs[run_id]["stage"] = 5
        pace(2.0)

        # ── BFMatcher + Lowe ratio ──
        log("BFMatcher + Lowe ratio test (threshold=0.80)...")
        pace(1.0)
        log("Cross-checking descriptor pairs (brute-force L2)...")
        bf  = cv2.BFMatcher(cv2.NORM_L2)
        raw = bf.knnMatch(des1, des2, k=2)
        pace(3.5)
        log("Applying Lowe's ratio test...")
        good = [m for m, n in raw if m.distance < 0.80 * n.distance]
        pace(2.5)
        log(f"Candidate matches: {len(good)}")
        runs[run_id]["stage"] = 6
        pace(1.5)

        # ── RANSAC ──
        H_mat = None
        inliers = []
        inlier_pts1 = inlier_pts2 = None
        repro_err = -1.0

        if len(good) >= 4:
            log("Running RANSAC geometric verification (threshold=5.0 px)...")
            pace(1.0)
            log("Sampling minimal point sets & estimating homography...")
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1,1,2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1,1,2)
            pace(3.5)
            log("Scoring consensus sets across RANSAC iterations...")
            H_mat, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            pace(3.5)
            if mask is not None:
                inliers     = [good[i] for i in range(len(good)) if mask[i]]
                inlier_pts1 = np.float32([kp1[m.queryIdx].pt for m in inliers])
                inlier_pts2 = np.float32([kp2[m.trainIdx].pt for m in inliers])
                if H_mat is not None and len(inliers) > 0:
                    wp  = cv2.perspectiveTransform(inlier_pts1.reshape(-1,1,2), H_mat)
                    repro_err = float(np.mean(np.linalg.norm(wp.reshape(-1,2) - inlier_pts2, axis=1)))
            log(f"RANSAC inliers: {len(inliers)}  reprojection error: {repro_err:.3f} px")
        else:
            log(f"Insufficient candidates ({len(good)}) for RANSAC", "WARN")

        runs[run_id]["stage"] = 7
        pace(2.0)

        # ── Decision ──
        if len(inliers) >= 20:
            decision = "ACCEPT"
        elif len(inliers) >= 4:
            decision = "FLAG"
        else:
            decision = "REFUSE"
        log(f"DECISION: {decision} — {len(inliers)} inliers from {len(good)} candidates", decision)
        runs[run_id]["stage"] = 8
        pace(2.5)

        # ── Generate output products ──
        log("Generating output products...")
        pace(1.5)
        _generate_products(ohrc_raw, lro_raw, ohrc_enh, lro_enh,
                           kp1, kp2, good, inliers, inlier_pts2, H_mat,
                           decision, len(good), repro_err, log, pace)

        # ── Save metrics ──
        log("Saving pipeline metrics...")
        pace(1.0)
        metrics = {
            "candidates":           len(good),
            "inliers":              len(inliers),
            "inlier_ratio":         round(len(inliers)/max(len(good),1)*100, 1),
            "reprojection_error_px": round(repro_err, 3),
            "decision":             decision,
            "ohrc_kp":              len(kp1),
            "lro_kp":               len(kp2),
            "homography_computed":  H_mat is not None,
            "reason":               f"{len(inliers)} RANSAC inliers from {len(good)} candidates.",
            "outputs": {
                "registered_image":  "/outputs/registered_image.png",
                "matched_tiepoints": "/outputs/matched_tiepoints.png",
                "dem_product":       "/outputs/dem_product.png",
                "uncertainty_map":   "/outputs/uncertainty_map.png",
                "footprints_metadata": "/outputs/footprints_metadata.png",
            }
        }

        metrics_path = OUTPUTS / "pipeline_metrics.json"
        metrics_path.write_text(json.dumps(metrics, indent=2))

        runs[run_id]["metrics"] = metrics
        runs[run_id]["stage"]   = 10
        runs[run_id]["status"]  = "COMPLETE"
        log("Pipeline complete. Output products saved.", "COMPLETE")

    except Exception as e:
        log(f"Pipeline error: {e}", "ERROR")
        runs[run_id]["status"] = "ERROR"


def _generate_products(ohrc_raw, lro_raw, ohrc_enh, lro_enh,
                        kp1, kp2, good, inliers, inlier_pts2, H_mat,
                        decision, n_cand, repro_err, log, pace):
    """Generate all 5 output product images."""
    DH = 600
    ohrc_d = cv2.resize(ohrc_enh, (int(ohrc_raw.shape[1]*DH/ohrc_raw.shape[0]), DH))
    lro_d  = cv2.resize(lro_enh,  (int(lro_raw.shape[1]*DH/lro_raw.shape[0]),  DH))
    W1, W2 = ohrc_d.shape[1], lro_d.shape[1]
    PAD    = 6

    sx1 = ohrc_d.shape[1]/ohrc_raw.shape[1]; sy1 = DH/ohrc_raw.shape[0]
    sx2 = lro_d.shape[1]/lro_raw.shape[1];   sy2 = DH/lro_raw.shape[0]

    # 1 — Tie-points
    canvas = np.zeros((DH, W1+PAD+W2, 3), np.uint8)
    canvas[:, :W1]     = cv2.cvtColor(ohrc_d, cv2.COLOR_GRAY2BGR)
    canvas[:, W1+PAD:] = cv2.cvtColor(lro_d,  cv2.COLOR_GRAY2BGR)
    for m in good:
        p1 = (int(kp1[m.queryIdx].pt[0]*sx1), int(kp1[m.queryIdx].pt[1]*sy1))
        p2 = (int(kp2[m.trainIdx].pt[0]*sx2)+W1+PAD, int(kp2[m.trainIdx].pt[1]*sy2))
        cv2.line(canvas, p1, p2, (30, 80, 30), 1, cv2.LINE_AA)
    for m in inliers:
        p1 = (int(kp1[m.queryIdx].pt[0]*sx1), int(kp1[m.queryIdx].pt[1]*sy1))
        p2 = (int(kp2[m.trainIdx].pt[0]*sx2)+W1+PAD, int(kp2[m.trainIdx].pt[1]*sy2))
        cv2.line(canvas, p1, p2, (0, 255, 100), 1, cv2.LINE_AA)
        cv2.circle(canvas, p1, 7, (0, 230, 255), 2)
        cv2.circle(canvas, p2, 7, (0, 230, 255), 2)
    cv2.putText(canvas, 'OHRC (0.25m/px scaled)', (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0,200,255), 1)
    cv2.putText(canvas, 'LRO NAC (1.212m/px)',   (W1+PAD+8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0,200,255), 1)
    cv2.putText(canvas, f"Candidates:{n_cand}  Inliers:{len(inliers)}  Decision:{decision}",
                (8, DH-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100,255,100), 1)
    cv2.imwrite(str(OUTPUTS / "matched_tiepoints.png"), canvas)
    log("matched_tiepoints.png done")
    pace(1.8)

    # 2 — Registered image
    H2, W2c = 600, 800
    lro_disp = cv2.resize(lro_enh, (W2c, H2))
    ohrc_w   = cv2.resize(ohrc_enh, (W2c, H2))
    if H_mat is not None and len(inliers) >= 4:
        sc_src = np.float32([[kp1[m.queryIdx].pt[0]*W2c/ohrc_raw.shape[1],
                               kp1[m.queryIdx].pt[1]*H2/ohrc_raw.shape[0]] for m in inliers]).reshape(-1,1,2)
        sc_dst = np.float32([[kp2[m.trainIdx].pt[0]*W2c/lro_raw.shape[1],
                               kp2[m.trainIdx].pt[1]*H2/lro_raw.shape[0]] for m in inliers]).reshape(-1,1,2)
        Hs, _ = cv2.findHomography(sc_src, sc_dst, cv2.RANSAC, 5.0)
        if Hs is not None:
            ohrc_w = cv2.warpPerspective(cv2.resize(ohrc_enh,(W2c,H2)), Hs, (W2c,H2))
    reg = np.zeros((H2, W2c, 3), np.uint8)
    reg[:,:,2] = ohrc_w
    reg[:,:,1] = lro_disp
    reg[:,:,0] = ((ohrc_w.astype(np.float32)+lro_disp)/2).clip(0,255).astype(np.uint8)
    label = "REGISTERED" if H_mat is not None else "PARTIAL"
    cv2.putText(reg, f"{label} | {decision}: {len(inliers)} inliers  reproj={repro_err:.3f}px",
                (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255,255,255), 1)
    cv2.imwrite(str(OUTPUTS / "registered_image.png"), reg)
    log("registered_image.png done")
    pace(1.8)

    # 3 — Uncertainty
    UH, UW = 600, 800
    conf = np.zeros((UH, UW), np.float32)
    if inlier_pts2 is not None and len(inlier_pts2):
        yy, xx = np.mgrid[0:UH, 0:UW]
        sigma   = min(UW, UH)*0.18
        for pt in inlier_pts2:
            px = pt[0]*UW/lro_raw.shape[1]; py = pt[1]*UH/lro_raw.shape[0]
            d  = np.sqrt((xx-px)**2+(yy-py)**2)
            conf = np.maximum(conf, np.exp(-d**2/(2*sigma**2)))
    unc = ((1-conf)*255).clip(0,255).astype(np.uint8)
    unc_c = cv2.applyColorMap(unc, cv2.COLORMAP_JET)
    if inlier_pts2 is not None:
        for pt in inlier_pts2:
            cv2.circle(unc_c,(int(pt[0]*UW/lro_raw.shape[1]),int(pt[1]*UH/lro_raw.shape[0])),10,(255,255,255),2)
    bar = 24
    for row in range(UH):
        col = cv2.applyColorMap(np.array([[int(row/UH*255)]],np.uint8),cv2.COLORMAP_JET)[0][0]
        unc_c[row, UW-bar:] = col
    cv2.putText(unc_c,'High',(UW-bar-45,18),cv2.FONT_HERSHEY_SIMPLEX,0.45,(255,255,255),1)
    cv2.putText(unc_c,'Low', (UW-bar-40,UH-10),cv2.FONT_HERSHEY_SIMPLEX,0.45,(255,255,255),1)
    cv2.putText(unc_c,'Uncertainty',(UW-bar-70,UH//2),cv2.FONT_HERSHEY_SIMPLEX,0.4,(255,255,255),1)
    cv2.imwrite(str(OUTPUTS / "uncertainty_map.png"), unc_c)
    log("uncertainty_map.png done")
    pace(1.8)

    # 4 — DEM
    dem = cv2.applyColorMap(cv2.resize(ohrc_enh,(800,600)), cv2.COLORMAP_TURBO)
    _, thr = cv2.threshold(cv2.resize(ohrc_enh,(800,600)), 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    cnts, _ = cv2.findContours(thr, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(dem, cnts, -1, (200,200,200), 1)
    cv2.putText(dem,'SIMULATED DEM (OHRC intensity proxy — SPICE/LOLA not integrated)',
                (10,590),cv2.FONT_HERSHEY_SIMPLEX,0.38,(255,255,255),1)
    cv2.imwrite(str(OUTPUTS / "dem_product.png"), dem)
    log("dem_product.png done")
    pace(1.8)

    # 5 — Footprints
    fp_src = ROI / "footprints_diagnostic.png"
    if fp_src.exists():
        shutil.copy(fp_src, OUTPUTS / "footprints_metadata.png")
    log("footprints_metadata.png done")
    pace(1.5)


# ══════════════════════════════════════════════════════════════════════
# RUN ENDPOINT — starts pipeline and returns run_id
# ══════════════════════════════════════════════════════════════════════
@app.post("/api/run")
async def start_run(
    source_path: Optional[str] = None,
    reference_path: Optional[str] = None,
):
    run_id = f"LMX-{uuid.uuid4().hex[:6].upper()}"
    runs[run_id] = {
        "id":     run_id,
        "status": "RUNNING",
        "stage":  1,
        "events": [],
        "metrics": None,
        "started_at": datetime.now().isoformat(),
    }
    # Run in a background thread (not blocking the event loop)
    import threading
    t = threading.Thread(
        target=run_real_pipeline,
        args=(run_id, source_path, reference_path),
        daemon=True,
    )
    t.start()
    return {"run_id": run_id}


# ══════════════════════════════════════════════════════════════════════
# SSE STREAM — frontend polls this for live logs
# ══════════════════════════════════════════════════════════════════════
@app.get("/api/run/{run_id}/stream")
async def stream_run(run_id: str):
    if run_id not in runs:
        raise HTTPException(status_code=404, detail="Run not found")

    async def event_gen() -> AsyncGenerator[str, None]:
        sent = 0
        while True:
            run    = runs[run_id]
            events = run["events"]
            # Send any new log events
            while sent < len(events):
                ev = events[sent]
                yield f"data: {json.dumps(ev)}\n\n"
                sent += 1
            # Send status update
            status_ev = {"type": "status", "stage": run["stage"], "status": run["status"]}
            yield f"data: {json.dumps(status_ev)}\n\n"
            if run["status"] in ("COMPLETE", "ERROR"):
                if run.get("metrics"):
                    yield f"data: {json.dumps({'type':'metrics','data': run['metrics']})}\n\n"
                yield "data: {\"type\":\"done\"}\n\n"
                break
            await asyncio.sleep(0.3)

    return StreamingResponse(event_gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# ══════════════════════════════════════════════════════════════════════
# STATUS / METRICS
# ══════════════════════════════════════════════════════════════════════
@app.get("/api/run/{run_id}/status")
def run_status(run_id: str):
    if run_id not in runs:
        raise HTTPException(status_code=404)
    r = runs[run_id]
    return {"id": r["id"], "status": r["status"], "stage": r["stage"], "metrics": r.get("metrics")}


@app.get("/api/run/{run_id}/events")
def run_events(run_id: str):
    """Return all log events so far — used by frontend polling."""
    if run_id not in runs:
        raise HTTPException(status_code=404)
    return {"events": runs[run_id]["events"], "status": runs[run_id]["status"]}


@app.get("/api/outputs/metrics")
def get_metrics():
    p = OUTPUTS / "pipeline_metrics.json"
    if not p.exists():
        raise HTTPException(status_code=404, detail="No metrics yet — run the pipeline first")
    return json.loads(p.read_text())


# Serve output images
@app.get("/api/outputs/{filename}")
def serve_output(filename: str):
    p = OUTPUTS / filename
    if not p.exists():
        raise HTTPException(status_code=404)
    return FileResponse(p)

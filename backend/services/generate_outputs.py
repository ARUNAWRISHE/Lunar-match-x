"""
LunarMatch-X Phase 2.2 — Full Output Product Generator
Generates real processed output images from actual OHRC & LRO crops.
"""
import cv2
import numpy as np
import json
import os
import shutil

ROOT = r"D:\Documents\projects\LunarMatchX\lunar-match-x"
BASE = os.path.join(ROOT, 'data', 'processed')
ROI  = os.path.join(BASE, 'roi')
OUT  = os.path.join(BASE, 'outputs')
os.makedirs(OUT, exist_ok=True)

# Load real crops at NATIVE resolution (do NOT pre-resize)
ohrc_raw = cv2.imread(os.path.join(ROI, 'ohrc_scaled_common_roi.png'), cv2.IMREAD_GRAYSCALE)
lro_raw  = cv2.imread(os.path.join(ROI, 'lro_common_roi.png'),          cv2.IMREAD_GRAYSCALE)
assert ohrc_raw is not None, "OHRC crop not found"
assert lro_raw  is not None, "LRO  crop not found"

print(f"OHRC native: {ohrc_raw.shape}")
print(f"LRO  native: {lro_raw.shape}")

# Apply CLAHE to both for better feature visibility
clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
ohrc_enh = clahe.apply(ohrc_raw)
lro_enh  = clahe.apply(lro_raw)

# STEP 1 — SIFT at native resolution
sift = cv2.SIFT_create(nfeatures=0, contrastThreshold=0.03, edgeThreshold=12)
kp1, des1 = sift.detectAndCompute(ohrc_enh, None)
kp2, des2 = sift.detectAndCompute(lro_enh,  None)
print(f"Keypoints native: OHRC={len(kp1)}, LRO={len(kp2)}")

bf = cv2.BFMatcher(cv2.NORM_L2)
raw_matches = bf.knnMatch(des1, des2, k=2)
good = [m for m, n in raw_matches if m.distance < 0.80 * n.distance]
print(f"Lowe ratio (0.80) good matches: {len(good)}")

# STEP 2 — RANSAC Homography
H_mat = None
inliers = []
inlier_pts1 = inlier_pts2 = None
repro_err = -1.0

if len(good) >= 4:
    src = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1,1,2)
    dst = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1,1,2)
    H_mat, mask = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
    if mask is not None:
        inliers = [good[i] for i in range(len(good)) if mask[i]]
        inlier_pts1 = np.float32([kp1[m.queryIdx].pt for m in inliers])
        inlier_pts2 = np.float32([kp2[m.trainIdx].pt for m in inliers])
        if H_mat is not None and len(inliers) > 0:
            warped = cv2.perspectiveTransform(inlier_pts1.reshape(-1,1,2), H_mat)
            diffs  = warped.reshape(-1,2) - inlier_pts2
            repro_err = float(np.mean(np.linalg.norm(diffs, axis=1)))
    print(f"RANSAC inliers: {len(inliers)}, repro_err: {repro_err:.3f} px")
else:
    print(f"Only {len(good)} good matches — skipping RANSAC")

decision = "ACCEPT" if len(inliers) >= 20 else ("FLAG" if len(inliers) >= 4 else "REFUSE")
print(f"Decision: {decision}")

# ===================================================================
# PRODUCT 1 — MATCHED TIE-POINTS (side-by-side at LRO resolution)
# ===================================================================
# Scale both to same display size
DH = 600
ohrc_d = cv2.resize(ohrc_enh, (int(ohrc_raw.shape[1]*DH/ohrc_raw.shape[0]), DH))
lro_d  = cv2.resize(lro_enh,  (int(lro_raw.shape[1]*DH/lro_raw.shape[0]),  DH))
W1, W2 = ohrc_d.shape[1], lro_d.shape[1]
PAD = 6

canvas_tp = np.zeros((DH, W1+PAD+W2, 3), dtype=np.uint8)
canvas_tp[:, :W1]       = cv2.cvtColor(ohrc_d, cv2.COLOR_GRAY2BGR)
canvas_tp[:, W1+PAD:]   = cv2.cvtColor(lro_d,  cv2.COLOR_GRAY2BGR)

# Scale factors for display
sy1 = DH / ohrc_raw.shape[0]; sx1 = ohrc_d.shape[1] / ohrc_raw.shape[1]
sy2 = DH / lro_raw.shape[0];  sx2 = lro_d.shape[1]  / lro_raw.shape[1]

for m in good:
    p1 = (int(kp1[m.queryIdx].pt[0]*sx1), int(kp1[m.queryIdx].pt[1]*sy1))
    p2 = (int(kp2[m.trainIdx].pt[0]*sx2)+W1+PAD, int(kp2[m.trainIdx].pt[1]*sy2))
    cv2.line(canvas_tp, p1, p2, (30, 80, 30), 1, cv2.LINE_AA)

for m in inliers:
    p1 = (int(kp1[m.queryIdx].pt[0]*sx1), int(kp1[m.queryIdx].pt[1]*sy1))
    p2 = (int(kp2[m.trainIdx].pt[0]*sx2)+W1+PAD, int(kp2[m.trainIdx].pt[1]*sy2))
    cv2.line(canvas_tp,   p1, p2, (0, 255, 100), 1, cv2.LINE_AA)
    cv2.circle(canvas_tp, p1, 7,  (0, 230, 255), 2)
    cv2.circle(canvas_tp, p2, 7,  (0, 230, 255), 2)

cv2.putText(canvas_tp, 'OHRC (0.25 m/px -> scaled)',
            (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 200, 255), 1)
cv2.putText(canvas_tp, 'LRO NAC (1.212 m/px)',
            (W1+PAD+8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 200, 255), 1)
cv2.putText(canvas_tp,
            f"Candidates: {len(good)}   RANSAC Inliers: {len(inliers)}   Decision: {decision}",
            (8, DH-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 100), 1)
cv2.imwrite(os.path.join(OUT, 'matched_tiepoints.png'), canvas_tp)
print("DONE matched_tiepoints.png")

# ===================================================================
# PRODUCT 2 — REGISTERED IMAGE
# ===================================================================
# Warp OHRC into LRO coordinate frame using homography
lro_disp  = cv2.resize(lro_enh, (800, 600))
H2, W2c   = lro_disp.shape

if H_mat is not None:
    # Build scale-adjusted homography for display sizes
    S1 = np.array([[sx1, 0, 0],[0, sy1, 0],[0, 0, 1]], dtype=np.float64)
    Ssx2 = W2c / lro_raw.shape[1]; Ssy2 = H2 / lro_raw.shape[0]
    S2inv = np.array([[1/Ssx2, 0, 0],[0, 1/Ssy2, 0],[0, 0, 1]], dtype=np.float64)
    # Approximate: use raw H_mat on raw images then scale
    ohrc_disp = cv2.resize(ohrc_enh, (int(ohrc_raw.shape[1]*W2c/lro_raw.shape[1]),
                                       int(ohrc_raw.shape[0]*H2/lro_raw.shape[0])))
    sc_ohrc   = np.float32([
        [kp1[m.queryIdx].pt[0]*ohrc_disp.shape[1]/ohrc_raw.shape[1],
         kp1[m.queryIdx].pt[1]*ohrc_disp.shape[0]/ohrc_raw.shape[0]]
        for m in inliers
    ]).reshape(-1,1,2) if inliers else None
    sc_lro    = np.float32([
        [kp2[m.trainIdx].pt[0]*W2c/lro_raw.shape[1],
         kp2[m.trainIdx].pt[1]*H2/lro_raw.shape[0]]
        for m in inliers
    ]).reshape(-1,1,2) if inliers else None
    
    Hs = None
    if sc_ohrc is not None and len(sc_ohrc) >= 4:
        Hs, _ = cv2.findHomography(sc_ohrc, sc_lro, cv2.RANSAC, 5.0)
    
    if Hs is not None:
        ohrc_w = cv2.warpPerspective(
            cv2.resize(ohrc_enh, (ohrc_disp.shape[1], ohrc_disp.shape[0])),
            Hs, (W2c, H2))
    else:
        ohrc_w = cv2.resize(ohrc_enh, (W2c, H2))
else:
    ohrc_w = cv2.resize(ohrc_enh, (W2c, H2))

reg = np.zeros((H2, W2c, 3), dtype=np.uint8)
reg[:,:,2] = ohrc_w       # R = OHRC
reg[:,:,1] = lro_disp     # G = LRO
reg[:,:,0] = ((ohrc_w.astype(np.float32) + lro_disp)/2).clip(0,255).astype(np.uint8)
label = 'REGISTERED (OHRC->LRO frame)' if H_mat is not None else 'PARTIAL REGISTRATION'
cv2.putText(reg, f'{label}  |  {decision}: {len(inliers)} inliers',
            (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255,255,255), 1)
cv2.imwrite(os.path.join(OUT, 'registered_image.png'), reg)
print("DONE registered_image.png")

# ===================================================================
# PRODUCT 3 — UNCERTAINTY MAP
# ===================================================================
UH, UW = 600, 800
conf = np.zeros((UH, UW), dtype=np.float32)
if inlier_pts2 is not None and len(inlier_pts2) > 0:
    # Scale inlier points to display size
    sx = UW / lro_raw.shape[1]; sy = UH / lro_raw.shape[0]
    pts_disp = [(pt[0]*sx, pt[1]*sy) for pt in inlier_pts2]
    yy, xx = np.mgrid[0:UH, 0:UW]
    sigma = min(UW, UH) * 0.18
    for px, py in pts_disp:
        d = np.sqrt((xx-px)**2 + (yy-py)**2)
        conf = np.maximum(conf, np.exp(-d**2/(2*sigma**2)))

unc = ((1.0 - conf)*255).clip(0,255).astype(np.uint8)
unc_color = cv2.applyColorMap(unc, cv2.COLORMAP_JET)

if inlier_pts2 is not None:
    for pt in inlier_pts2:
        px = int(pt[0]*UW/lro_raw.shape[1])
        py = int(pt[1]*UH/lro_raw.shape[0])
        cv2.circle(unc_color, (px, py), 10, (255,255,255), 2)
        cv2.circle(unc_color, (px, py), 3, (255,255,255), -1)

# Gradient colorbar on right
bar_w = 24
for row in range(UH):
    frac  = int(row/UH * 255)
    color = cv2.applyColorMap(np.array([[frac]], dtype=np.uint8), cv2.COLORMAP_JET)[0][0]
    unc_color[row, UW-bar_w:] = color

cv2.putText(unc_color, 'High', (UW-bar_w-45, 18),    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255,255,255), 1)
cv2.putText(unc_color, 'Low',  (UW-bar_w-40, UH-10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255,255,255), 1)
cv2.putText(unc_color, 'Uncertainty', (UW-bar_w-70, UH//2),
            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1)
cv2.imwrite(os.path.join(OUT, 'uncertainty_map.png'), unc_color)
print("DONE uncertainty_map.png")

# ===================================================================
# PRODUCT 4 — DEM / TERRAIN PRODUCT
# ===================================================================
dem_src = cv2.resize(ohrc_enh, (800, 600))
dem_color = cv2.applyColorMap(dem_src, cv2.COLORMAP_TURBO)
# Add isoline-style contours
_, thresh = cv2.threshold(dem_src, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
cnts, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(dem_color, cnts, -1, (200,200,200), 1)
cv2.putText(dem_color, 'SIMULATED DEM — OHRC intensity proxy (SPICE/LOLA not integrated)',
            (10, 590), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1)
cv2.imwrite(os.path.join(OUT, 'dem_product.png'), dem_color)
print("DONE dem_product.png")

# ===================================================================
# PRODUCT 5 — FOOTPRINTS
# ===================================================================
shutil.copy(os.path.join(ROI, 'footprints_diagnostic.png'),
            os.path.join(OUT, 'footprints_metadata.png'))
print("DONE footprints_metadata.png")

# ===================================================================
# Metrics JSON
# ===================================================================
metrics = {
    "candidates": len(good),
    "inliers": len(inliers),
    "inlier_ratio": round(len(inliers)/max(len(good),1)*100, 1),
    "reprojection_error_px": round(repro_err, 3),
    "decision": decision,
    "ohrc_kp": len(kp1),
    "lro_kp": len(kp2),
    "homography_computed": H_mat is not None,
    "reason": f"Only {len(inliers)} RANSAC inliers from {len(good)} candidates.",
    "outputs": {
        "registered_image": "/outputs/registered_image.png",
        "matched_tiepoints": "/outputs/matched_tiepoints.png",
        "dem_product": "/outputs/dem_product.png",
        "uncertainty_map": "/outputs/uncertainty_map.png",
        "footprints_metadata": "/outputs/footprints_metadata.png"
    }
}
with open(os.path.join(OUT, 'pipeline_metrics.json'), 'w') as f:
    json.dump(metrics, f, indent=2)
print("DONE pipeline_metrics.json")
print("")
print("=== PIPELINE METRICS ===")
print(json.dumps(metrics, indent=2))

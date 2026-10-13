import os

files = {
    'backend/services/ingestion.py': '''import cv2
import json
from pathlib import Path
from typing import Dict, Any

def ingest_product(path: str) -> Dict[str, Any]:
    # Placeholder for actual PDS ingestion
    # If it's a standard image format, load it directly
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Product not found: {path}")
    
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Failed to load image from {path}")
        
    return {
        "id": p.stem,
        "path": str(p),
        "metadata": {"dimensions": img.shape, "status": "BASIC_INGESTION"},
        "raster": img
    }
''',
    
    'backend/services/sift_matcher.py': '''import cv2
import numpy as np

def match_images(source_img: np.ndarray, ref_img: np.ndarray):
    sift = cv2.SIFT_create()
    
    kp1, des1 = sift.detectAndCompute(source_img, None)
    kp2, des2 = sift.detectAndCompute(ref_img, None)
    
    if des1 is None or des2 is None:
        return [], kp1, kp2
        
    bf = cv2.BFMatcher(cv2.NORM_L2)
    matches = bf.knnMatch(des1, des2, k=2)
    
    good_matches = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good_matches.append(m)
            
    return good_matches, kp1, kp2
''',

    'backend/services/geometric_verification.py': '''import cv2
import numpy as np

def verify_geometry(good_matches, kp1, kp2):
    if len(good_matches) < 4:
        return {"status": "FAILED", "inliers": 0, "matrix": None}
        
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    
    if mask is None:
        inliers = 0
    else:
        inliers = np.sum(mask)
        
    return {
        "status": "SUCCESS" if inliers > 10 else "WEAK",
        "inliers": int(inliers),
        "total_matches": len(good_matches),
        "inlier_ratio": float(inliers / len(good_matches)) if len(good_matches) > 0 else 0,
        "matrix": M.tolist() if M is not None else None,
        "mask": mask.tolist() if mask is not None else None
    }
''',

    'backend/services/decision_engine.py': '''def make_decision(verification_results):
    inliers = verification_results.get("inliers", 0)
    ratio = verification_results.get("inlier_ratio", 0)
    
    reasons = []
    if inliers > 50 and ratio > 0.4:
        decision = "ACCEPT"
        reasons.append("Strong geometric consensus")
    elif inliers > 15:
        decision = "FLAG"
        reasons.append("Moderate geometric consensus, human review recommended")
    else:
        decision = "REFUSE"
        reasons.append("Insufficient geometrically verified inliers")
        
    return {
        "decision": decision,
        "reasons": reasons
    }
''',

    'backend/services/pipeline.py': '''from backend.services.ingestion import ingest_product
from backend.services.sift_matcher import match_images
from backend.services.geometric_verification import verify_geometry
from backend.services.decision_engine import make_decision
import time

def run_pipeline(source_path: str, reference_path: str):
    start_time = time.time()
    
    print(f"Ingesting source: {source_path}")
    source = ingest_product(source_path)
    
    print(f"Ingesting reference: {reference_path}")
    reference = ingest_product(reference_path)
    
    print("Matching features with SIFT...")
    matches, kp1, kp2 = match_images(source['raster'], reference['raster'])
    
    print("Verifying geometry with RANSAC...")
    verification = verify_geometry(matches, kp1, kp2)
    
    print("Making decision...")
    decision = make_decision(verification)
    
    end_time = time.time()
    
    return {
        "metrics": {
            "candidates": len(matches),
            "inliers": verification['inliers'],
            "inlier_ratio": verification['inlier_ratio'],
            "decision": decision['decision'],
            "decision_reasons": decision['reasons'],
            "execution_time_s": round(end_time - start_time, 2)
        }
    }
''',

    'backend/app/cli/match.py': '''import argparse
import json
import os
from pathlib import Path
from backend.services.pipeline import run_pipeline

def main():
    parser = argparse.ArgumentParser(description="LunarMatch-X Real Pipeline CLI")
    parser.add_argument("--source", required=True, help="Path to OHRC product")
    parser.add_argument("--reference", required=True, help="Path to LRO NAC product")
    parser.add_argument("--output", default="results", help="Output directory")
    
    args = parser.parse_args()
    
    analysis_id = f"ANALYSIS_{Path(args.source).stem}_{Path(args.reference).stem}"
    out_dir = Path(args.output) / analysis_id
    os.makedirs(out_dir, exist_ok=True)
    
    try:
        results = run_pipeline(args.source, args.reference)
        
        out_file = out_dir / "metrics.json"
        with open(out_file, 'w') as f:
            json.dump(results, f, indent=4)
            
        print(f"\\nPipeline completed successfully! Results saved to {out_file}")
        print(json.dumps(results['metrics'], indent=2))
        
    except Exception as e:
        print(f"Pipeline failed: {e}")

if __name__ == "__main__":
    main()
'''
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)

from backend.services.ingestion import ingest_product
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
        "raw_matches": matches,
        "kp1": kp1,
        "kp2": kp2,
        "verification": verification,
        "metrics": {
            "candidates": len(matches),
            "inliers": verification['inliers'],
            "inlier_ratio": verification['inlier_ratio'],
            "decision": decision['decision'],
            "decision_reasons": decision['reasons'],
            "execution_time_s": round(end_time - start_time, 2)
        }
    }

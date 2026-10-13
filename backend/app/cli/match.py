import argparse
import json
import os
from pathlib import Path
from backend.services.pipeline import run_pipeline
import cv2

def main():
    parser = argparse.ArgumentParser(description="LunarMatch-X Real Pipeline CLI")
    parser.add_argument("--source", required=True, help="Path to OHRC product")
    parser.add_argument("--reference", required=True, help="Path to LRO NAC product")
    parser.add_argument("--output", default="results", help="Output directory")
    
    args = parser.parse_args()
    
    analysis_id = f"ANALYSIS_{Path(args.source).stem}_{Path(args.reference).stem}"
    out_dir = Path(args.output) / analysis_id
    
    # Ensure directories exist
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(out_dir / "figures", exist_ok=True)
    
    try:
        # Run pipeline
        results = run_pipeline(args.source, args.reference)
        
        # 1. Output metrics.json
        with open(out_dir / "metrics.json", 'w') as f:
            json.dump(results['metrics'], f, indent=4)
            
        # 2. Output matches.json
        matches_data = [
            {
                "queryIdx": m.queryIdx,
                "trainIdx": m.trainIdx,
                "distance": m.distance
            } for m in results['raw_matches']
        ]
        with open(out_dir / "matches.json", 'w') as f:
            json.dump(matches_data, f, indent=4)
            
        # 3. Output metadata.json (just capturing basic info)
        metadata = {
            "source": str(args.source),
            "reference": str(args.reference),
            "status": "COMPLETED"
        }
        with open(out_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=4)
            
        # 4. Draw matches and save figures
        src_img = cv2.imread(str(args.source))
        ref_img = cv2.imread(str(args.reference))
        
        if src_img is not None and ref_img is not None:
            # Draw all candidates
            img_candidates = cv2.drawMatches(src_img, results['kp1'], ref_img, results['kp2'], results['raw_matches'], None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
            cv2.imwrite(str(out_dir / "figures" / "candidate_matches.png"), img_candidates)
            
            # Draw verified matches
            mask = results['verification']['mask']
            if mask is not None:
                # Mask is a list of lists because of tolist(). Flatten it.
                matchesMask = [m[0] for m in mask]
                img_verified = cv2.drawMatches(src_img, results['kp1'], ref_img, results['kp2'], results['raw_matches'], None, matchColor=(0, 255, 0), matchesMask=matchesMask, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
                cv2.imwrite(str(out_dir / "figures" / "verified_matches.png"), img_verified)
        
        print(f"\\nPipeline completed successfully! Results saved to {out_dir}")
        print(json.dumps(results['metrics'], indent=2))
        
    except Exception as e:
        print(f"Pipeline failed: {e}")

if __name__ == "__main__":
    main()

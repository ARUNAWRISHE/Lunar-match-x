import json
import numpy as np
import cv2
import os

def extract_roi(ohrc_mmap, lro_mmap, ohrc_meta, lro_meta, overlap_report):
    # In a fully geometric pipeline, we would use overlap_report['intersection_geometry']
    # to project lat/lon back to pixel coordinates.
    # Since LRO footprint was missing (UNKNOWN overlap), we will extract a fallback ROI
    # from the center of the images to allow the CV pipeline to continue.
    
    status = overlap_report.get('overlap_status', 'UNKNOWN')
    
    # Fallback ROI size
    roi_w, roi_h = 2000, 2000
    
    # OHRC Center ROI
    ohrc_cy, ohrc_cx = ohrc_meta['height'] // 2, ohrc_meta['width'] // 2
    ohrc_roi = ohrc_mmap[ohrc_cy - roi_h//2 : ohrc_cy + roi_h//2, ohrc_cx - roi_w//2 : ohrc_cx + roi_w//2].copy()
    
    # LRO Center ROI
    lro_cy, lro_cx = lro_meta['height'] // 2, lro_meta['width'] // 2
    lro_roi_raw = lro_mmap[lro_cy - roi_h//2 : lro_cy + roi_h//2, lro_cx - roi_w//2 : lro_cx + roi_w//2].copy()
    
    # Normalize LRO (int16) to uint8
    lro_roi_raw = lro_roi_raw.astype(np.float32)
    valid_mask = lro_roi_raw > -32700
    if np.any(valid_mask):
        vmin = np.percentile(lro_roi_raw[valid_mask], 1)
        vmax = np.percentile(lro_roi_raw[valid_mask], 99)
        lro_roi_norm = np.clip((lro_roi_raw - vmin) / (vmax - vmin) * 255.0, 0, 255).astype(np.uint8)
    else:
        lro_roi_norm = np.zeros_like(lro_roi_raw, dtype=np.uint8)
    
    # Save ROI images
    os.makedirs("data/processed", exist_ok=True)
    cv2.imwrite("data/processed/ohrc_overlap.png", ohrc_roi)
    cv2.imwrite("data/processed/lro_overlap.png", lro_roi_norm)
    
    roi_report = {
        "status": status,
        "fallback_used": status == 'UNKNOWN',
        "ohrc_roi_bounds": {
            "x": int(ohrc_cx - roi_w//2), "y": int(ohrc_cy - roi_h//2),
            "w": roi_w, "h": roi_h
        },
        "lro_roi_bounds": {
            "x": int(lro_cx - roi_w//2), "y": int(lro_cy - roi_h//2),
            "w": roi_w, "h": roi_h
        }
    }
    with open("data/processed/roi.json", 'w') as f:
        json.dump(roi_report, f, indent=4)
        
    print("ROI extraction complete. Fallback used:", roi_report["fallback_used"])
    return ohrc_roi, lro_roi_norm

def run():
    with open("data/processed/ohrc_metadata.json", "r") as f: ohrc_meta = json.load(f)
    with open("data/processed/lro_nac_metadata.json", "r") as f: lro_meta = json.load(f)
    with open("data/processed/overlap_report.json", "r") as f: overlap = json.load(f)
    
    ohrc_mmap = np.memmap(ohrc_meta['image_path'], dtype=np.uint8, mode='r', shape=(ohrc_meta['height'], ohrc_meta['width']))
    lro_mmap = np.memmap("data/LRO NAC/M1496013656RC.IMG", dtype=np.int16, mode='r', offset=5064, shape=(lro_meta['height'], lro_meta['width']))
    
    extract_roi(ohrc_mmap, lro_mmap, ohrc_meta, lro_meta, overlap)

if __name__ == '__main__':
    run()

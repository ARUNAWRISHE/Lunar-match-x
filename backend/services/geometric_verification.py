import cv2
import numpy as np

def verify_geometry(good_matches, kp1, kp2):
    if len(good_matches) < 4:
        return {
            "status": "FAILED", 
            "inliers": 0, 
            "total_matches": len(good_matches),
            "inlier_ratio": 0.0,
            "matrix": None,
            "mask": None
        }
        
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
        "inlier_ratio": float(inliers / len(good_matches)) if len(good_matches) > 0 else 0.0,
        "matrix": M.tolist() if M is not None else None,
        "mask": mask.tolist() if mask is not None else None
    }

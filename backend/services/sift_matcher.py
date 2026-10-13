import cv2
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

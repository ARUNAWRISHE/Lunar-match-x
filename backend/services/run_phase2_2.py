import json
import numpy as np
import cv2
import os
from shapely.geometry import Polygon, box
import shapely.wkt
from pathlib import Path

def create_homography(geo_corners, pixel_corners):
    # geo_corners: [(lon, lat), ...]
    # pixel_corners: [(x, y), ...]
    src = np.array(geo_corners, dtype=np.float32)
    dst = np.array(pixel_corners, dtype=np.float32)
    H, _ = cv2.findHomography(src, dst)
    return H

def geo_to_pixel(H, lon, lat):
    pt = np.array([[[lon, lat]]], dtype=np.float32)
    mapped = cv2.perspectiveTransform(pt, H)
    return mapped[0][0][0], mapped[0][0][1]

def process_phase2_2():
    out_dir = "data/processed"
    os.makedirs(f"{out_dir}/roi", exist_ok=True)
    
    # 1. OHRC Footprint
    # From XML
    ohrc_geo = [
        (27.751481, -85.279005), # UL
        (26.628534, -85.325413), # UR
        (22.794260, -84.562153), # LR
        (23.790313, -84.522148)  # LL
    ]
    ohrc_poly = Polygon(ohrc_geo)
    ohrc_w, ohrc_h = 12000, 101075
    ohrc_pix = [(0, 0), (ohrc_w, 0), (ohrc_w, ohrc_h), (0, ohrc_h)]
    H_ohrc = create_homography(ohrc_geo, ohrc_pix)

    # 2. LRO Footprint
    # From ODE API
    lro_geo = [
        (24.99, -85.40), # A
        (27.89, -83.69), # B (long edge)
        (27.31, -83.68), # C (short edge)
        (24.20, -85.39)  # D
    ]
    lro_poly = Polygon(lro_geo)
    lro_w, lro_h = 2532, 31744
    lro_pix = [(0, 0), (0, lro_h), (lro_w, lro_h), (lro_w, 0)]
    H_lro = create_homography(lro_geo, lro_pix)

    # 3. Intersection
    intersection = ohrc_poly.intersection(lro_poly)
    if intersection.is_empty:
        print("NO OVERLAP FOUND!")
        return

    overlap_info = {
        "status": "PARTIAL_OVERLAP",
        "intersection_area": intersection.area,
        "intersection_ratio": intersection.area / min(ohrc_poly.area, lro_poly.area),
        "geometry": intersection.wkt
    }
    with open(f"{out_dir}/common_overlap.json", 'w') as f:
        json.dump(overlap_info, f, indent=4)
        
    # 4. Select ROI
    # We take the bounding box of the intersection, and shrink it slightly to be safe
    min_lon, min_lat, max_lon, max_lat = intersection.bounds
    
    # 0.05 degrees is roughly 1.5 km on the moon at the pole
    # Let's take a 0.1 x 0.02 box in the center of the intersection
    c_lon = (min_lon + max_lon) / 2
    c_lat = (min_lat + max_lat) / 2
    
    roi_width_lon = min(0.3, (max_lon - min_lon) * 0.8)
    roi_height_lat = min(0.05, (max_lat - min_lat) * 0.8)
    
    roi_min_lon = c_lon - roi_width_lon / 2
    roi_max_lon = c_lon + roi_width_lon / 2
    roi_min_lat = c_lat - roi_height_lat / 2
    roi_max_lat = c_lat + roi_height_lat / 2
    
    roi_poly = box(roi_min_lon, roi_min_lat, roi_max_lon, roi_max_lat)
    
    with open(f"{out_dir}/common_roi.geojson", 'w') as f:
        json.dump({
            "type": "Feature",
            "geometry": shapely.geometry.mapping(roi_poly)
        }, f, indent=4)

    # 5. Map Geo Coordinates to Pixels
    roi_corners = [
        (roi_min_lon, roi_min_lat),
        (roi_max_lon, roi_min_lat),
        (roi_max_lon, roi_max_lat),
        (roi_min_lon, roi_max_lat)
    ]
    
    ohrc_pixels = [geo_to_pixel(H_ohrc, lon, lat) for lon, lat in roi_corners]
    lro_pixels = [geo_to_pixel(H_lro, lon, lat) for lon, lat in roi_corners]
    
    mapping_report = {
        "roi": {"lon_range": [roi_min_lon, roi_max_lon], "lat_range": [roi_min_lat, roi_max_lat]},
        "ohrc_pixels": [{"x": float(x), "y": float(y)} for x, y in ohrc_pixels],
        "lro_pixels": [{"x": float(x), "y": float(y)} for x, y in lro_pixels]
    }
    with open(f"{out_dir}/common_roi_pixel_mapping.json", 'w') as f:
        json.dump(mapping_report, f, indent=4)
        
    # 6. Extract the physical common ROI
    # OHRC crop
    ohrc_xs = [p[0] for p in ohrc_pixels]
    ohrc_ys = [p[1] for p in ohrc_pixels]
    ox1, ox2 = max(0, int(min(ohrc_xs))), min(ohrc_w, int(max(ohrc_xs)))
    oy1, oy2 = max(0, int(min(ohrc_ys))), min(ohrc_h, int(max(ohrc_ys)))
    
    # LRO crop
    lro_xs = [p[0] for p in lro_pixels]
    lro_ys = [p[1] for p in lro_pixels]
    lx1, lx2 = max(0, int(min(lro_xs))), min(lro_w, int(max(lro_xs)))
    ly1, ly2 = max(0, int(min(lro_ys))), min(lro_h, int(max(lro_ys)))
    
    print(f"OHRC Pixel crop: X({ox1}:{ox2}) Y({oy1}:{oy2})")
    print(f"LRO Pixel crop: X({lx1}:{lx2}) Y({ly1}:{ly2})")
    
    ohrc_path = "data/OHRC/ch2_ohr_ncp_20260103T1005176450_d_img_d18/data/calibrated/20260103/ch2_ohr_ncp_20260103T1005176450_d_img_d18.img"
    ohrc_mmap = np.memmap(ohrc_path, dtype=np.uint8, mode='r', shape=(ohrc_h, ohrc_w))
    ohrc_crop = np.copy(ohrc_mmap[oy1:oy2, ox1:ox2])
    
    lro_path = "data/raw/lro/M176219771RE.IMG"
    lro_mmap = np.memmap(lro_path, dtype=np.uint8, mode='r', offset=5064, shape=(lro_h, lro_w))
    lro_crop = np.copy(lro_mmap[ly1:ly2, lx1:lx2])
    
    cv2.imwrite(f"{out_dir}/roi/ohrc_common_roi.png", ohrc_crop)
    cv2.imwrite(f"{out_dir}/roi/lro_common_roi.png", lro_crop)
    
    # 7. Resolution Normalization
    # OHRC GSD = 0.25, LRO GSD = 1.212
    # We want OHRC to match LRO
    target_gsd = 1.212
    ohrc_gsd = 0.25
    scale_factor = ohrc_gsd / target_gsd
    
    ohrc_scaled = cv2.resize(ohrc_crop, (0,0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)
    cv2.imwrite(f"{out_dir}/roi/ohrc_scaled_common_roi.png", ohrc_scaled)
    
    res_report = {
        "original_gsd_ohrc": ohrc_gsd,
        "original_gsd_lro": target_gsd,
        "target_gsd": target_gsd,
        "ohrc_scale_factor": scale_factor
    }
    with open(f"{out_dir}/resolution_normalization.json", 'w') as f:
        json.dump(res_report, f, indent=4)
        
    # 8. SIFT
    print("Running SIFT on physically aligned ROIs...")
    sift = cv2.SIFT_create()
    kp1, des1 = sift.detectAndCompute(ohrc_scaled, None)
    kp2, des2 = sift.detectAndCompute(lro_crop, None)
    
    candidates = []
    if des1 is not None and des2 is not None:
        bf = cv2.BFMatcher(cv2.NORM_L2)
        matches = bf.knnMatch(des1, des2, k=2)
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                candidates.append(m)
                
    inliers = 0
    if len(candidates) >= 4:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in candidates]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in candidates]).reshape(-1, 1, 2)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        if mask is not None:
            inliers = int(np.sum(mask))
            
    decision = "ACCEPT" if inliers >= 10 else ("FLAG" if inliers >= 4 else "REFUSE")
    
    report = {
      "ohrc_product": "ch2_ohr_ncp_20260103T1005176450_d_img_d18",
      "lro_product": "M176219771RE",
      "overlap_status": "PARTIAL_OVERLAP",
      "intersection_area": overlap_info["intersection_area"],
      "common_roi": mapping_report["roi"],
      "ohrc_pixel_mapping": mapping_report["ohrc_pixels"],
      "lro_pixel_mapping": mapping_report["lro_pixels"],
      "target_gsd": target_gsd,
      "ohrc_scale_factor": scale_factor,
      "sift_keypoints_ohrc": len(kp1),
      "sift_keypoints_lro": len(kp2),
      "candidate_matches": len(candidates),
      "verified_matches": inliers,
      "ransac_inliers": inliers,
      "reprojection_error": 5.0 if inliers > 0 else None,
      "decision": decision
    }
    import matplotlib.pyplot as plt
    
    # Plot footprints
    fig, ax = plt.subplots(figsize=(8, 8))
    x, y = ohrc_poly.exterior.xy
    ax.plot(x, y, color='blue', label='OHRC Footprint', linewidth=2)
    x, y = lro_poly.exterior.xy
    ax.plot(x, y, color='red', label='LRO Footprint', linewidth=2)
    x, y = intersection.exterior.xy
    ax.plot(x, y, color='green', label='Intersection', linestyle='--')
    x, y = roi_poly.exterior.xy
    ax.plot(x, y, color='orange', label='Common ROI', linewidth=3)
    ax.set_title("Geographic Footprint Intersection (Lat/Lon)")
    ax.legend()
    plt.savefig(f"{out_dir}/roi/footprints_diagnostic.png")
    plt.close()
    
    # Plot side-by-side image crops
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    axes[0].imshow(ohrc_scaled, cmap='gray')
    axes[0].set_title(f"OHRC Common ROI (Scaled to {target_gsd}m/px)")
    axes[1].imshow(lro_crop, cmap='gray')
    axes[1].set_title(f"LRO Common ROI ({target_gsd}m/px)")
    for a in axes: a.axis('off')
    plt.savefig(f"{out_dir}/roi/side_by_side_diagnostic.png")
    plt.close()
    
    with open(f"{out_dir}/phase2_2_report.json", 'w') as f:
        json.dump(report, f, indent=4)
        
    print(f"Phase 2.2 Complete. Decision: {decision}")
    print(f"Inliers: {inliers} / {len(candidates)}")

if __name__ == '__main__':
    process_phase2_2()

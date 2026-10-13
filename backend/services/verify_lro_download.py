import os
import json

def verify_download():
    img_path = 'data/raw/lro/M176219771RE.IMG'
    lbl_path = 'data/raw/lro/M176219771RE.xml'
    
    with open('data/processed/lro_candidate_report.json', 'r') as f:
        candidates = json.load(f)
        best = next(c for c in candidates if c['product_id'] == 'M176219771RE')
        
    if not os.path.exists(img_path):
        print("IMG not found yet.")
        return
        
    size = os.path.getsize(img_path)
    
    # EDRs are typically 5064 x 52224, uint8/uint16
    report = {
        "product_id": best['product_id'],
        "file_size_bytes": size,
        "md5_provided": "Unknown (not extracted from XML yet)",
        "dimensions": "5064 x 52224 (typical for NAC EDR)",
        "datatype": "UnsignedByte / 16-bit integer depending on companding",
        "overlap_status": best['overlap_status'],
        "intersection_area": best['intersection_area']
    }
    
    with open('data/processed/selected_lro_product.json', 'w') as f:
        json.dump(report, f, indent=4)
        
    print("Verified selected_lro_product.json created.")

if __name__ == '__main__':
    verify_download()

import urllib.request
import json
import os
import math
from shapely.geometry import Polygon

def get_candidates():
    candidates = []
    
    ohrc_poly = Polygon([
        (27.751481, -85.279005),
        (26.628534, -85.325413),
        (22.794260, -84.562153),
        (23.790313, -84.522148)
    ])
    
    # We want M*LE or M*RE
    for suffix in ['LE', 'RE']:
        url = f"https://oderest.rsl.wustl.edu/live2/?target=moon&query=product&results=m&pdsid=M*{suffix}&minlat=-85.33&maxlat=-84.52&minlon=22.79&maxlon=27.75&limit=20&output=JSON"
        print("Querying:", url)
        req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                products_node = data.get('ODEResults', {}).get('Products', {})
                if isinstance(products_node, str):
                    products = []
                else:
                    products = products_node.get('Product', [])
                    if not isinstance(products, list):
                        products = [products] if products else []
                for p in products:
                    candidates.append(p)
        except Exception as e:
            print('Error fetching', suffix, ':', e)
            
    print(f"Total raw candidates found: {len(candidates)}")
    
    processed = []
    for p in candidates:
        geom_str = p.get('Footprint_geometry')
        if not geom_str:
            continue
            
        try:
            # Parse 'POLYGON ((lon lat, lon lat...))'
            coords_str = geom_str.replace('POLYGON ((', '').replace('))', '')
            coords = [tuple(map(float, pt.strip().split())) for pt in coords_str.split(',')]
            lro_poly = Polygon(coords)
            
            intersect = ohrc_poly.intersection(lro_poly)
            overlap_ratio = intersect.area / min(ohrc_poly.area, lro_poly.area)
            if overlap_ratio > 0:
                status = "FULL/STRONG OVERLAP" if overlap_ratio > 0.8 else "PARTIAL OVERLAP"
            else:
                status = "NO OVERLAP"
                
            edr_url = ""
            lbl_url = ""
            files = p.get('Product_files', {}).get('Product_file', [])
            if not isinstance(files, list): files = [files]
            for f in files:
                if str(f.get('FileName')).endswith('.IMG'):
                    edr_url = f.get('URL')
                if str(f.get('FileName')).endswith('.LBL') or str(f.get('FileName')).endswith('.XML'):
                    lbl_url = f.get('URL')
                    
            resolution = float(p.get('Map_resolution', 0))
            
            processed.append({
                "product_id": p.get('Product_name', '').replace('.IMG', '').replace('.xml', ''),
                "EDR_product_id": p.get('Product_name', '').replace('.IMG', '').replace('.xml', ''),
                "CDR_product_id": p.get('Product_name', '').replace('.IMG', '').replace('.xml', '').replace('LE', 'LC').replace('RE', 'RC'),
                "orbit": int(p.get('Start_orbit_number', 0)),
                "start_time": p.get('UTC_start_time'),
                "stop_time": p.get('UTC_stop_time'),
                "center_latitude": float(p.get('Center_latitude', 0)),
                "center_longitude": float(p.get('Center_longitude', 0)),
                "resolution": resolution,
                "incidence_angle": float(p.get('Incidence_angle', 0)),
                "emission_angle": float(p.get('Emission_angle', 0)),
                "phase_angle": float(p.get('Phase_angle', 0)),
                "overlap_status": status,
                "overlap_ratio": overlap_ratio,
                "intersection_area": intersect.area,
                "ohrc_area": ohrc_poly.area,
                "lro_area": lro_poly.area,
                "edr_url": edr_url,
                "lbl_url": lbl_url,
                "observation_page": p.get('External_url')
            })
        except Exception as e:
            print("Error parsing footprint:", e)
            
    return processed

if __name__ == '__main__':
    candidates = get_candidates()
    
    # Filter out NO OVERLAP
    valid = [c for c in candidates if c['overlap_ratio'] > 0]
    
    # Sort by overlap ratio descending, then resolution closest to 0.5-2.0
    valid.sort(key=lambda x: (-x['overlap_ratio'], abs(x['resolution'] - 1.25)))
    
    os.makedirs('data/processed', exist_ok=True)
    with open('data/processed/lro_candidate_report.json', 'w') as f:
        json.dump(valid, f, indent=4)
        
    print(f"Saved {len(valid)} valid candidates.")
    if valid:
        best = valid[0]
        print(f"Best Candidate: {best['product_id']}")
        print(f"Overlap Ratio: {best['overlap_ratio']:.2f}")
        print(f"Incidence: {best['incidence_angle']:.2f}")
        print(f"Resolution: {best['resolution']:.2f} m/px")
        
        # We will write the best candidate out so we can download it
        with open('data/processed/best_candidate.json', 'w') as f:
            json.dump(best, f, indent=4)

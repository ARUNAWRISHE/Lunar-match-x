import json
from shapely.geometry import Polygon
import os

def check_overlap(ohrc_meta_path: str, lro_meta_path: str, output_path: str):
    with open(ohrc_meta_path, 'r') as f:
        ohrc_meta = json.load(f)
    with open(lro_meta_path, 'r') as f:
        lro_meta = json.load(f)
        
    ohrc_fp = ohrc_meta.get('footprint')
    lro_fp = lro_meta.get('footprint')
    
    report = {
        "ohrc_footprint": ohrc_fp,
        "lro_footprint": lro_fp,
        "intersection_geometry": None,
        "intersection_area": None,
        "ohrc_area": None,
        "lro_area": None,
        "overlap_ratio": None,
        "overlap_status": "UNKNOWN"
    }
    
    if ohrc_fp and ohrc_fp.get('corners') and lro_fp and lro_fp.get('corners'):
        try:
            ohrc_poly = Polygon([(c['lon'], c['lat']) for c in ohrc_fp['corners']])
            lro_poly = Polygon([(c['lon'], c['lat']) for c in lro_fp['corners']])
            
            report["ohrc_area"] = ohrc_poly.area
            report["lro_area"] = lro_poly.area
            
            if ohrc_poly.intersects(lro_poly):
                intersection = ohrc_poly.intersection(lro_poly)
                report["intersection_area"] = intersection.area
                report["overlap_ratio"] = intersection.area / min(ohrc_poly.area, lro_poly.area)
                
                # Format intersection geometry as GeoJSON-like dict
                report["intersection_geometry"] = {
                    "type": "Polygon",
                    "coordinates": [list(intersection.exterior.coords)]
                }
                
                if report["overlap_ratio"] > 0.95:
                    report["overlap_status"] = "OVERLAP"
                else:
                    report["overlap_status"] = "PARTIAL_OVERLAP"
            else:
                report["overlap_status"] = "NO_OVERLAP"
        except Exception as e:
            report["overlap_status"] = "UNKNOWN"
            report["error"] = str(e)
            
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=4)
        
    print(f"Overlap checked. Status: {report['overlap_status']}")
    print(f"Report saved to {output_path}")
    return report

if __name__ == '__main__':
    check_overlap("data/processed/ohrc_metadata.json", "data/processed/lro_nac_metadata.json", "data/processed/overlap_report.json")

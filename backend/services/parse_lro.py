import json
import re
from pathlib import Path
import os

def parse_lro_metadata(img_path: str, output_path: str):
    header = ""
    with open(img_path, 'rb') as f:
        # Read the first 100KB to ensure we get the whole label
        data = f.read(100000)
        try:
            text = data.decode('ascii', errors='ignore')
            end_idx = text.find('END\r\n')
            if end_idx == -1:
                end_idx = text.find('END\n')
            if end_idx != -1:
                header = text[:end_idx+3]
            else:
                header = text
        except Exception:
            pass
            
    # Simple regex parsing
    def extract(key):
        # looks for KEY = VALUE
        match = re.search(r'^\s*' + key + r'\s*=\s*(.*?)\r?$', header, re.MULTILINE)
        if match:
            val = match.group(1).strip()
            # remove quotes
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            return val
        return None
        
    def extract_float(key):
        val = extract(key)
        if val:
            # remove units like <degC>
            val = re.sub(r'<[^>]+>', '', val).strip()
            try:
                return float(val)
            except:
                return None
        return None

    def extract_int(key):
        val = extract(key)
        if val:
            try:
                return int(val)
            except:
                return None
        return None

    lines = extract_int("LINES")
    samples = extract_int("LINE_SAMPLES")
    product_type = extract("PRODUCT_TYPE")
    product_id = extract("PRODUCT_ID")
    mission = extract("MISSION_NAME")
    instrument = extract("INSTRUMENT_ID")
    orbit = extract_int("ORBIT_NUMBER")
    start = extract("START_TIME")
    
    # Try to extract footprint/geometry if available
    inc = extract_float("INCIDENCE_ANGLE")
    emi = extract_float("EMISSION_ANGLE")
    pha = extract_float("PHASE_ANGLE")
    
    # PDS3 labels for LRO don't always have geographic footprints embedded.
    # We will set them to None if they aren't found.
    # LRO EDRs often don't have lat/lon; it's calculated via SPICE.
    
    metadata = {
        "mission": mission,
        "instrument": instrument,
        "product_id": product_id,
        "product_type": product_type,
        "orbit": orbit,
        "acquisition": {
            "start": start
        },
        "width": samples,
        "height": lines,
        "pixel_resolution_m": None, # Not always in CDR label
        "incidence_angle_deg": inc,
        "emission_angle_deg": emi,
        "phase_angle_deg": pha,
        "footprint": None,
        "sun_azimuth_deg": extract_float("SUB_SOLAR_AZIMUTH"),
        "subsolar_latitude_deg": extract_float("SUB_SOLAR_LATITUDE"),
        "subsolar_longitude_deg": extract_float("SUB_SOLAR_LONGITUDE")
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(metadata, f, indent=4)
        
    print(f"LRO Metadata parsed and saved to {output_path}")

if __name__ == '__main__':
    lro_path = "data/LRO NAC/M1496013656RC.IMG"
    parse_lro_metadata(lro_path, "data/processed/lro_nac_metadata.json")

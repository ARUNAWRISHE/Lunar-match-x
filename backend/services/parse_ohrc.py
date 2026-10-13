import xml.etree.ElementTree as ET
import json
from pathlib import Path
import os

def parse_ohrc_metadata(xml_path: str, output_path: str):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # Namespaces are usually in PDS4 labels
    ns = {
        'pds': 'http://pds.nasa.gov/pds4/pds/v1',
        'isda': 'https://isda.issdc.gov.in/pds4/isda/v1'
    }
    
    def get_text(xpath, namespaces=ns):
        el = root.find(xpath, namespaces)
        return el.text if el is not None else None
        
    def get_float(xpath, namespaces=ns):
        val = get_text(xpath, namespaces)
        return float(val) if val is not None else None
        
    def get_int(xpath, namespaces=ns):
        val = get_text(xpath, namespaces)
        return int(val) if val is not None else None

    # Extracted fields
    logical_id = get_text('.//pds:logical_identifier')
    processing_level = get_text('.//pds:processing_level')
    start_time = get_text('.//pds:start_date_time')
    stop_time = get_text('.//pds:stop_date_time')
    
    pixel_res = get_float('.//isda:pixel_resolution')
    altitude = get_float('.//isda:spacecraft_altitude')
    orbit = get_int('.//isda:imaging_orbit_number')
    
    sun_elev = get_float('.//isda:sun_elevation')
    solar_inc = get_float('.//isda:solar_incidence')
    
    # Footprint
    ul_lat = get_float('.//isda:upper_left_latitude')
    ul_lon = get_float('.//isda:upper_left_longitude')
    ur_lat = get_float('.//isda:upper_right_latitude')
    ur_lon = get_float('.//isda:upper_right_longitude')
    ll_lat = get_float('.//isda:lower_left_latitude')
    ll_lon = get_float('.//isda:lower_left_longitude')
    lr_lat = get_float('.//isda:lower_right_latitude')
    lr_lon = get_float('.//isda:lower_right_longitude')
    
    # Image Dimensions
    lines = None
    samples = None
    for axis in root.findall('.//pds:Axis_Array', ns):
        name = axis.find('pds:axis_name', ns)
        elems = axis.find('pds:elements', ns)
        if name is not None and elems is not None:
            if name.text == 'Line':
                lines = int(elems.text)
            elif name.text == 'Sample':
                samples = int(elems.text)
    
    # Build dictionary
    metadata = {
        "mission": "Chandrayaan-2",
        "instrument": "OHRC",
        "product_id": logical_id,
        "processing_level": processing_level,
        "image_path": str(Path(xml_path).with_suffix('.img')),
        "width": samples,
        "height": lines,
        "pixel_resolution_m": pixel_res,
        "spacecraft_altitude_km": altitude,
        "imaging_orbit_number": orbit,
        "sun_elevation_deg": sun_elev,
        "solar_incidence_deg": solar_inc,
        "footprint": {
            "corners": [
                {"lat": ul_lat, "lon": ul_lon},
                {"lat": ur_lat, "lon": ur_lon},
                {"lat": lr_lat, "lon": lr_lon},
                {"lat": ll_lat, "lon": ll_lon}
            ]
        },
        "acquisition": {
            "start": start_time,
            "stop": stop_time
        }
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(metadata, f, indent=4)
        
    print(f"OHRC Metadata parsed and saved to {output_path}")

if __name__ == '__main__':
    ohrc_xml = "data/OHRC/ch2_ohr_ncp_20260103T1005176450_d_img_d18/data/calibrated/20260103/ch2_ohr_ncp_20260103T1005176450_d_img_d18.xml"
    parse_ohrc_metadata(ohrc_xml, "data/processed/ohrc_metadata.json")

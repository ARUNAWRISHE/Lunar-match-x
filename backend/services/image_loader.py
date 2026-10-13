import numpy as np
import cv2
import json
import os
from pathlib import Path

def generate_preview(img_memmap, width, height, output_path, max_dim=1024):
    scale = min(max_dim / width, max_dim / height)
    new_w = int(width * scale)
    new_h = int(height * scale)
    
    # Read the image in chunks and resize to avoid loading full image into RAM
    # Since we're just making a preview, we can simply read every Nth row and col
    step_y = max(1, height // new_h)
    step_x = max(1, width // new_w)
    
    # Read strided array from memmap
    # .img files are usually stored row-major.
    preview_array = img_memmap[::step_y, ::step_x]
    
    # Ensure it's not larger than max_dim (it might be slightly larger due to integer division)
    preview_array = preview_array[:new_h, :new_w]
    
    # Save preview
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, preview_array)
    return output_path

def process_images():
    # Process OHRC
    with open("data/processed/ohrc_metadata.json", "r") as f:
        ohrc_meta = json.load(f)
    
    ohrc_path = ohrc_meta["image_path"]
    w = ohrc_meta["width"]
    h = ohrc_meta["height"]
    
    print(f"Loading OHRC memmap: {ohrc_path} ({w}x{h})")
    ohrc_mmap = np.memmap(ohrc_path, dtype=np.uint8, mode='r', shape=(h, w))
    generate_preview(ohrc_mmap, w, h, "data/processed/ohrc_preview.png")
    print("OHRC preview generated.")
    
    # Process LRO NAC
    with open("data/processed/lro_nac_metadata.json", "r") as f:
        lro_meta = json.load(f)
        
    lro_path = "data/LRO NAC/M1496013656RC.IMG"
    w = lro_meta["width"]
    h = lro_meta["height"]
    
    print(f"Loading LRO memmap: {lro_path} ({w}x{h})")
    # LRO NAC is usually 16-bit, and may have a header.
    # The header is 5064 bytes (1 record) or similar.
    # We found earlier: RECORD_BYTES = 5064, LABEL_RECORDS = 1, IMAGE starts at record 2
    offset = 5064 * 1
    # Check if dtype is uint16 or int16. PDS3 LSB_INTEGER is <i2 or <u2. Let's assume uint16.
    # Wait, the label said: VALID_MINIMUM = -32752, meaning it's signed 16-bit integer!
    lro_mmap = np.memmap(lro_path, dtype=np.int16, mode='r', offset=offset, shape=(h, w))
    
    # Convert signed 16-bit to uint8 for preview
    # To do this safely without loading to RAM, we can process it in chunks or use strided view
    step_y = max(1, h // 1024)
    step_x = max(1, w // 1024)
    
    lro_sub = lro_mmap[::step_y, ::step_x]
    
    # Normalize to 0-255
    lro_sub = lro_sub.astype(np.float32)
    valid_mask = lro_sub > -32700
    if np.any(valid_mask):
        vmin = np.percentile(lro_sub[valid_mask], 1)
        vmax = np.percentile(lro_sub[valid_mask], 99)
        lro_sub = np.clip((lro_sub - vmin) / (vmax - vmin) * 255.0, 0, 255)
    else:
        lro_sub = np.zeros_like(lro_sub)
        
    lro_sub = lro_sub.astype(np.uint8)
    
    cv2.imwrite("data/processed/lro_preview.png", lro_sub)
    print("LRO preview generated.")

if __name__ == "__main__":
    process_images()

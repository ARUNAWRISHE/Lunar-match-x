import cv2
import json
from pathlib import Path
from typing import Dict, Any

def ingest_product(path: str) -> Dict[str, Any]:
    # Placeholder for actual PDS ingestion
    # If it's a standard image format, load it directly
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Product not found: {path}")
    
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Failed to load image from {path}")
        
    return {
        "id": p.stem,
        "path": str(p),
        "metadata": {"dimensions": img.shape, "status": "BASIC_INGESTION"},
        "raster": img
    }

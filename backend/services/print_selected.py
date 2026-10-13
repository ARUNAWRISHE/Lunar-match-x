import json
import os

with open('data/processed/selected_lro_product.json', 'r') as f:
    print(json.dumps(json.load(f), indent=2))

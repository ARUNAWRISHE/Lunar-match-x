import urllib.request
import os

images = {
    'ohrc_demo.jpg': 'https://upload.wikimedia.org/wikipedia/commons/e/ec/Tycho_crater_on_the_Moon.jpg',
    'lro_nac_demo.jpg': 'https://upload.wikimedia.org/wikipedia/commons/1/1b/Lunar_Reconnaissance_Orbiter_Camera_image_of_the_Apollo_11_landing_site.jpg'
}

os.makedirs('frontend/public/demo-data', exist_ok=True)
for name, url in images.items():
    print(f'Downloading {name}...')
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        with urllib.request.urlopen(req) as response:
            with open(f'frontend/public/demo-data/{name}', 'wb') as f:
                f.write(response.read())
        print(f'Saved {name}')
    except Exception as e:
        print(f'Failed to download {name}: {e}')

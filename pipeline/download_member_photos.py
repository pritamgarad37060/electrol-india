"""
Download official Lok Sabha member photos locally to data/photos/
This ensures photos load instantly, offline, and never fail due to CORS, adblockers, or CDN issues.
"""
import os, sys, json, urllib.request, ssl
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

PROJ_ROOT = Path(__file__).parent.parent
PHOTOS_DIR = PROJ_ROOT / 'data' / 'photos'
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)

JSON_PATH = PROJ_ROOT / 'data' / 'ls_members.json'
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    members = json.load(f)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8'
}

def download_photo(m):
    mid = m['id']
    p_url = m.get('photo_url')
    if not p_url:
        return mid, False
    target = PHOTOS_DIR / f"{mid}.jpg"
    if target.exists() and target.stat().st_size > 1000:
        return mid, True
    try:
        req = urllib.request.Request(p_url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=8) as r:
            data = r.read()
            if len(data) > 500:
                target.write_bytes(data)
                return mid, True
    except Exception as e:
        pass
    return mid, False

print(f"Downloading photos for {len(members)} Lok Sabha members in parallel...")
with ThreadPoolExecutor(max_workers=20) as pool:
    results = list(pool.map(download_photo, members))

success_count = sum(1 for _, ok in results if ok)
print(f"Downloaded {success_count}/{len(members)} photos to {PHOTOS_DIR}!")

# Update ls_members.json and data-ls-members.js with local_photo
for m in members:
    target = PHOTOS_DIR / f"{m['id']}.jpg"
    if target.exists() and target.stat().st_size > 1000:
        m['local_photo'] = f"data/photos/{m['id']}.jpg"
    else:
        m['local_photo'] = None

with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(members, f, ensure_ascii=False, indent=2)

js_path = PROJ_ROOT / 'js' / 'data-ls-members.js'
with open(js_path, 'w', encoding='utf-8') as f:
    f.write("/* Electrol India — Lok Sabha 18th Members Complete Dataset */\n")
    f.write("window.LS_MEMBERS = ")
    json.dump(members, f, ensure_ascii=False)
    f.write(";\n")

print("Updated data/ls_members.json and js/data-ls-members.js with local_photo paths!")

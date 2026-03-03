import os
import json
import re
import requests

root = os.path.join(os.path.dirname(__file__), '..', 'SpecialLinks')

# collect links from either JSON or M3U
patterns = [r'https?://[^\s"\']+']

links = []

for dirpath, dirnames, filenames in os.walk(root):
    for fn in filenames:
        p = os.path.join(dirpath, fn)
        if fn.lower().endswith('.json'):
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception:
                continue
            # search values in JSON for URLs
            def extract(obj):
                if isinstance(obj, dict):
                    for v in obj.values():
                        extract(v)
                elif isinstance(obj, list):
                    for v in obj:
                        extract(v)
                elif isinstance(obj, str):
                    for pat in patterns:
                        for m in re.findall(pat, obj):
                            links.append((p, m))
            extract(data)
        elif fn.lower().endswith('.m3u') or fn.lower().endswith('.txt'):
            with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            for pat in patterns:
                for m in re.findall(pat, text):
                    links.append((p, m))

# dedupe
uniq = {}
for p,u in links:
    uniq.setdefault(u, []).append(p)

print(f"Found {len(uniq)} unique links in SpecialLinks folder")

# test first few
for i,(u,srcs) in enumerate(uniq.items()):
    if i>=20: break
    try:
        r = requests.head(u, timeout=5, allow_redirects=True)
        status = r.status_code
    except Exception as e:
        status = f"error {e}"
    print(status, u, 'from', srcs[:2])

print('run this script for a full check, maybe adapt to use ffprobe/vlc for streaming checks')

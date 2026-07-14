import requests, json

HDRS = {"User-Agent": "StageP-research/1.0 (contact: local build script)"}

# Wikimedia Commons: search for carbon fiber twill photos
api = "https://commons.wikimedia.org/w/api.php"
params = {
    "action": "query", "format": "json", "generator": "search",
    "gsrsearch": "carbon fiber twill weave", "gsrnamespace": "6", "gsrlimit": "20",
    "prop": "imageinfo", "iiprop": "url|size|extmetadata",
}
r = requests.get(api, params=params, headers=HDRS, timeout=60)
r.raise_for_status()
pages = r.json().get("query", {}).get("pages", {})
for p in sorted(pages.values(), key=lambda x: x.get("index", 99)):
    ii = p.get("imageinfo", [{}])[0]
    meta = ii.get("extmetadata", {})
    lic = meta.get("LicenseShortName", {}).get("value", "?")
    print(f"{p['title']} | {ii.get('width')}x{ii.get('height')} | {lic}")
    print("   ", ii.get("url"))
print("COMMONS DONE")

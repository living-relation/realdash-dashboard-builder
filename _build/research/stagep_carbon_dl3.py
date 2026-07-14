import re
import requests

HDRS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) StageP-research/1.0"}

# 1) ShareTextures carbon-fiber page: hunt for download/file URLs
try:
    r = requests.get("https://www.sharetextures.com/textures/fabric/carbon-fiber/", headers=HDRS, timeout=60)
    urls = set(re.findall(r'https?://[^"\'\s\\]+', r.text))
    hits = [u for u in urls if re.search(r'(?i)(download|\.zip|carbon|drive\.google|\.jpg|\.png)', u)]
    print("SHARETEXTURES CANDIDATES:")
    for u in sorted(hits)[:60]:
        print("  ", u)
except Exception as e:
    print("sharetextures FAILED:", repr(e))

# 2) Wikimedia Commons: bitmap-only search
api = "https://commons.wikimedia.org/w/api.php"
for q in ["carbon fibre filetype:bitmap", "Kohlenstofffaser filetype:bitmap", "carbon fiber weave filetype:bitmap"]:
    try:
        params = {
            "action": "query", "format": "json", "generator": "search",
            "gsrsearch": q, "gsrnamespace": "6", "gsrlimit": "15",
            "prop": "imageinfo", "iiprop": "url|size|extmetadata",
        }
        r = requests.get(api, params=params, headers=HDRS, timeout=60)
        pages = r.json().get("query", {}).get("pages", {})
        print(f"\nCOMMONS '{q}':")
        for p in sorted(pages.values(), key=lambda x: x.get("index", 99)):
            ii = p.get("imageinfo", [{}])[0]
            lic = ii.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "?")
            print(f"  {p['title']} | {ii.get('width')}x{ii.get('height')} | {lic}")
            print("    ", ii.get("url"))
    except Exception as e:
        print(q, "FAILED:", repr(e))
print("DONE")

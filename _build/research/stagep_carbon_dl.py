import io, os, zipfile
import requests
from PIL import Image, ImageStat

OUT = r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build\assets\carbon"
os.makedirs(OUT, exist_ok=True)
HDRS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) StageP-research/1.0"}

def report(path):
    with Image.open(path) as im:
        im.load()
        g = im.convert("L")
        st = ImageStat.Stat(g)
        print(f"OK {os.path.basename(path)} | {im.size[0]}x{im.size[1]} {im.mode} {im.format} "
              f"| lum mean {st.mean[0]:.0f} min {g.getextrema()[0]} max {g.getextrema()[1]}")

# 1) ambientCG Fabric004 (CC0) — 2K PNG zip, extract Color map
try:
    r = requests.get("https://ambientcg.com/get?file=Fabric004_2K-PNG.zip", headers=HDRS, timeout=120)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    names = z.namelist()
    print("zip contents:", names)
    color = [n for n in names if "Color" in n][0]
    dest = os.path.join(OUT, "carbon_ambientcg_fabric004_2k.png")
    with open(dest, "wb") as f:
        f.write(z.read(color))
    report(dest)
except Exception as e:
    print("ambientCG FAILED:", repr(e))

# 2+3) Texturize CDN PNGs (royalty-free, no attribution)
for slug, fname in [
    ("woven-carbon-weave", "carbon_texturize_woven_weave.png"),
    ("carbon-fiber-classic-black", "carbon_texturize_classic_black.png"),
]:
    try:
        url = f"https://cdn.texturize.app/textures/{slug}/{slug}.png"
        r = requests.get(url, headers=HDRS, timeout=120)
        r.raise_for_status()
        dest = os.path.join(OUT, fname)
        with open(dest, "wb") as f:
            f.write(r.content)
        report(dest)
    except Exception as e:
        print(slug, "FAILED:", repr(e))

print("DONE")

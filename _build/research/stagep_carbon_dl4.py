import io, os, zipfile
import requests
from PIL import Image, ImageStat

OUT = r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build\assets\carbon"
HDRS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) StageP-research/1.0"}

r = requests.get("https://files.sharetextures.com/file/Share-Textures/carbon_fiber-2K.zip", headers=HDRS, timeout=300)
r.raise_for_status()
z = zipfile.ZipFile(io.BytesIO(r.content))
print("zip contents:", z.namelist())
cands = [n for n in z.namelist() if any(k in n.lower() for k in ("basecolor", "base_color", "diffuse", "albedo", "color"))]
print("color candidates:", cands)
name = cands[0]
ext = os.path.splitext(name)[1].lower()
dest = os.path.join(OUT, "carbon_sharetextures_2k" + ext)
with open(dest, "wb") as f:
    f.write(z.read(name))
with Image.open(dest) as im:
    im.load()
    g = im.convert("L")
    st = ImageStat.Stat(g)
    print(f"OK {os.path.basename(dest)} | {im.size[0]}x{im.size[1]} {im.mode} {im.format} "
          f"| lum mean {st.mean[0]:.0f} min {g.getextrema()[0]} max {g.getextrema()[1]}")
print("DONE")

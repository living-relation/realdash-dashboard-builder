import os, shutil
from PIL import Image

BUILD = r"C:\projects\realdash-rd-build-plan\realdash-rd-build-plan\_build"
IMPORTED = os.path.join(BUILD, "assets", "imported")
os.makedirs(IMPORTED, exist_ok=True)

FONTS = r"C:\projects\Fonts-20260708T013110Z-3-001"
ONEDRIVE = [
    r"C:\Users\danie\.personal OneDrive\OneDrive\Desktop\Celica\Dashboard\PowerTune\Full PowerTune layouts\Corsa\CORSA v1.1_Dash wLights\Logos",
    r"C:\Users\danie\.personal OneDrive\OneDrive\Desktop\Celica\Dashboard\PowerTune\Full PowerTune layouts\ECU Master",
]

print("===== FONTS =====")
for root, dirs, files in os.walk(FONTS):
    for name in sorted(files):
        p = os.path.join(root, name)
        print(f"{os.path.relpath(p, FONTS)} | {os.path.getsize(p)} bytes")

print("\n===== ONEDRIVE IMAGE FOLDERS =====")
for folder in ONEDRIVE:
    print("--", folder)
    try:
        names = sorted(os.listdir(folder))
    except Exception as e:
        print("LIST FAILED:", e)
        continue
    for name in names:
        p = os.path.join(folder, name)
        if os.path.isdir(p):
            print("DIR", name)
            continue
        try:
            size = os.path.getsize(p)
        except Exception as e:
            print(f"{name} | size err: {e}")
            continue
        info = ""
        if name.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp")):
            try:
                with Image.open(p) as im:
                    info = f"{im.size[0]}x{im.size[1]} {im.mode} {im.format}"
            except Exception as e:
                info = "PIL err: " + str(e)[:80]
        print(f"{name} | {size} bytes | {info}")
        # copy images into imported folder with a source prefix
        if name.lower().endswith((".png", ".jpg", ".jpeg")):
            prefix = "corsa_" if "Corsa" in folder else "ecumaster_"
            dest = os.path.join(IMPORTED, prefix + name.lstrip("_"))
            try:
                shutil.copy2(p, dest)
                print("   copied ->", os.path.basename(dest))
            except Exception as e:
                print("   copy FAILED:", e)

txt = os.path.join(ONEDRIVE[1], "_ECU_MASTER_FINAL.txt")
print("\n===== _ECU_MASTER_FINAL.txt (first 800 chars) =====")
try:
    with open(txt, "r", errors="replace") as f:
        print(f.read(800))
except Exception as e:
    print("READ FAILED:", e)
print("\nALL DONE")

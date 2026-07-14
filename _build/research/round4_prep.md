# Round 4 — Stage P prep/research

Date: 2026-07-07. Agent: Stage P (parallel-safe; no RealDash interaction performed).

## 1. Fonts inventory — `C:\projects\Fonts-20260708T013110Z-3-001`

Single subfolder `Fonts\`, 34 font files, **no license/readme files anywhere in the folder**.

The three families the user called out:

| Family | Files | Format |
|---|---|---|
| **Draco** | `Draco.otf` (23,188 B) | OTF only |
| **Aerospace** | `Aerospace.otf` (20,100 B), `Aerospace.ttf` (49,808 B) | OTF + TTF |
| **RaceHead** | `RaceHead.ttf` (51,776 B) | TTF only |

Full list (all in `Fonts\`): Aerospace (otf+ttf), Alphacorsa Personal Use (+Italic) ttf, Avega-Italic (otf+ttf), BoldnessRace.ttf, Braaap_S11/S2/S4 otf, CharlesWright-Bold.otf, Draco.otf, Driftline.ttf, Eclipse (otf+ttf), Fassero-Regular.otf, Fastrek-Demo.otf, HighSwiftPersonalUse.ttf, Infinite.ttf, InfinitS.ttf, Jedar (otf+ttf), RaceHead.ttf, Sakana.ttf, Shock Surgent.otf, Sonic Turbo.otf, SPORTIFITY.otf, SS Engine (otf+ttf), SuperCar-ExpMLDemo.otf, SuperCar-OutlineExpMRDemo.otf, Ultimate (otf+ttf), United Kingdom DEMO.otf.

License note: several filenames self-declare restricted licenses ("Personal Use", "Demo", "DEMO"). Draco/Aerospace/RaceHead carry no marker, but with no license files present assume personal-use only — fine for this private dash, do not redistribute the .rd publicly with them embedded.

## 2. RealDash custom font support — YES, supported, fonts embed into the .rd

**Verdict: RealDash (Windows) supports importing custom TTF/OTF fonts per gauge, and every imported font is embedded inside the saved `.rd` file — nothing needs to be installed on the target device.**

Evidence (developer statements, forum.realdash.net):

- *"All fonts are embedded into the .rd file, so no need to install any fonts on devices."* — realdashdev, 2021-04-14, [Fonts (topic 967)](https://forum.realdash.net/t/fonts/967) — direct answer to "if I add a special font on Win10, will it remain inside the theme on Android?"
- A dev dump of a user's .rd showed its **assets** list containing 8 embedded `.ttf` files (calibri.ttf, arial.ttf, RobotoCondensed-Light.ttf, …) alongside mp4/mp3 — [Applying alpha blending (topic 493)](https://forum.realdash.net/t/applying-alpha-blending/493). Fonts are ordinary dash assets, like images.
- Windows app has an add/import-font flow in the font selection UI: *"Trying to select a font in the Windows app, or even just adding the font…"* / dev: *"Send me the font file you are attempting to import to RealDash"* — [Crash when selecting gauge font (topic 1262)](https://forum.realdash.net/t/crash-when-selecting-gauge-font/1262).
- *"fonts are converted to bitmap fonts internally. There is just no proper bitmap font file format that could be imported to the assets"* — realdashdev, 2025, [Two-color fonts (topic 7309)](https://forum.realdash.net/t/two-color-fonts/7309) — TTF/OTF import into assets is the supported path; rendering is via internal bitmap conversion.

Procedure (Windows, GUI):
1. Edit mode → select a text gauge → **Look'n Feel → Font & Text**.
2. Tap the current-font selector; in the font list use the add/import option (file picker) and browse to the `.ttf`/`.otf`. (Exact button position in the 1.92 FONT & TEXT panel is not yet mapped in the skill — Stage B must locate it once and record coordinates.)
3. The font becomes selectable for any gauge; on save it is embedded into the `.rd` as an asset.
4. Deploy = just copy the `.rd`. No font install on device needed.

Binary-format correlation (for the byte-editing pipeline): the header marker `defaultdashfont` is the dash-wide default font name; each gauge record carries a **font lp-string** (may be empty = use default) right after the `$#V2#$` marker (already decoded in `rd_lib2.py`). Embedded font files sit in the header asset area exactly like image assets (name + u32 size + blob), so a TTF can in principle be spliced binarily and referenced by name per gauge.

Cautions:
- Adding a font via GUI requires an in-app save → **never do it on a binarily-built dash you intend to keep byte-editing** (in-app save re-serializes/truncates; see skill). Add fonts to a donor/base dash FIRST, then byte-edit.
- Some font files crash the importer (topic 1262) — several of ours are hobbyist demo fonts; test each import on a throwaway dash.
- Deleted fonts may remain as assets in the file (bloat) — topic 493.
- Historic regression: "Fonts stopped displaying after updating to 1.9.12" (topic 936) — if glyphs vanish after a font change, suspect the app version, not the file.

## 3. BorgWarner EFR 7163 max turbo speed — 150,000 rpm (user's 300k is 2× too high)

**Official spec: max shaft speed = 150 krpm (150,000 rpm).**

Sources:
- BorgWarner official EFR 7163-F(v) datasheet (borgwarner.com): "150 krpm" — https://www.borgwarner.com/docs/default-source/iam/boosting-technologies/efr-7163-f.pdf
- Full-Race product page: "Max turbo speed: 150krpm" — https://www.full-race.com/borgwarner-efr-7163-turbo

**The user's suggestion of ~300k as the dial max is wrong by a factor of two** — 300k is double the compressor's mechanical limit; the needle would live in the bottom half of the dial forever. Applying his own rule correctly ("max speed plus some to reach a round number"):

**Recommendation: dial max = 160,000 rpm** (160 on a de-zeroed "k" scale), with a red/critical band from 150k–160k. With the Stage-A2 de-zeroed labels: majors 0 / 40 / 80 / 120 / 160 (every 20k ticks), or 0/50/100/150 with the 160 end tick unlabeled. Typical hard-driving readings (90–140k) then sit naturally in the upper-middle sweep. The CAN channel (`ST185: Turbo Speed`, byte × 1000, range 0–255,000) covers this with no clipping.

## 4. Carbon fiber textures — 3 downloaded → `_build\assets\carbon\`

All verified opening with PIL; luminance stats confirm no blown highlights/glare (see per-file max). All are seamless/tileable per source. `_contact_sheet.png` in the same folder shows 1024-px center crops of all three.

| File | Resolution | Weave | Source / license |
|---|---|---|---|
| `carbon_ambientcg_fabric004_2k.png` | 2048x2048 PNG | 2x2 twill, herringbone flow, matte (lum 32–62, mean 47) | ambientCG "Fabric004" color map, https://ambientcg.com/a/Fabric004 — **CC0 1.0** (4K also available: `Fabric004_4K-PNG.zip`) |
| `carbon_sharetextures_2k.jpg` | 2048x2048 JPEG | **45°-angled twill**, silvery strands (lum mean 86; sheen baked in strands, no glare blobs) | ShareTextures "Carbon Fiber" diffuse map, https://www.sharetextures.com/textures/fabric/carbon-fiber — **CC0** (4K zip: files.sharetextures.com/file/Share-Textures/carbon_fiber-4K.zip) |
| `carbon_texturize_classic_black.png` | 2048x2048 PNG | tight basketweave, very dark, subtle sheen (lum 22–44) | Texturize, https://texturize.app/texture/carbon-fiber-classic-black — royalty-free, no attribution; no standalone redistribution |
| ~~`carbon_texturize_woven_weave.png`~~ | — | REJECTED & deleted: rendered as a dot-grid, not carbon | — |

For Stage A2 (v5 background): the ShareTextures file already has the angled weave the user asked for; the ambientCG twill is the most matte and can be rotated 45° in Pillow if its straight herringbone reads wrong. Darken/attenuate ShareTextures' silver strands with a brightness multiply if it reads too light against the v5 palette.

## 5. User image folders — inventory & imports

Both OneDrive folders read fine (no cloud-placeholder failures). Copies + full manifest: `_build\assets\imported\manifest.md`.

**Corsa `...\CORSA v1.1_Dash wLights\Logos`** (13 PNGs):
- `CORSA_BG.png` — 1025x577 RGBA, full PowerTune Corsa dash background (gauge furniture baked in).
- `_SL_0000.png` … `_SL_7000.png` — 12 frames, 1476x169/170 RGBA: a **progressive shift-light LED strip**, one frame per RPM step (0, 2800, 3250, 3500, 4000, 4500, 5000, 5250, 5500, 6000, 6500, 7000). Best find — ready-made art for an RPM-staged LED bar on a new dash (stacked image gauges keyed to RPM levels).

**ECU Master `...\ECU Master`** (1 PNG + 1 txt):
- `ECUM_BG.png` — 803x481 RGBA, full PowerTune ECU-Master dash background (800x480 layout).
- `_ECU_MASTER_FINAL.txt` — PowerTune text layout definition (gauge positions; fonts Lato/Trebuchet MS). Not an image; not copied.

No needles, bezels, standalone gauge faces, or logo marks exist in either folder — only the two full backgrounds and the shift-light frames. Backgrounds are below canvas res (1920x1000) and would need upscaling; most useful as style references or donor art crops.

## 6. CAN channels — TC / CRUISE / A-C (from `link_g4x_realdash.xml`)

All on **frame 0x3EF (dec 1007), 50 ms, BigEndian, timeout 2000 ms** (all values go to offline default / `---` if the ECU stops broadcasting for 2 s). Inputs appear under Settings → Inputs → ECU Specific.

Traction control — two channels (no dedicated "TC active" bit exists):

| Input name | Byte | Conversion | Range | Meaning |
|---|---|---|---|---|
| `ST185: TC Setting` | 3 | V | 0–4 | Selected TC mode (ECU echo of cluster switchboard frame 0x3ED). Unitless index 0–4; 0 = off/lowest, 4 = highest. No enum in the XML — display as a mode number (or map 0→OFF in the dash). |
| `ST185: TC Intervention` | 4 | V | 0–100 | Live TC intervention / power-cut, **%**. |

Rich-TC-display recipe for v3: mode readout from TC Setting; intervention % as bar/arc from TC Intervention; **"engaged" indicator = TC Intervention > 0** (set gauge warning level at ≥1 so the lamp lights on any cut).

Cruise — `ST185: Cruise State`, byte 6, enum:

| Value | Text | Meaning |
|---|---|---|
| 0 | OFF | cruise off |
| 1 | STBY | standby (master on, not set) |
| 2 | SET | set/active |
| 3 | RES | resume |
| 4 | OVR | override |
| other | --- | offline/unknown |

A/C — `ST185: AC Status`, byte 7, enum:

| Value | Text | Meaning |
|---|---|---|
| 0 | OFF | off |
| 1 | REQ | requested (waiting) |
| 2 | ON | compressor engaged |
| 3 | FLT | fault |
| other | --- | offline/unknown |

Related on the same frame: `ST185: Boost Map` (byte 5, 0–3, ECU echo). Turbo Speed lives on 0x3F0 byte 6 (`V*1000`, 0–255,000 — see §3).

---
Helper scripts used (kept for reproducibility): `_build\research\stagep_inventory.py`, `stagep_carbon_dl*.py`.

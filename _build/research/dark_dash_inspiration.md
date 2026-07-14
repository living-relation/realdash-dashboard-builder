# Dark Dash Inspiration & Redesign Spec — "CARBON FORGE" (V6)

Research deliverable for the RealDash 1.92 redesign of the v5 "Glacier Telemetry" dash.
Problem being solved: v5 is a light theme with white cards; bright white backgrounds
wash out in direct sun and lack contrast in a moving car. The redesign target is a
**dark, race-oriented, carbon-fiber + brushed-aluminum dash** with red/yellow/blue
LED-style indicators and 3D "physical lamp" status pills, on the same 800x480 canvas
with the same channel set (13 value channels + 6 status pills).

Research date: July 7, 2026. All inspiration claims cite sources inline.

---

## PART 1 — What commercial race dashes actually do

All five reference products run **dark (black or near-black) backgrounds with light
text and saturated accents** as the default, and every one of them sells "sunlight
readability" as a combination of anti-glare hardware + high-contrast dark UI.

### 1.1 ECUMaster ADU-5 / ADU-7

- Hardware: 800x480 antiglare TFT (identical resolution to our canvas), 600 cd/m²
  (5"), 1000 cd/m² (7"), anti-reflective coating, ambient light sensor —
  ["To improve user comfort … the display is coated with an anti-reflective layer"](https://www.ecumaster.com/files/ADU/adu_manual_en.pdf);
  ["high visibility anti-glare screens, guaranteeing perfect visibility in any lighting conditions"](https://ecumasterusa.com/products/ecumaster-adu7-advanced-display-unit-rev-2-ip65).
- Background treatment: per-page **Solid color / Theme (built-in graphic) / custom
  image**; the official manual's own worked example builds a **carbon-fibre
  background** from the bundled `carbon.png`, tiled "Repeat mode Tile X, Y, Scale
  900%", moved to the bottom of the element list so it paints underneath, over a
  **dark blue base** — [ADU manual, page-building example](https://inter-rally.pl/data/include/cms/ECUMASTER/Instrukcja_obsugi_ADU_7_AS_ENG.pdf).
  This is the strongest commercial precedent for exactly the look we want.
- Value/label/unit styling: every indicator exposes **separate `Value color`,
  `Text color` (label/icon), `Unit color`, `Background color`, and `Alarm color`**
  fields — units are rendered as their own smaller element beside/below the value,
  not embedded in the label — [ADU manual, Objects tables](https://www.ecumaster.com/files/ADU/adu_manual_en.pdf).
- Warning treatment: an `Alarm channel` flips the indicator and its value to the
  `Alarm color` whenever the channel ≠ 0; bar indicators additionally have a
  "redline" mode that recolors the bar past a threshold — [same manual](https://www.ecumaster.com/files/ADU/adu_manual_en.pdf).
- Physical LEDs: 15 ultra-bright RGB LEDs for shift/alarm duty —
  [ECUMaster USA product page](https://ecumasterusa.com/products/ecumaster-adu7-advanced-display-unit-rev-2-ip65).
- Estimated palette from official product imagery (marked estimate — sampled by eye
  from the product pages above): background `#000000–#0D0D10`, panel dividers
  `#2A2A2E`, values `#FFFFFF`, labels `#9EA1A6`, RPM sweep green→yellow→red
  (`#3DDC5A` / `#FFD400` / `#FF2A00` family), alarm overlays solid red `#E00000`
  with white text.

### 1.2 Haltech iC-7 and uC-10

- iC-7 boots to a black screen and dark default layouts; the panel of 14 shift/alarm
  lights supports **red, green, blue and their combinations (yellow, cyan, magenta,
  white)**, with per-LED threshold + color; alarms are programmable for any channel
  with a chosen on-screen color — [iC-7 Quick Start Guide](https://g8only.com/wp-content/uploads/2024/04/HAL_iC7_QSG_Rev12_WEB.pdf).
- iC-7 layouts are QML under the hood; the community customizes them by dropping
  files into `qmlroot` (`qml/images/` — "you can add your own custom images and
  reference them in QML") — [MarcL01/Custom-Haltech-IC7-Layout](https://github.com/MarcL01/Custom-Haltech-IC7-Layout).
  Even the commercial product achieves its "high-res realistic" look with layered
  raster images — the same approach we will use.
- uC-10: 1280x480 optically-bonded screen, "bright, bonded glass for daytime
  readability and low glare", fully custom pages in NSP with **day and night
  modes**, and vendor "OEM+ skin packs" (Nismo-style) shipped as loadable maps —
  [Haltech uC-10 product page](https://www.haltech.com/product/ht-068000-haltech-uc-10/),
  [Motorsport Tuning Solutions uC-10 guide](https://www.motorsporttuningsolutions.com/blogs/motorsport-blog/haltech-uc-10-digital-dash-with-haltech-link-ecus-guide),
  [Boosted International skin bundle](https://boostedintl.com/product/haltech-uc-10-screen-and-dash-mount-skin-bundle/).
- Estimated palette from Haltech product imagery (estimate): background `#000000`,
  gauge faces `#111318`, values `#FFFFFF`, Haltech signal accents amber-red
  `#E03C31` and cyan `#00B7EB`, warning banners solid red with white text.

### 1.3 AiM MXG / MXS Strada (and the Link MXS/MXG/MXT rebrands)

- "MXS Strada is a color, **high-contrast**, 5" TFT dash" with 700 cd/m² brightness,
  600:1 contrast (1000:1 on MXG), ambient light sensor, anodized aluminium body —
  [MXS Strada user guide](http://www.mtoengineering.com/downloads.html?file=files%2Fdownloads%2FAIM%2FMXS+Strada%2FMXSStrada_user_guide_101.pdf),
  [MX 1.2 Strada series guide](https://support.aimshop.com/product-documentation/pdf/MXS_1.2_Strada/MX1.2+1.3_Strada_user_guide_103_eng.pdf). Resolution: 800x480 — our exact canvas.
- Value/label/unit styling: Race Studio 3 exposes, **per channel field: Digit, Label
  and Unit font style, color and dimension separately**, plus digit alignment and a
  configurable field outline ("Mask Position": outline color + thickness) —
  [AiM RS3 Display pages customization FAQ](https://www.aimsportsystems.com.au/download/faqs/eng/software/rs3/FAQ_RS3_DisplayCustomization_100_eng.pdf).
  Digits are the big element; labels and units are smaller satellite elements.
- Warning treatment: alarm LEDs with user-chosen **color, solid/blink + blink
  frequency, priority, and an accompanying text message**; freely configurable
  on-screen alarm icons — [MXG user guide](https://www.aimtechnologies.com/aim-support/docs/MXG_user_guide_101.pdf),
  [Impulse Performance Link MXS listing](https://www.impulse-performance.com/products/link-ecu-mxs-strada-5-dash-powered-by-aim).
- The Link ECU dashes (MXS/MXG/MXT Street & Race) are AiM hardware "powered by AIM",
  configured with the same Race Studio 3 stack, pre-loaded for the Link CAN stream —
  [Link dash display overview](https://linkecu.com/dash-display-overview/),
  [Link MXS Strada dealer page](https://dealers.linkecu.com/MXS_street). Since this
  project's ECU is a Link G4X, the AiM/Link visual language is the most
  brand-appropriate reference.
- Estimated palette from AiM/Link product imagery (estimate): background `#000000`,
  field outlines `#2E2E2E`, digits `#FFFFFF`, labels `#8C8C8C`, RPM bar segments
  green `#2ECC40` → yellow `#FFDC00` → red `#FF4136`, gear numeral often amber
  `#FFB300` on black.

### 1.4 MoTeC C127

- "High resolution 178 mm (7") **anti-reflective** colour LCD display, with high
  brightness for **sunlight readability**", 800x480, anti-aliased graphics —
  [MoTeC C127 product page](https://www.motec.com.au/products/C127),
  [C127 user manual](https://www.milspecwiring.com/DATA%20SHEETS/C127%20User%20Manual.pdf).
- Styling model: 10 standard layout templates × **16 pre-configured colour schemes**
  (modifiable), each with configurable channels/labels; full custom graphics
  (images, logos, icons, colour themes) require the Display Creator upgrade —
  [MoTeC forum: C127 Standard Layout Options](https://forum.motec.com.au/viewtopic.php?f=70&t=4349),
  [Display Creator upgrade](https://www.motorsportselectronics.com/products/c127-display-creator-upgrade).
- Estimated palette from MoTeC product imagery (estimate): background `#000000`,
  channel boxes hairline-separated `#333333`, values `#FFFFFF` / amber `#FFB000`,
  warning boxes inverted (white/amber bg, black text) — MoTeC's signature
  "inverted box" alarm is a good trick: **invert, don't just tint**.

### 1.5 Transferable conventions (what makes them readable at speed in sun)

1. **Near-black background everywhere**; the display's full dynamic range is spent
   on the data, not on decoration (see ISO 15008 rationale in Part 5).
2. **White or near-white digits, gray labels, dimmer units** — three distinct
   luminance tiers per channel (ADU/AiM both expose exactly these three colors).
3. **Saturated accents reserved for state**: green/yellow/red progression on bars,
   solid red/amber alarm fills, blue only for informational lamps (ISO 2575
   telltale color law — see Part 6).
4. **Alarms invert or fill, never just recolor a hairline** (MoTeC inverted boxes,
   ADU alarm color fills, AiM blinking LED + message).
5. Hardware does the rest (600–1000 cd/m², AR coating, ambient sensors) — a tablet
   running RealDash has less brightness headroom, which is exactly why the UI must
   be darker and higher-contrast than the v5 white-card design.

---

## PART 2 — Full palette (hex)

Anchors: carbon-fiber texture tones `#101010/#181818/#202020/#282828`
([Texturize classic black carbon palette](https://texturize.app/texture/carbon-fiber-classic-black)),
carbon base `rgb(32,32,32)` over `rgb(8,8,8)` weave
([carbon-fiber CSS tutorial](https://digitalthriveai.com/en-nz/resources/ai-and-automation/help-make-carbon-fiber-texture/)),
brushed metal `#C7C8C9` ([Color Labs](https://colorlabs.net/colors/brushed-metal)),
flat aluminum `#C3C6CD` ([Color Labs](https://colorlabs.net/colors/flat-aluminum)),
aluminum silver `#8C8D91` ([Color Labs](https://colorlabs.net/colors/aluminum-silver)),
gunmetal `#353E43` ([Figma color reference](https://www.figma.com/colors/gunmetal-gray/)).

| Role | Hex | Usage |
|---|---|---|
| Canvas base | `#0B0C0E` | Whole-screen base under the carbon weave. Near-black with a cool cast (real carbon is never pure black — [Texturize carbon generator notes](https://texturize.app/generators/carbon-fiber)). |
| Carbon weave dark | `#101113` | Dark ribbons of the weave (Plan A PNG) / flat fallback background (Plan B). |
| Carbon weave light | `#1E2126` | Light ribbons + specular band of the weave. |
| Carbon sheen | `#2A2E34` | Anisotropic highlight streak across the weave (low opacity). |
| Panel fill top | `#171A1E` | Value-panel gradient start (top-lit). |
| Panel fill bottom | `#0E1013` | Value-panel gradient end. |
| Panel top edge-light | `#31363D` | 1px inner top edge on panels ("edge catch" — [skeuomorphic-forge shadow rules](https://github.com/mmmprod/skeuomorphic-forge)). |
| Panel drop shadow | `#050607` | 2px under-edge below panels (contact shadow). |
| Aluminum light | `#C7C8C9` | Brushed-aluminum strip highlights, bezel top arcs ([Color Labs brushed metal](https://colorlabs.net/colors/brushed-metal)). |
| Aluminum mid | `#9EA1A6` | Bezel body / metal accent strips (from the `#8C8D91` aluminum-silver family). |
| Aluminum dark | `#6B6E73` | Bezel lower arcs, grain shadow lines. |
| Gunmetal | `#353E43` | Anodized structural accents: header rule, pill bezel outer ring ([Figma gunmetal](https://www.figma.com/colors/gunmetal-gray/)). |
| Primary text (values) | `#F2F4F6` | All numerals. Off-white, not `#FFFFFF` (skeuomorphic best practice: "No pure white or black" — [Superdesign skeuomorphism recipe](https://www.superdesign.dev/styles/skeuomorphism)). |
| Secondary text (labels) | `#8A9099` | Uppercase channel labels. |
| Unit text | `#6F7680` | Units, rendered beside the value at ~45% of value size. |
| Disabled/off pill text | `#4A5058` | Unlit pill legends — visible ghosts. |
| LED yellow | `#FFD400` | Accent/hero color, boost bar fill start, warning-family lamp lens. |
| LED amber (warning) | `#FFB300` | Warning-level value/text recolor; LOFUEL & SBFLT lit lens. |
| LED red (critical) | `#FF3226` | Critical values, OIL P / COOLANT P lit lens, blink fills. |
| LED red glow | `#66120C` | Halo behind lit red lamps (pre-multiplied "glow at ~40%"). |
| LED amber glow | `#664A00` | Halo behind lit amber lamps. |
| LED blue | `#2E9BFF` | Informational lamps (FAN, FLAT), enum "ON" states (TC/CRUISE/A/C active). Blue = reserved informational per ISO 2575. |
| LED blue glow | `#0E2E4D` | Halo behind lit blue lamps. |
| Status green | `#3DDC5A` | Trigger Err = 0 ("healthy") value color only. Green = safe/normal per ISO 2575. |
| Critical flash bg | `#3D0800` | Blink partner color for critical tile backgrounds. |

Contrast check: `#F2F4F6` on `#0E1013` ≈ 16.9:1; `#8A9099` labels on panel ≈ 5.9:1;
even the dim `#6F7680` units clear 4:1 — all far above the ISO 15008 legibility
minimums (≥2:1 direct sun, ≥3:1 diffuse; see Part 5), which is the washout margin
the white v5 theme lacked.

---

## PART 3 — Texture strategy (carbon fiber + brushed aluminum in RealDash)

### 3.1 How custom images get into a RealDash dash (verified workflow)

The developer's own instructions ([forum: How do you create a custom dash design](https://forum.realdash.net/t/how-do-you-create-a-custom-dash-design/3291)):

1. Enter edit mode → **ADD GAUGE → Image** (an "Image Gauge").
2. **Look'n Feel → Images → Background Image** → tap the big **plus-sign (+)** →
   select the file.
3. Tap Done until back on the dash, then save — the asset is **embedded into the
   `.rd` file** on save.

Supported formats (developer statement, same thread): **"PNG for transparent
images, JPG for photograph style images. For pre-defined animations you can use MP4
videos or animated GIFs."** There is no documented hard pixel-size limit; the
developer's performance guidance is to avoid graphics "way too big in pixel size
for their usage" and to limit alpha-blended pixels
([forum: Slow Response/Refresh/FPS on Custom Dashes](https://forum.realdash.net/t/slow-response-refresh-fps-on-custom-dashes/3448),
[forum: Applying alpha blending](https://forum.realdash.net/t/applying-alpha-blending/493)).
Multiple small images should be packed into a single **texture atlas** and sampled
via **Look'n Feel → Images → Subframes** (set X/Y subframe counts, then the
`Subframe` index) — "significantly reduces load times and makes rendering much
faster" ([forum: Play/Pause button transition — dev explanation of atlases](https://forum.realdash.net/t/play-pause-button-transition/4531)).
Per-level images are supported: the **Editing Level** selector in Look'n Feel →
Images lets a gauge swap images between Normal/Warning/Critical
([same thread](https://forum.realdash.net/t/play-pause-button-transition/4531)), and
**Image Blend Color** per level recolors grayscale art live
([official tutorial: Make an indicator](https://realdash.net/manuals/make_an_indicator.php),
[forum: One-off cluster graphics](https://forum.realdash.net/t/one-off-cluster-graphics/920)).
RealDash provides no built-in texture pack beyond the 4 new-dash templates — custom
looks are expected to be authored in GIMP/Illustrator/etc. and imported
([forum: building needle gauge — dev: "I took photos of real dashboards and used GIMP"](https://forum.realdash.net/t/building-needle-gauge/1510)).

The commercial precedent for this exact move is ECUMaster's own manual, which
builds a carbon-fibre page background from a tiled `carbon.png` and layers it under
all elements ([ADU manual](https://inter-rally.pl/data/include/cms/ECUMASTER/Instrukcja_obsugi_ADU_7_AS_ENG.pdf)).

### 3.2 Plan A (preferred): ONE full-screen baked background PNG

Because of the binary-pipeline constraint that **image-type records must not be
cloned** (see Part 8), all static texture, metal, bezels and depth are baked into a
**single 800x480 PNG-24** used as the background image of the dash's one Image
Gauge. Everything dynamic (values, bars, pill fills, pill glows, labels) renders as
native text/bar gauges on top.

Concrete authoring steps (scriptable in Python/Pillow — no artist needed):

1. **Base carbon weave.** Fill `#0B0C0E`. Draw a 2/2 twill weave of diagonal
   ribbons: alternating parallelograms in `#101113` (dark tow) and `#1E2126`
   (light tow), tile cell 10–14px, each light ribbon carrying a 1px `#2A2E34`
   center streak (the per-tow specular band). Twill reads as "the more
   expensive-looking weave used in luxury automotive"
   ([Texturize carbon-fiber generator docs](https://texturize.app/generators/carbon-fiber)).
   Equivalent cheap approximation: two 45°/135° crossed linear gradient layers,
   black 25%/transparent 75% stops, 10px cells, offset half a cell — the standard
   CSS carbon recipe ([carbon CSS tutorial](https://digitalthriveai.com/en-nz/resources/ai-and-automation/help-make-carbon-fiber-texture/)).
   Keep weave contrast LOW (≤ #2A tones) so it never competes with data.
2. **Panel wells.** For each of the 13 value panels and the header band (geometry in
   Part 4), draw a rounded rect (r=8): vertical gradient `#171A1E` → `#0E1013`,
   a 1px top inner edge `#31363D`, a 1px bottom inner edge `#050607`, and a 2px
   soft outer shadow below. This is the canonical 4-shadow skeuomorphic stack:
   contact shadow + ambient shadow + inset top highlight + inset bottom shade,
   single top light source ([Superdesign skeuomorphism recipe](https://www.superdesign.dev/styles/skeuomorphism),
   [skeuomorphic-forge rules](https://github.com/mmmprod/skeuomorphic-forge)).
3. **Brushed aluminum accents.** A 4px full-width strip under the header and 2px
   column separators: vertical gradient `#C7C8C9` → `#9EA1A6` → `#6B6E73` →
   `#B0B3B8` (the classic 4-stop metal ramp — [CSS metal gradient guide](https://thesaastree.com/css-metal-gradient-button-effect-create-metallic-ui-elements/)),
   overlaid with 1px horizontal grain lines alternating ±3 RGB of noise
   (repeating-linear-gradient grain trick, same source; directional-grain rationale
   in [Texturize metal generator docs](https://texturize.app/generators/metal) —
   "aluminium is warmer… coarse stretched layer establishes the visible streaks").
4. **Pill bezels (the 3D lamp housings).** For each of the 6 pills, bake the
   housing only (the lens stays dynamic): outer rounded rect r=16 in gunmetal
   `#353E43` with a 1px `#6B6E73` top arc and 1px `#1A1D20` bottom arc (machined
   ring), then a 4px-deep recessed well: fill `#08090B` with a 2px inner shadow at
   the top (dark) and 1px light lip at the bottom — the "depth well before
   decoration" pattern ([skeuomorphic-forge](https://github.com/mmmprod/skeuomorphic-forge)).
5. Export as `carbonforge_bg.png`, 800x480 PNG-24 (no alpha needed on the base
   layer → cheaper to composite; alpha costs GPU on weak devices —
   [alpha blending thread](https://forum.realdash.net/t/applying-alpha-blending/493)).
6. Import per §3.1 into an Image Gauge stretched to the full canvas, painted first
   (bottom of the z-order; Numpad+/− adjusts z-order in the editor).

### 3.3 Plan B (fallback): no images, gradient approximation

If embedding the PNG proves fragile in the binary pipeline, approximate with native
gauges only (all constructs verified in the earlier procedures research —
[realdash_procedures.md sources](https://forum.realdash.net/t/bar-gauge-and-text-issue/1097)):

- Canvas: full-screen rect `#0B0C0E`; a second full-width rect over the top third
  with a vertical gradient `#12141A` → transparent-equivalent (`#0B0C0E`) fakes a
  top-lit sheen. No weave — flat near-black reads as "satin carbon" at arm's length.
- Panels: rounded-rect text-gauge backgrounds with the bar-gauge gradient trick
  (a Bar Gauge pinned at 100% behind each panel provides `#171A1E`→`#0E1013`
  vertical gradients — bar gauges natively support gradient fills, dev-confirmed in
  [custom dash design thread](https://forum.realdash.net/t/how-do-you-create-a-custom-dash-design/3291)).
  Top edge-light = separate 1px-high rect `#31363D` per panel.
- Metal strips: three stacked 1–2px rects (`#C7C8C9` / `#9EA1A6` / `#6B6E73`) fake
  the metal ramp; skip the grain.
- Pill bezels: two nested rounded rects (outer `#353E43` r=16, inner `#08090B`
  r=12) instead of the baked housing; everything else in the pill recipe (Part 6)
  is unchanged because it is already native.

Plan B loses the weave and grain but keeps 100% of the palette, depth stack, and
LED behavior. Decide A vs B after one loader test with the embedded PNG.

---

## PART 4 — 800x480 layout plan

Same channel set as v5. Grid: 8px outer margin, 8px gutters.

```
x=0                                                                      x=800
+--------------------------------------------------------------------------+ y=0
| BOOST/MAP  [ 184.3 kPa ]      ████████████████████░░░░░░░░░░  (sweep bar) |  header 8..96
+= brushed aluminum strip =================================================+ y=96..100
+----------------+----------------+----------------+----------------+ y=108
| TC             | THROTTLE       | TARGET λ       | CHARGE T       |  row 1 (h=88)
|  ON            |  87 %          |  0.82 λ        |  41 °C         |
+----------------+----------------+----------------+----------------+ y=204
| COOLANT P      | TURBO RPM      | ENGINE LOAD    | FUEL T         |  row 2
|  118 kPa       |  128400 rpm    |  64 %          |  34 °C         |
+----------------+----------------+----------------+----------------+ y=300
| ETHANOL        | TRIGGER ERR    | CRUISE         | A/C            |  row 3
|  72 %          |  0             |  OFF           |  OFF           |
+----------------+----------------+----------------+----------------+ y=388
| (FLAT) (FAN) (LOFUEL) (SBFLT) (COOLANT P) (OIL P)   3D lamp pills  | y=400..464
+--------------------------------------------------------------------------+ y=480
```

Coordinate table (x, y, w, h in the 800x480 space):

| # | Element | x | y | w | h | Notes |
|---|---|---|---|---|---|---|
| BG | Full-screen background image (Plan A) | 0 | 0 | 800 | 480 | `carbonforge_bg.png`, painted first |
| H0 | Header well (baked/panel) | 8 | 8 | 784 | 88 | carbon banner panel |
| H1 | "BOOST/MAP" label | 20 | 14 | 180 | 20 | `#8A9099`, uppercase |
| H2 | Boost value | 20 | 36 | 220 | 52 | `#FFD400`, mono, right-aligned |
| H3 | Boost unit "kPa" | 246 | 64 | 70 | 24 | `#6F7680`, baseline-aligned to H2 |
| H4 | Boost sweep bar — track | 330 | 24 | 452 | 56 | baked well / `#0E1013` rect |
| H5 | Boost sweep bar — fill | 334 | 28 | 444 | 48 | H bar gauge, gradient `#FFD400` → `#FF3226` |
| M | Aluminum strip | 8 | 96 | 784 | 4 | baked metal ramp (Plan A) |
| R1C1 | TC panel | 8 | 108 | 190 | 88 | enum: OFF `#8A9099` / ON `#2E9BFF` |
| R1C2 | Throttle % panel | 206 | 108 | 190 | 88 | |
| R1C3 | Target Lambda panel | 404 | 108 | 190 | 88 | 2 decimals |
| R1C4 | Charge Temp panel | 602 | 108 | 190 | 88 | |
| R2C1 | Coolant Pressure panel | 8 | 204 | 190 | 88 | |
| R2C2 | Turbo RPM panel | 206 | 204 | 190 | 88 | mono font mandatory (6 digits) |
| R2C3 | Engine Load panel | 404 | 204 | 190 | 88 | |
| R2C4 | Fuel Temp panel | 602 | 204 | 190 | 88 | |
| R3C1 | Ethanol % panel | 8 | 300 | 190 | 88 | |
| R3C2 | Trigger Err panel | 206 | 300 | 190 | 88 | value `#3DDC5A` at 0, red > 0 |
| R3C3 | Cruise panel | 404 | 300 | 190 | 88 | enum OFF/ON like TC |
| R3C4 | A/C panel | 602 | 300 | 190 | 88 | enum OFF/ON like TC |
| P1–P6 | Pills FLAT / FAN / LOFUEL / SBFLT / COOLANT P / OIL P | 8 / 140 / 272 / 404 / 536 / 668 | 400 | 124 | 64 | layered recipe, Part 6 |

Inside each 190x88 value panel:

| Sub-element | x (rel) | y (rel) | w | h | Style |
|---|---|---|---|---|---|
| Label | +12 | +10 | 166 | 18 | uppercase, `#8A9099` |
| Value | +12 | +34 | 118 | 44 | mono, `#F2F4F6` (accent/warn/crit per state) |
| Unit | +134 | +54 | 46 | 20 | `#6F7680`, bottom-aligned with value baseline |

Enum panels (TC, CRUISE, A/C) have no unit gauge; the value gauge renders the
state text (OFF/ON) centered in the label+unit footprint.

---

## PART 5 — Why dark works in sunlight (readability rationale)

- **ISO 15008 legibility floors:** driver-relevant content must hold a contrast
  ratio ≥ **2:1 under direct sunlight** (45 klx test condition) and ≥ **3:1 under
  diffuse daylight** ([Wiley/SID: Understanding the Requirements for Automotive Displays in Ambient Light Conditions](https://sid.onlinelibrary.wiley.com/doi/10.1002/j.2637-496X.2016.tb00902.x),
  [Information Display: Optimized Workflow for ISO 15008 Contrast Evaluation](https://sid.onlinelibrary.wiley.com/doi/full/10.1002/msid.1549)).
- **Why washout kills light themes:** sunlight reflected by the panel adds a
  constant luminance term to *both* foreground and background. A white-card UI
  starts with most of its luminance budget already spent on the background, so the
  ratio collapses toward 1:1. A near-black background keeps the denominator small —
  the same reflected light costs far less contrast. The engineering metric is
  **Ambient Contrast Ratio** — "a display may have high contrast in laboratory
  measurements but still perform poorly outdoors if surface reflections reduce
  effective contrast" ([VarTech: Sunlight-Readable Displays](https://www.vartechsystems.com/articles/designing-operator-interfaces-bright-outdoor-conditions)).
- **The sunlight-optimized UI rule:** "the complete dynamic range (black to white)
  is utilized by the UI" ([Wiley/SID paper](https://sid.onlinelibrary.wiley.com/doi/10.1002/j.2637-496X.2016.tb00902.x)) —
  i.e., near-black bg + near-white digits, which is exactly what every commercial
  race dash in Part 1 ships by default.
- **Color discipline:** "maintain strong luminance contrast between foreground and
  background; avoid relying solely on subtle color differences; reinforce critical
  conditions with text or icons" ([VarTech](https://www.vartechsystems.com/articles/designing-operator-interfaces-bright-outdoor-conditions));
  "high-contrast colors, large fonts, minimal clutter, avoidance of subtle grays"
  ([outdoor LCD integration guide](https://dev.to/alan12/how-to-integrate-a-high-brightness-lcd-into-outdoor-embedded-systems-a-practical-guide-3ced)).
  Consequence for this spec: saturated accents (`#FFD400`, `#FF3226`, `#2E9BFF`)
  ride on top of a *luminance* hierarchy — every state change also changes
  brightness or fill, never hue alone. Anti-washout accent choice: fully saturated
  primaries survive desaturation-by-glare far better than pastels; the carbon weave
  is kept ≤ `#2A` so it disappears (rather than turning to noise) in direct sun.

---

## PART 6 — 3D status pill treatment (the "physical indicator lamp" recipe)

Design goal: each pill should read as a **recessed LED lamp in a machined gunmetal
housing** — bezel, dark glass lens when off, saturated glowing lens + halo when lit.
Layer recipe below is the skeuomorphic LED/lamp stack (radial-bright center →
darker rim lens, inset depth shadow, outer bloom glow, bezel recess, top-left
specular) documented in
[Superdesign's skeuomorphism CSS recipe](https://www.superdesign.dev/styles/skeuomorphism),
[skeuomorphic-forge (industrial panels, LED indicators, depth wells)](https://github.com/mmmprod/skeuomorphic-forge),
and the SkeuoLED-style component patterns in
[astro-skeuomorphism-theme](https://github.com/ctrimm/astro-skeuomorphism-theme) —
translated to RealDash primitives (rounded rects, per-level colors, one baked PNG).

Layer stack per pill (124x64 footprint, back → front):

| Layer | Geometry | Off state | Lit state | RealDash primitive |
|---|---|---|---|---|
| 1. Housing + well | 124x64, r=16 bezel; 4px recess | baked: gunmetal `#353E43` ring, `#6B6E73` top arc, `#1A1D20` bottom arc, well `#08090B` w/ top inner shadow | (static) | Baked into background PNG (Plan A) or 2 nested rounded rects (Plan B) |
| 2. Glow halo | 132x72 centered (−4px offset), r=18 | transparent (opacity 0) | LED glow color (`#66120C`/`#664A00`/`#0E2E4D`) at ~55% opacity | Rounded-rect text gauge, per-level Background Color (Normal transparent; Warning/Critical glow) |
| 3. Lens fill | 112x52 inset 6px, r=12 | `#15181C` (dark glass) | full LED color `#FF3226` / `#FFB300` / `#2E9BFF` | Rounded-rect text gauge, dynamic bg fill 0→1 or per-level colors |
| 4. Gloss highlight | 112x24, top half of lens, r=12 top corners | white at 12% opacity | same (reads as glass over the lit lens) | Static rounded-rect gauge, semi-transparent white bg, unbound |
| 5. Legend text | centered, h=18 | `#4A5058` | white `#FFFFFF` (red/blue lens) or near-black `#1A1400` (amber/yellow lens) | Text gauge, per-level Text Color |

Behavior wiring (matches the proven v5 pill logic in the local build system):

- **Informational pills (FLAT, FAN — blue):** steady, never blinking. Dynamic
  background fill over min 0 / max 1 with alarm windows pushed out of reach
  (warn/crit above 999, below −999) so the gauge never leaves Normal level — the
  established "steady pill" recipe.
- **Caution pills (LOFUEL, SBFLT — amber):** warning window `0.5`, lit lens
  `#FFB300`, **no blink** (persistent caution).
- **Critical pills (COOLANT P, OIL P — red):** critical window `0.7`, lit lens
  `#FF3226`, **Blink Speed set on Critical level only** (Look'n Feel → Special →
  Blink Speed; Normal stays 0) — the dev-documented alarm blink path
  ([forum: Flashing indicators](https://forum.realdash.net/t/flashing-indicators/7487)).

Color-to-meaning mapping follows the ISO 2575 telltale color law: **red = danger /
imminent serious damage, yellow/amber = caution or malfunction, blue = reserved
informational, green = safe normal operation**
([ISO 2575 color conventions summary](https://standards.iteh.ai/catalog/standards/iso/9703c4a8-79ba-4606-8bbc-f94f76b4994a/iso-2575-2021),
[ISO 2575 PDF preview, §5.1–5.4](https://cdn.standards.iteh.ai/samples/39704/114c5db061a14fa2b81b633a2dbb60b8/ISO-2575-2004.pdf)).
That is exactly the red/yellow/blue LED language requested, with a standards
pedigree.

Depth realism rules applied across pills AND panels (from the skeuomorphic
sources): one light source (top), warm-tinted highlights rather than pure white,
dark-alpha for depth vs light-alpha for specular kept separate, minimum 4-layer
shadow stacks — "one shadow looks flat; four look machined"
([Superdesign recipe](https://www.superdesign.dev/styles/skeuomorphism),
[skeuomorphic-forge priority rules](https://github.com/mmmprod/skeuomorphic-forge)).

---

## PART 7 — Typography, labels, units, warning/critical

### Typography

- Values: **fixed-width / mono-spaced font** (Look'n Feel → Font & Text) so digits
  don't dance as they change width — dev recommendation
  ([custom dash design thread](https://forum.realdash.net/t/how-do-you-create-a-custom-dash-design/3291)).
  RealDash text size = gauge height, so sizes are enforced by gauge rect height:
  hero boost value 52px, panel values 44px, labels 18px, units 20–24px, pill
  legends 18px.
- Labels: UPPERCASE, `#8A9099`, top-left of each panel. Label names the
  measurement only ("COOLANT P", "CHARGE T", "TARGET λ" is acceptable since λ names
  the quantity).
- **Units convention (hard rule): units render NEXT TO the value readout as their
  own smaller, dimmer gauge (`#6F7680`, ~45% of value height, baseline-aligned) —
  never inside the label when the label names the measurement.** This mirrors the
  ADU's separate `Unit color`/`Unit font` element
  ([ADU manual objects tables](https://www.ecumaster.com/files/ADU/adu_manual_en.pdf))
  and AiM's separately-styled Unit field per channel
  ([RS3 customization FAQ](https://www.aimsportsystems.com.au/download/faqs/eng/software/rs3/FAQ_RS3_DisplayCustomization_100_eng.pdf)).
- Decimals per channel resolution (Link G4X XML is the source of truth): lambda 2
  decimals, temps/pressures 0–1, integers 0.

### Warning / critical / LED treatment (value panels)

- Normal: value `#F2F4F6` on the panel gradient.
- Warning: value AND its unit recolor to `#FFB300`; panel background unchanged
  (quiet escalation — AiM/ADU recolor-the-digit convention).
- Critical: value `#FF3226`; panel background blinks `#0E1013` ↔ `#3D0800`
  (Blink Speed on Critical only). The fill-level change (not just hue) is the
  MoTeC-style "invert, don't tint" cue and survives sun-glare desaturation.
- Boost sweep bar: gradient `#FFD400` → `#FF3226` so the tip "heats up" toward the
  overboost end, echoing the green→yellow→red RPM segment convention on AiM/ADU
  hardware bars.
- Editing-level discipline: always set the Editing Level selector BEFORE adjusting
  colors — editing while "All" is selected wipes per-level colors (dev-confirmed
  gotcha, [bar gauge thread](https://forum.realdash.net/t/bar-gauge-and-text-issue/1097)).

---

## PART 8 — Implementation notes for the automation agent

Constraints and steps, reconciled against the local `realdash-dashboard-builder`
skill and the binary `.rd` pipeline:

1. **Asset budget: exactly ONE image gauge.** The binary pipeline must never clone
   bar/graph/image records (clones hang the loader) and image-type records must sit
   grouped at the END of the record stream with `Image Gauge 1` (asset-name map
   carrier) last. Therefore Plan A uses a single full-screen `carbonforge_bg.png`
   on the dash's one Image Gauge, built from `_build\backup\asset_donor_template.rd`.
   All pill bezels, panel wells, metal strips and the weave are baked into that one
   PNG. **Verify paint order vs record order on a test load** — the background must
   paint underneath the text/bar records; if the required record ordering forces
   the image to paint on top and paint order cannot be fixed binarily, fall back to
   Plan B (§3.3, zero images).
2. **Generate the PNG programmatically** (Python + Pillow, steps in §3.2) at
   exactly 800x480, PNG-24, no alpha. Keep it the only large texture; do not add
   per-pill PNGs (alpha-blend cost + clone ban). If small icons are ever needed,
   pack them into one atlas and use Subframes
   ([dev atlas guidance](https://forum.realdash.net/t/play-pause-button-transition/4531)).
3. **GUI import path** (if importing via the app instead of binary embedding):
   ADD GAUGE → Image → Look'n Feel → Images → Background Image → **+** → pick the
   PNG from `C:\Users\danie\Downloads` → Done → FILE → SAVE, then verify the file's
   LastWriteTime changed. PNG/JPG confirmed supported
   ([dev statement](https://forum.realdash.net/t/how-do-you-create-a-custom-dash-design/3291)).
4. **Everything dynamic is text/bar gauges** (proven binary-safe): 13 label gauges,
   13 value gauges, 10 unit gauges (no units on TC/CRUISE/A/C enum panels), 1 hero
   bar fill, plus per pill: halo + lens + gloss + legend = 24 gauges. Keep the total
   text-record count ≤ 122 renderables (RealDash 1.92 render cap) with 2 inert
   transparent pads last — count before building.
5. **Text sizing** is gauge-height-driven; never write the stored font-size float.
   Use mono font for all value gauges.
6. **Per-level styling:** set Editing Level BEFORE color edits ("All" wipes
   per-level colors). Blink Speed only on Critical (pills: only OIL P / COOLANT P;
   panels: critical level only). Steady informational pills (FAN, FLAT) use the
   dynamic-fill min0/max1 trick with alarm windows at ±999 so they can never blink.
7. **Bindings are GUI-only** (channel hashes not computable): INPUT & VALUES →
   Select Data Source → ECU SPECIFIC → search → SELECT INPUT → DONE, per channel,
   then audit with `tools/audit_gauge.py`. Same channel set as v5 — reuse v5's
   binding map. Decimals from `link_g4x_realdash.xml`.
8. **Backups + verification loop:** back up the `.rd` to `_build\backup\` before
   every session; after each binary write, reload via `tools/load_dash.py` and read
   the screenshot; discard any "Save dash?" prompt so the app doesn't clobber disk
   edits. A malformed image record can hang the loader in a splash loop — keep the
   pre-image-gauge `.rd` snapshot until the background is proven to load.
9. **Acceptance checks:** (a) all 13 values legible in a screenshot scaled to 50%
   (arm's-length test); (b) unit text present beside every non-enum value, absent
   from labels; (c) pills read as lamps: visible bezel ring, dark lens off, filled
   lens + halo lit; (d) warning state changes value color, critical state blinks
   the panel; (e) no gauge overlaps the 8px outer margins.

---

## Sources

Commercial dashes:
- [ECUMaster ADU manual (EN) — backgrounds, carbon.png texture example, per-element colors](https://www.ecumaster.com/files/ADU/adu_manual_en.pdf)
- [ECUMASTER ADU-5/ADU-7 user manual mirror (inter-rally.pl) — texture/tiling workflow](https://inter-rally.pl/data/include/cms/ECUMASTER/Instrukcja_obsugi_ADU_7_AS_ENG.pdf)
- [ECUMaster USA ADU7 product page — antiglare, 800x480, 15 RGB LEDs](https://ecumasterusa.com/products/ecumaster-adu7-advanced-display-unit-rev-2-ip65)
- [Xtra Motorsport ADU-5 — 600 cd/m², anti-aliased 50fps, auto-brightness](https://xtramotorsport.com/product/ecumaster-adu-5-advanced-display-unit/)
- [Haltech iC-7 Quick Start Guide — LED colors, alarms, dark default screens](https://g8only.com/wp-content/uploads/2024/04/HAL_iC7_QSG_Rev12_WEB.pdf)
- [MarcL01/Custom-Haltech-IC7-Layout — QML layouts, custom images folder](https://github.com/MarcL01/Custom-Haltech-IC7-Layout)
- [Haltech uC-10 product page — optically bonded, NSP customization](https://www.haltech.com/product/ht-068000-haltech-uc-10/)
- [Motorsport Tuning Solutions uC-10 guide — day/night modes, custom pages](https://www.motorsporttuningsolutions.com/blogs/motorsport-blog/haltech-uc-10-digital-dash-with-haltech-link-ecus-guide)
- [LSX Mag uC-10 overview — 1280x480, NSP day/night](https://www.lsxmag.com/news/haltech-uc-10-digital-dash-is-much-more-than-a-display/)
- [Boosted International uC-10 skin bundle — OEM+ skin packs precedent](https://boostedintl.com/product/haltech-uc-10-screen-and-dash-mount-skin-bundle/)
- [AiM MXG user guide — RGB alarm LEDs, color/blink/message config](https://www.aimtechnologies.com/aim-support/docs/MXG_user_guide_101.pdf)
- [AiM MXS Strada user guide — high-contrast TFT, 800x480, page layouts](http://www.mtoengineering.com/downloads.html?file=files%2Fdownloads%2FAIM%2FMXS+Strada%2FMXSStrada_user_guide_101.pdf)
- [AiM MX 1.2/1.3 Strada guide — 700 cd/m², 600:1–1000:1 contrast, ambient sensor](https://support.aimshop.com/product-documentation/pdf/MXS_1.2_Strada/MX1.2+1.3_Strada_user_guide_103_eng.pdf)
- [AiM RS3 Display customization FAQ — per-channel digit/label/unit font, color, size, outline](https://www.aimsportsystems.com.au/download/faqs/eng/software/rs3/FAQ_RS3_DisplayCustomization_100_eng.pdf)
- [MoTeC C127 product page — anti-reflective, sunlight readability, layouts](https://www.motec.com.au/products/C127)
- [MoTeC C127 user manual — fixed layouts + colour scheme editing](https://www.milspecwiring.com/DATA%20SHEETS/C127%20User%20Manual.pdf)
- [MoTeC forum — 10 templates × 16 colour schemes](https://forum.motec.com.au/viewtopic.php?f=70&t=4349)
- [MoTeC Display Creator upgrade — custom graphics/images/themes](https://www.motorsportselectronics.com/products/c127-display-creator-upgrade)
- [Link ECU dash display overview — AiM partnership, MXS/MXG/MXT](https://linkecu.com/dash-display-overview/)
- [Link MXS Strada Street edition — RS3 configuration, RGB LEDs](https://dealers.linkecu.com/MXS_street)
- [Impulse Performance Link MXS listing — alarm color/blink/message options](https://www.impulse-performance.com/products/link-ecu-mxs-strada-5-dash-powered-by-aim)

Textures, metal, LED/skeuomorphic treatments:
- [Carbon fiber texture with CSS — crossed 45° gradient recipe, scale guidance](https://digitalthriveai.com/en-nz/resources/ai-and-automation/help-make-carbon-fiber-texture/)
- [Texturize carbon-fiber generator — twill/plain weave anatomy, tint guidance](https://texturize.app/generators/carbon-fiber)
- [Texturize classic black carbon — palette #101010/#181818/#202020/#282828, 64–128px tiling](https://texturize.app/texture/carbon-fiber-classic-black)
- [Texturize metal generator — brushed grain construction, aluminum tint notes](https://texturize.app/generators/metal)
- [CSS metal gradient button effect — 4-stop aluminum ramp + repeating grain lines](https://thesaastree.com/css-metal-gradient-button-effect-create-metallic-ui-elements/)
- [Color Labs: Brushed Metal #C7C8C9](https://colorlabs.net/colors/brushed-metal)
- [Color Labs: Flat Aluminum #C3C6CD](https://colorlabs.net/colors/flat-aluminum)
- [Color Labs: Aluminum Silver #8C8D91](https://colorlabs.net/colors/aluminum-silver)
- [Figma color reference: Gunmetal Gray #353E43](https://www.figma.com/colors/gunmetal-gray/)
- [Superdesign skeuomorphism recipe — 4-shadow stack, top light, no pure white/black](https://www.superdesign.dev/styles/skeuomorphism)
- [skeuomorphic-forge — industrial panels, LED indicators, depth wells, warm speculars](https://github.com/mmmprod/skeuomorphic-forge)
- [astro-skeuomorphism-theme — SkeuoLED glowing indicator component patterns](https://github.com/ctrimm/astro-skeuomorphism-theme)

RealDash-specific:
- [RealDash Gallery — premium dark/racing dashes (GTV6, Pole Position, F40, Screamer)](https://realdash.net/gallery.php)
- [Forum: How do you create a custom dash design — PNG/JPG/MP4/GIF support, image import steps](https://forum.realdash.net/t/how-do-you-create-a-custom-dash-design/3291)
- [Official tutorial: Make an indicator — Image gauge + per-level Image Blend Color](https://realdash.net/manuals/make_an_indicator.php)
- [Forum: Play/Pause button transition — per-level images, texture atlas + Subframes](https://forum.realdash.net/t/play-pause-button-transition/4531)
- [Forum: Dash Design for Beginners — ARC Gauge — layered background/asset workflow, dark bg + red warning zones](https://forum.realdash.net/t/dash-design-for-beginners-arc-gauge/7086)
- [Forum: building needle gauge — no built-in texture packs; author graphics in GIMP](https://forum.realdash.net/t/building-needle-gauge/1510)
- [Forum: One-off cluster graphics — Shadows (auto/custom map + offset), grayscale + blend color](https://forum.realdash.net/t/one-off-cluster-graphics/920)
- [Forum: Slow Response/Refresh/FPS — image sizing, atlas, square-gauge performance](https://forum.realdash.net/t/slow-response-refresh-fps-on-custom-dashes/3448)
- [Forum: Applying alpha blending — transparency GPU cost](https://forum.realdash.net/t/applying-alpha-blending/493)
- [Forum: Flashing indicators — Blink Speed per editing level](https://forum.realdash.net/t/flashing-indicators/7487)
- [Forum: Bar gauge and text issue — per-level colors, "All" wipes levels](https://forum.realdash.net/t/bar-gauge-and-text-issue/1097)

Readability & color standards:
- [Wiley/SID: Automotive displays in ambient light — ISO 15008 2:1 sun / 3:1 diffuse, full-dynamic-range UI](https://sid.onlinelibrary.wiley.com/doi/10.1002/j.2637-496X.2016.tb00902.x)
- [Information Display: ISO 15008 contrast evaluation workflow — 45 klx test, reflections](https://sid.onlinelibrary.wiley.com/doi/full/10.1002/msid.1549)
- [VarTech: Sunlight-readable displays — Ambient Contrast Ratio, luminance-contrast rules](https://www.vartechsystems.com/articles/designing-operator-interfaces-bright-outdoor-conditions)
- [Outdoor high-brightness LCD integration guide — high-contrast UI, avoid subtle grays](https://dev.to/alan12/how-to-integrate-a-high-brightness-lcd-into-outdoor-embedded-systems-a-practical-guide-3ced)
- [ISO 2575:2021 — telltale color conventions (red/amber/green/blue)](https://standards.iteh.ai/catalog/standards/iso/9703c4a8-79ba-4606-8bbc-f94f76b4994a/iso-2575-2021)
- [ISO 2575 PDF preview §5 — color meanings verbatim](https://cdn.standards.iteh.ai/samples/39704/114c5db061a14fa2b81b633a2dbb60b8/ISO-2575-2004.pdf)

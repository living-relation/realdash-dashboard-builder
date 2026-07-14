# Design Inspiration — Two New Dashboard Concepts (RealDash 1.92, 800x480)

Research deliverable for the ST185 Celica GT-Four / Link G4X RealDash project.
Constraints honored: text gauges (label + value), bar gauges (H/V fill, gradient OK),
rounded rectangles, solid/gradient colors, blink-on-alarm. No custom images required.
Both concepts are deliberately distinct from each other **and** from the existing
"modern flat dark navy tile grid" dashboard.

Research note: professional race displays (MoTeC C125, AiM MXG) natively run
**800x480** — the same canvas as ours — and their stock layouts are the strongest
directly-transferable references ([MoTeC C125 specs](https://www.motec.com.au/products/C125),
[AiM MXG specs](https://www.aimtechnologies.com/aim-support/docs/MXG_user_guide_101.pdf)).
Race-dash convention: a full-width sweep bar on top, one or two giant "hero" numerals,
channel boxes with small labels and large values, color-coded red ranges, and pop-up /
flashing alarms ([Precision Racing C125 layout description](https://precisionracing.com.au/product/motec-c125-display/),
[Haltech IC-7 Quick Start Guide](https://g8only.com/wp-content/uploads/2024/04/HAL_iC7_QSG_Rev12_WEB.pdf)).
OEM luxury convention: deep blacks (OLED), clear graphic structure, thin accent lines,
minimalist type, critical items pinned to a fixed strip on the bottom edge
([Porsche Driver Experience / Porsche DI](https://newsroom.porsche.com/en/press-kits/Cayenne-Electric-and-Cayenne-Turbo-Electric/Porsche-Driver-Experience.html),
[PRINT Magazine on Audi Virtual Cockpit](https://www.printmag.com/branding-identity-design/driven-distraction-dashboard-design-typography/)).

---

# CONCEPT 1 — "STAGE 185" (WRC / MoTeC-style rally telemetry)

## Design intent

A pure motorsport data display: matte black screen, huge white numerals, rally-yellow
accents and a fat full-width boost sweep bar across the top — the visual language of a
MoTeC C125 / AiM MXG stage dash, where every value must be readable in one glance at
speed. Nothing is decorative; hierarchy comes from sheer size contrast (hero boost
numeral ~6x label height) and thick chunky separations, not from color variety.

## Palette

| Role | Hex | Usage |
|---|---|---|
| Background | `#000000` | Entire canvas. True black, like an anti-reflective race TFT. |
| Tile / panel | `#121212` | Channel boxes (rounded rect, corner radius ~6). |
| Panel outline | `#2E2E2E` | 2px box outlines (AiM RS3 exposes exactly this: box outline color + thickness — [AiM display customization FAQ](https://www.aimsportsystems.com.au/download/faqs/eng/software/rs3/FAQ_RS3_DisplayCustomization_100_eng.pdf)). |
| Primary text (values) | `#FFFFFF` | All numerals. |
| Secondary / label text | `#8C8C8C` | Uppercase labels + units. |
| Accent | `#FFD400` | Rally yellow: hero boost numeral, bar fill start, active status text. |
| Warning | `#FF9500` | Amber: value + outline turn amber in warning range. |
| Critical | `#FF2A00` | Red: value/box flip red + blink; alarm pill fill. |
| Status-OK green | `#3DDC5A` | Small "armed/on" status states only (TC ON, A/C ON). |

## 800x480 layout plan

ASCII wireframe (1 char ≈ 10px wide):

```
x=0                                                                      x=800
+--------------------------------------------------------------------------+ y=0
| BOOST SWEEP BAR  ############################...........................|  h=44
+---------------------------------------+----------------+-----------------+ y=52
|  BOOST PSI                            |  LAMBDA TGT    |  TC       ON    |
|                                       |                +-----------------+
|        1 8 . 4        (giant,         |     0.82       |  CRUISE   OFF   |
|                        h=132)         |    (h=88)      +-----------------+
|                                       |                |  A/C      OFF   |
+------------------+------------------+-+---------------++-----------------+ y=240
| THROTTLE %       | ENGINE LOAD %    | CHARGE/IAT C    | COOLANT P kPa    |
|      87          |      64          |      41         |      118         |
| ####### ....     | #####  ......    |                 |                  |
+------------------+------------------+-----------------+------------------+ y=354
| TURBO RPM        | FUEL TEMP C      | ETHANOL %       | TRIG ERRORS      |
|    128,400       |      34          |      72         |       0          |
+--------+---------+--------+---------+--------+--------+---------+--------+ y=436
|  FLAT  |   FAN   | LOFUEL |  SBFLT  | COOL P |  OIL P |  (alarm pills)   |
+--------+---------+--------+---------+--------+--------+------------------+ y=474
```

Coordinate table (x, y, w, h in the 800x480 space):

| # | Element | x | y | w | h | Notes |
|---|---|---|---|---|---|---|
| 1 | Boost sweep bar — track | 0 | 0 | 800 | 44 | Rounded rect `#121212`, outline `#2E2E2E` |
| 1b | Boost sweep bar — fill | 4 | 4 | 792 | 36 | H bar gauge, gradient (see below) |
| 2 | Hero BOOST tile | 8 | 52 | 384 | 180 | `#121212` panel |
| 2a | · label "BOOST PSI" | 24 | 60 | 200 | 24 | left-aligned, `#8C8C8C` |
| 2b | · value | 24 | 92 | 352 | 132 | `#FFD400`, right-aligned |
| 3 | Hero LAMBDA tile | 400 | 52 | 192 | 180 | |
| 3a | · label "LAMBDA TGT" | 416 | 60 | 160 | 22 | |
| 3b | · value | 416 | 104 | 160 | 88 | `#FFFFFF`, centered |
| 4 | TC status block | 600 | 52 | 192 | 56 | label left, state right |
| 5 | CRUISE status block | 600 | 114 | 192 | 56 | |
| 6 | A/C status block | 600 | 176 | 192 | 56 | |
| 7 | Throttle % tile | 8 | 240 | 192 | 106 | mini bar at bottom |
| 8 | Engine Load % tile | 205 | 240 | 192 | 106 | mini bar at bottom |
| 9 | Charge/IAT tile | 402 | 240 | 192 | 106 | |
| 10 | Coolant Pressure tile | 599 | 240 | 192 | 106 | |
| 11 | Turbo RPM tile | 8 | 354 | 192 | 72 | |
| 12 | Fuel Temp tile | 205 | 354 | 192 | 72 | |
| 13 | Ethanol % tile | 402 | 354 | 192 | 72 | |
| 14 | Trigger Errors tile | 599 | 354 | 192 | 72 | value `#3DDC5A` at 0, red >0 |
| P1–P6 | Alarm pills FLAT / FAN / LOFUEL / SBFLT / COOLANT P / OIL P | 10 / 141 / 272 / 403 / 534 / 665 | 436 | 125 | 38 | rounded rect, radius 19 (full pill) |

Inside the mid tiles (7–10): label at (tile_x+12, tile_y+8, w-24, h=20); value at
(tile_x+12, tile_y+30, w-24, h=56); mini bar at (tile_x+12, tile_y+90, w-24, h=10).
Inside lower tiles (11–14): label h=18 at top, value h=44 below.

## Typography guidance

- Chunky and loud. In RealDash text size = gauge height, so enforce ratios by gauge height:
  labels **20–24px**, mid-tile values **56px** (~2.5x label), hero boost value **132px**
  (~6x label), lambda hero **88px**, lower-tier values **44px**, status states **28px**.
- Labels: UPPERCASE, left-aligned at tile top-left. Values: right-aligned in the hero
  boost tile (digits grow leftward — race-dash convention), centered in all square tiles.
- Units live in the label ("BOOST PSI", "CHARGE/IAT C") — never next to the numeral,
  so the numeral stays maximal, exactly like MoTeC/AiM channel boxes.

## Bar gauge treatment

- **Hero boost sweep (top, 792x36):** horizontal fill, gradient `#FFD400` → `#FF2A00`
  (yellow body ending hot red at the overboost end, mimicking an RPM sweep's red zone —
  [Precision Racing C125](https://precisionracing.com.au/product/motec-c125-display/)).
  Track `#121212`. Range: -14 to +22 psi so idle vacuum still animates.
- **Mini bars (Throttle, Load; 168x10):** solid-feel gradient `#5A5A5A` → `#FFD400`
  on track `#000000`. Thin enough to read as an underline, thick enough at arm's length.
- Segment ticks are optional: overlay 3 vertical 2px `#000000` rects on the hero bar at
  25/50/75% to fake the segmented race-bar look with pure rectangles.

## Warning / critical treatment

- Warning range: value text and tile outline switch to `#FF9500` (matches IC-7 "red
  ranges for channels — numeric display changes color" behavior — [IC-7 QSG](https://g8only.com/wp-content/uploads/2024/04/HAL_iC7_QSG_Rev12_WEB.pdf)).
- Critical: value `#FF2A00` + **blink-on-alarm on the tile background** (flash between
  `#121212` and `#3D0800`). Big, unmissable, ugly on purpose.
- Alarm pills: inactive = `#121212` fill, `#2E2E2E` outline, `#4A4A4A` text (visible
  but dead). Active = fill `#FF2A00`, text `#FFFFFF`, blink ON. COOLANT P and OIL P
  may also blink the hero boost tile outline red as a redundancy cue.

## Sources (Concept 1)

- [MoTeC C125 product page — 800x480, layouts, color schemes](https://www.motec.com.au/products/C125)
- [Precision Racing — C125 layout details: RPM sweep, color variations, zero-centred bar](https://precisionracing.com.au/product/motec-c125-display/)
- [Haltech IC-7 Quick Start Guide — alarm colors, red ranges, flashing alarm behavior](https://g8only.com/wp-content/uploads/2024/04/HAL_iC7_QSG_Rev12_WEB.pdf)
- [AiM MX TFT custom dashboard — box outline/background/bar colors are the styling primitives](https://www.aimsports.com/us/products/mx-tft-series/custom-dashboard.htm)
- [AiM RS3 display customization FAQ — per-channel font color/size/alignment](https://www.aimsportsystems.com.au/download/faqs/eng/software/rs3/FAQ_RS3_DisplayCustomization_100_eng.pdf)
- [Brewed Motorsports MoTeC Display Creator custom layouts — pro custom-layout conventions](https://www.brewedmotorsports.com/display-creator-motec-dash/)
- [RealDash forum: "Haltech IC-7 style hero dash page" — community precedent for this style in RealDash](https://forum.realdash.net/t/haltech-ic-7-style-hero-dash-page/1273)

---

# CONCEPT 2 — "MIDNIGHT CIRCUIT" (OEM-luxury x synthwave neon)

## Design intent

An elegant night-drive cluster that reads like a Porsche/Audi OLED panel restyled in
synthwave: a deep violet-black vertical gradient, **no tile boxes at all** — content
zones separated only by 1px hairlines — thin lavender-white numerals, and neon cyan
accents used sparingly (~10–15% of the surface, per neon-UI best practice). Warnings
escalate through neon yellow to hot magenta, so alert states feel like the neon "waking
up" rather than a klaxon.

## Palette

| Role | Hex | Usage |
|---|---|---|
| Background (gradient top) | `#060411` | Vertical gradient start (top). |
| Background (gradient bottom) | `#131028` | Gradient end (bottom) — subtle violet lift. |
| Panel (only for chips/pills) | `#14122A` | Status chips + alarm segments; everything else is boxless. |
| Primary text (values) | `#F0E8FF` | Cool lavender-white ("light emitted from a screen"). |
| Secondary / label text | `#9070C8` | Muted purple "monitor glow" for labels + units. |
| Accent | `#00F0FF` | Neon cyan: hairlines, bar fills, active statuses. |
| Accent 2 (gradient partner) | `#B026FF` | Electric purple: far end of bar gradients. |
| Warning | `#FCEE0A` | Neon yellow: warning-range values + hairline recolor. |
| Critical | `#FF2A6D` | Hot magenta-red: critical values, alarm segments, blink. |

Palette anchors are documented synthwave/cyberpunk systems: background `#0D0818`,
foreground `#F0E8FF`, muted `#9070C8`, neon cyan accent
([gloam synthwave theme spec](https://github.com/marvinrichter/gloam/blob/main/themes/synthwave/synthwave.md));
cyan `#00F0FF` / magenta `#FF2A6D` / yellow `#FCEE0A` / void-black
([Cybercore CSS palette](https://github.com/GasmanDev/cybercore-css)); electric purple
`#B026FF` and "dark bg + thin 1px separators, slight rounding" rules
([mph synthwave dashboard skill](https://github.com/mphinance/alpha-skills/tree/main/plugins/mph-kit/skills/mph-synthwave-theme));
"always dark backgrounds, limit neon to 10–15% of the UI"
([DevPalettes neon guide](https://devpalettes.com/neon-color-palettes/)).

## 800x480 layout plan

Porsche-style three-zone ("tube") structure: left data column, center hero, right data
column; statuses on a thin top rail; alarms pinned to a fixed bottom edge strip (the
Audi Virtual Cockpit puts fixed warning symbols along the bottom edge —
[PRINT Magazine](https://www.printmag.com/branding-identity-design/driven-distraction-dashboard-design-typography/)).

```
x=0                                                                      x=800
+--------------------------------------------------------------------------+ y=0
|   [ TC : ON ]            [ CRUISE : OFF ]              [ A/C : OFF ]     |  rail h=44
|                                                                          |
|  LAMBDA TGT        |            B O O S T             |  CHARGE/IAT C    | y=60
|  0.82              |                                  |  41              |
|  ------------      |                                  |  ------------    |
|  THROTTLE %        |          1 8 . 4                 |  COOLANT P kPa   | y=148
|  87                |         (h=110 thin)             |  118             |
|  ======            |                                  |  ------------    |
|  ENGINE LOAD %     |     psi                          |  FUEL TEMP C     | y=236
|  64                |  ~~~~~~~~~~~~~~~~~~~~~~~~~~      |  34              |
|  ======            |  (gradient bar, h=12)            |  ------------    |
|  TURBO RPM         |                                  |  ETHANOL %       | y=324
|  128,400           |        TRIG ERRORS               |  72              |
|  ------------      |            0                     |  ------------    |
|                    |                                  |                  | y=410
| [FLAT] [FAN] [LOFUEL] [SBFLT] [COOLANT P] [OIL P]   (ghost segments)     | y=430
+--------------------------------------------------------------------------+ y=480
```

(`|` = 1px vertical hairlines at x=250 and x=549; `------` = 1px hairline underlines;
`======` = 6px mini gradient bars.)

Coordinate table (x, y, w, h in the 800x480 space):

| # | Element | x | y | w | h | Notes |
|---|---|---|---|---|---|---|
| 0 | Background rect | 0 | 0 | 800 | 480 | V-gradient `#060411` → `#131028` |
| S1 | TC status chip | 40 | 10 | 170 | 30 | rounded rect r=15, `#14122A`, 1px `#00F0FF` outline when ON |
| S2 | CRUISE status chip | 315 | 10 | 170 | 30 | same |
| S3 | A/C status chip | 590 | 10 | 170 | 30 | same |
| V1 | Left column hairline | 250 | 56 | 1 | 350 | `#9070C8` @ ~25% alpha (use `#2A2246`) |
| V2 | Right column hairline | 549 | 56 | 1 | 350 | same |
| L1 | Target Lambda — label / value / rule | 32 | 60 / 80 / 130 | 200 | 16 / 44 / 1 | rule = 1px `#2A2246` |
| L2 | Throttle % — label / value / bar | 32 | 148 / 168 / 220 | 200 | 16 / 44 / 6 | 6px mini gradient bar |
| L3 | Engine Load % — label / value / bar | 32 | 236 / 256 / 308 | 200 | 16 / 44 / 6 | |
| L4 | Turbo RPM — label / value / rule | 32 | 324 / 344 / 394 | 200 | 16 / 44 / 1 | |
| R1 | Charge/IAT — label / value / rule | 568 | 60 / 80 / 130 | 200 | 16 / 44 / 1 | |
| R2 | Coolant Pressure — label / value / rule | 568 | 148 / 168 / 220 | 200 | 16 / 44 / 1 | |
| R3 | Fuel Temp — label / value / rule | 568 | 236 / 256 / 308 | 200 | 16 / 44 / 1 | |
| R4 | Ethanol % — label / value / rule | 568 | 324 / 344 / 394 | 200 | 16 / 44 / 1 | |
| C1 | "BOOST" hero label | 280 | 84 | 240 | 20 | centered, letter-spaced |
| C2 | Boost hero value | 270 | 108 | 260 | 110 | centered, `#F0E8FF` |
| C3 | "psi" unit tag | 270 | 222 | 260 | 16 | centered, `#9070C8` |
| C4 | Boost bar — track | 270 | 248 | 260 | 12 | `#1A1830`, rounded ends r=6 |
| C4b | Boost bar — fill | 272 | 250 | 256 | 8 | H gradient `#00F0FF` → `#FF2A6D` |
| C5 | Trigger Errors — label | 300 | 310 | 200 | 14 | centered |
| C6 | Trigger Errors — value | 300 | 330 | 200 | 48 | centered, `#00F0FF` at 0 |
| A1–A6 | Alarm segments FLAT / FAN / LOFUEL / SBFLT / COOLANT P / OIL P | 20 / 148 / 276 / 404 / 532 / 660 | 430 | 120 | 34 | rounded rect r=8 |

## Typography guidance

- Thin and airy. Gauge heights: labels **16px** (uppercase, letter-spaced — pad with
  spaces between characters if needed, e.g. `B O O S T`), column values **44px**
  (~2.75x label), boost hero **110px** (~7x label), status chip text **18px**,
  alarm segment text **16px**.
- Left column: labels + values **left-aligned** at x=32. Right column: **right-aligned**
  to x=768 (mirror symmetry around the center, like OEM cluster tubes). Center hero and
  trigger errors: centered.
- Units in muted purple, either inside the label ("COOLANT P kPa") or as the tiny
  centered "psi" tag under the hero — never at value size.

## Bar gauge treatment

- **Hero boost bar (256x8 fill in a 260x12 track):** horizontal, gradient
  `#00F0FF` → `#FF2A6D` so the fill tip naturally "heats up" toward magenta at high
  boost. Track `#1A1830`. To fake a neon glow with no images, stack a second bar
  behind it: same fill geometry expanded to h=16, same gradient, ~20% alpha
  (e.g. `#003A44` → `#44001C` as pre-multiplied solid equivalents).
- **Mini bars (Throttle, Load; 200x6):** gradient `#00F0FF` → `#B026FF` on track
  `#1A1830`. They double as the row's underline — thin, jewel-like.
- Keep total neon-lit area small; the bars and hairlines *are* the accent budget
  ([DevPalettes: limit neon to 10–15%](https://devpalettes.com/neon-color-palettes/)).

## Warning / critical treatment

- Warning range: the value recolors `#F0E8FF` → `#FCEE0A` and its 1px underline rule
  recolors to `#FCEE0A` (the hairline "wakes up" — quiet, elegant escalation).
- Critical: value `#FF2A6D` + blink-on-alarm on the value text only (not the
  background — the panel stays calm, the number pulses). Underline rule `#FF2A6D`.
- Status chips: OFF = `#14122A` fill, `#9070C8` text, no outline. ON = 1px `#00F0FF`
  outline + `#00F0FF` text.
- Alarm segments (bottom rail): inactive = `#14122A` fill, `#3A3358` text — legible
  ghosts. Active = fill gradient `#FF2A6D` → `#B026FF`, text `#F0E8FF`, blink ON.
  The fixed bottom-edge alarm strip mirrors Audi Virtual Cockpit's fixed warning zone
  ([PRINT Magazine](https://www.printmag.com/branding-identity-design/driven-distraction-dashboard-design-typography/)).

## Sources (Concept 2)

- [Porsche Driver Experience press kit — Porsche DI design language: clear structures, minimalist icons, OLED blacks, three-tube cluster](https://newsroom.porsche.com/en/press-kits/Cayenne-Electric-and-Cayenne-Turbo-Electric/Porsche-Driver-Experience.html)
- [Porsche Taycan interior design — driver-focused, clean minimalist cluster philosophy](https://newsroom.porsche.com/en_US/products/taycan/interior-design-18552.html)
- [PRINT Magazine — Audi Virtual Cockpit typography/design, fixed bottom-edge warning zone](https://www.printmag.com/branding-identity-design/driven-distraction-dashboard-design-typography/)
- [gloam synthwave theme — exact palette rationale (#0D0818 / #F0E8FF / #FF60C8 / #40E8E0 / #9070C8) with contrast ratios](https://github.com/marvinrichter/gloam/blob/main/themes/synthwave/synthwave.md)
- [Cybercore CSS — cyberpunk UI palette (#00F0FF / #FF2A6D / #FCEE0A / #05FFA1 / #0A0A0F)](https://github.com/GasmanDev/cybercore-css)
- [mph synthwave dashboard skill — dark-terminal + neon dashboard rules: thin 1px separators, 4–8px corner rounding, neon reserved for critical data](https://github.com/mphinance/alpha-skills/tree/main/plugins/mph-kit/skills/mph-synthwave-theme)
- [DevPalettes neon color guide — dark background requirement, 10–15% neon budget](https://devpalettes.com/neon-color-palettes/)

---

## Why these two (and how they stay distinct)

| Axis | Existing dash | Concept 1 "STAGE 185" | Concept 2 "MIDNIGHT CIRCUIT" |
|---|---|---|---|
| Background | Flat dark navy | True black `#000000` | Violet-black **gradient** |
| Structure | Tile grid | Chunky outlined boxes + full-width sweep bar | **Boxless** hairline columns, center hero |
| Hierarchy | Uniform tiles | Extreme size contrast (6x hero) | Symmetric OEM "tubes" + thin type |
| Accent | Navy/blue family | Rally yellow `#FFD400` | Neon cyan `#00F0FF` + magenta |
| Alarm feel | — | Whole tile flashes red | Value/hairline pulses magenta |

Additional general references reviewed: [RealDash Project & Dashboard Showcase](https://forum.realdash.net/c/general/project-dashboard-showcase/14),
[RealDash community dashboard sharing](https://forum.realdash.net/t/introducing-my-realdash-community-dashboards/1240),
[Behance instrument-cluster concept search](https://www.behance.net/search/projects/instrument%20cluster%20?locale=en_US),
[Luxury Car Digital Cockpit UI/UX case study](https://alexandresilva.eu/featured_item/luxury-car-digital-cockpit-ui-ux/),
[MoTeC Display Creator upgrade — custom themes/graphics precedent](https://www.motorsportselectronics.com/products/c127-display-creator-upgrade).

# RealDash 1.92 automation reference

Verified on this PC: RealDash 1.92 (UWP, package `Napko.RealDash_tsn2xah6q27qw`, process `RealDash_uwp.exe`), window maximized ~1936x1048, physical screen 1920x1080. All coordinates below are physical screen pixels with `SetProcessDpiAwareness(2)`.

## Screen coordinates (maximized window)

### Run mode
| Target | Coords | Notes |
|---|---|---|
| Reveal top overlay | click (960, 55) | ONE tap; tapping again hides it |
| EDIT button (overlay) | (1835, 90) | enters editor, wait ~2.2 s |
| Dismiss overlay | click (960, 300) | click on dash body |

### Editor
| Target | Coords | Notes |
|---|---|---|
| Menu reveal handle | (960, 40) | menu auto-hides after actions; re-reveal each time |
| FILE | (146, 165) | may need two clicks: first highlights, second opens dropdown. NEVER click a dropdown-row position (e.g. SAVE) without confirming the dropdown is open — the click lands on the canvas and can select/move a gauge |
| ADD GAUGE | (420, 165) | |
| LOOK'N FEEL | (688, 165) | |
| INPUT & VALUES | (960, 165) | or Shift+4 with a gauge selected |
| SETTINGS | (1504, 165) | |
| DONE (exit editor) | (1774, 165) | |
| FILE dropdown: NEW/LOAD/COMBINE/IMPORT/SAVE/SAVE AS | y = 214/270/321/373/427/480 at x≈206 | NEVER click NEW accidentally |
| Load dialog File-name field | (572, 686) | type FULL PATH + Enter (dialog inherits its last-used folder) |
| Gauge-list search box | (218, 265) | clear with End + 20 backspaces first |
| First gauge-list result | (105, 329) | rows ~40 px apart; ordered by PAINT ORDER not number |
| Gauge list w/ top menu HIDDEN | search ≈(116, 141), rows from y≈175 — DISPLAY units | panel sits higher without the menu; physical px ≈ display × 1.875 |
| Save-confirm dialog | ✓ (1187, 727) save · X (733, 727) discard | discard protects disk edits |

### INPUT & VALUES panel
| Target | Coords |
|---|---|
| DONE (commit) | (133, 110) |
| X (cancel) | (1787, 109) |
| SELECT DATA SOURCE button | (527, 362) |
| Category next-arrow (→ channel list) | (1825, 608) |
| Channel search box | (960, 256) |
| First channel result | (608, 354) |
| SELECT INPUT (confirm) | (960, 959) |
| MIN / MAX fields | (302, 358) / (721, 358) |
| WARNING / CRITICAL level fields | (721, 433) / (721, 508) |

Warning/Critical semantics: "EQUAL & ABOVE" the level, plus a separate "BELOW" field. A bit input lights at 1 with warn 0.5 / crit 0.7. Temps that read −50 °C offline need the BELOW fields pushed to −99 to avoid false alarms.

### LOOK'N FEEL
- Submenus at x≈163: DASH PAGE (255) / IMAGES (345) / COLORS (437) / SHADOWS (528) / FONT & TEXT (617) / SPECIAL (708). Back arrow (86, 116).
- FONT & TEXT: DECIMAL PLACES field (1048, 587); also Static Text toggle, leading zeros, refresh delay, multiline.
- COLORS: pick Background/Text/etc. at left; RGBA + HEX fields at center; **Editing Level** selector bottom-left (gear, (265, 955)) — set level BEFORE editing, "All" overwrites every level.

## Keyboard shortcuts (official)

| Keys | Action |
|---|---|
| Shift+6 | enter edit mode (from run mode) — sometimes opens the dash GALLERY instead; recover: back-arrow (44,63) → overlay → EDIT |
| Space | toggle top menu |
| Shift+1…7 | File / Add Gauge / Look'n Feel / Input & Values / Dash Info / Settings / Exit edit |
| Tab / Shift+Tab | next / previous gauge |
| Ctrl+A | select all · Ctrl+F freeze · Shift+Ctrl+F unfreeze |
| Arrows / Shift+Arrows | move / resize (Shift+Ctrl+Arrows resize around center) |
| Ctrl+H / K / U / M | align left / right / top / bottom |
| Ctrl+J | space evenly · Ctrl+1/2/3 center/center-H/center-V |
| Ctrl+7 | same size · Ctrl+6 same size AND position |
| Ctrl+Q / Shift+Q | copy gauge area / position (normalized 0–1) to clipboard |
| Del / Shift+Del | delete gauge / delete page · Ctrl+Z undo |
| Ctrl+S / Ctrl+O | save / load · Ctrl+R rename gauge · Ctrl+E toggle edit bar |
| Numpad +/− | z-order · F4 fullscreen · F9 screenshot · F2 reload app |

Caveat: keyboard shortcuts are swallowed while the gauge-list search box has focus; click a list row first. `pyautogui.hotkey()` also gets swallowed — use `keyDown('shift') + press(n) + keyUp('shift')` after clicking a gauge-list ROW. The editor menu auto-hides fast: the menu reveal (960,40) and the menu-item click must run in the SAME script with ~0.8 s gap.

## Binary .rd format (as decoded by tools/rd_lib2.py — use Dash2/G2)

- Record marker: `<u16 type> BD 0C`. Types: 1=Needle, 2=Text, 3=Bar, 5=Image (also Indicator Light), 8=Arc, 12=Graph.
- Header: canvas 1920x1000 units @0x34/0x38. Plain-text dashes: bg ARGB @0x8A, count u32 @0xAA. **General rule (works with embedded assets too): gauge count = LAST u32 of the header; canvas bg = header_end−36.** Image assets live in the header as lpUTF16 name + u32 size + PNG blob. Footer: 46 bytes.

### Header asset table (general format, decoded round 4)

- u32 `asset_count` at **ver_end+36** (36 bytes after the end of the `2.4.1` version lpstr), then `asset_count` typed blocks back-to-back:
  - **tag=5 (font):** u32 5, lpstr filename (e.g. `RaceHead.ttf`), u32 data_size, 24 B meta (u32 0, u32 1, u32 0x46, u32 1, f32 1.0, u32 0), then the RAW UNMODIFIED TTF/OTF bytes (data_size = exact source file length; verified byte-identical for RaceHead, 51776 B).
  - **tag=0 (image):** u32 0, lpstr name, u32 size, then 4-byte zero pad + PNG (size includes the pad).
- Font blocks sit BEFORE image blocks. After the last asset the original header tail follows (u32 1, f32, canvas bg, gauge count).
- **Binary font splice (B2-proven, zero GUI import needed on any donor):** insert tag=5 blocks right after `asset_count`, bump the count (6→9 proven on the asset-donor template; needle/arc image assets survive the header edit). Blocks may be copied verbatim from any font-carrying .rd — `b1_v7_guiphase.rd`: RaceHead @118..51954, Aerospace @51954..101824, Draco @101824..125066. Dump a header asset table with `tools/b2_hdr_dump.py`.

### Gauge records

- Record skeleton (all types): lpstr name; [type-2: u32 0x40000002, 0, 0 / others: f32 2.0, 0, (optional image lpstr)]; u32 `0x11` rect anchor; rect1 4×f32 + rect2 4×f32 normalized to 800x480 (write both, except type 5 where the second slot is UV data); `$#V2#$`; font lpstr (may be empty); main text lpstr; text color @textEnd+4; stored font size f32 @textEnd+0x28 (metadata only — rendering auto-fits to rect height); **gauge-math lpstr @textEnd+0x74** (empty by default; e.g. `=V/1000`); 3 state strings @textEnd+0x78 (empty strings for non-text types — same layout).
- **Gauge math**: writing the @textEnd+0x74 string re-splices the record and shifts all later offsets — `G2.set_gauge_math()` must run BEFORE any other writes to that gauge. GUI path: INPUT & VALUES gauge-math field. Proven sample: `probe_gm.rd`, "Text Gauge 40" (=V/1000 → turbo "NNN k" with decimals 0). Works on NEEDLE records and needle CLONES too (de-zeroed dial scales — set it as the first write after cloning). **Warn/crit thresholds compare the POST-math display value** (turbo: ranges 0/255, warn 180 / crit 190 — 182 rendered amber in sim).
- **Fonts per gauge (round 4)**: the font lpstr right after `$#V2#$` (`G2.font`) = the asset FILENAME (default `defaultdashfont`) — but setting it alone does NOTHING at render time. The renderer reads **THREE per-level font lp-strings at `arr_marker+4+128+12`** (after the 4 color groups) — use `G2.set_level_fonts('RaceHead.ttf')`. Both writes are re-splices (shift later offsets — write early, like gauge math). An in-app save STRIPS font strings the renderer didn't accept, silently reverting them. Em-size still = gauge rect height.
- **Static-text flag**: u32 @statesEnd+76 (walk the 3 state strings from `_states_off()`, then +76). `0x20400000` = Static Text ON → a bound gauge FREEZES at its baked text; `0x00400000` = live. `probe_base.rd`'s text gauges ship static=ON — any dash rebuilt from that donor must clear bit `0x20000000` on every bound value gauge (see `round3_v5.py:set_static_text`).
- After state strings +4: `u32 0x10, f critBelow, f critAbove, f warnBelow, f warnAbove, f min, f max, f current` (this u32 0x10 = the "range anchor", `G2._range_off()`).
- **Blink Speed**: 3 consecutive f32 @rangeAnchor+40/+44/+48 = Normal/Warning/Critical blink. GUI "500 ms" saves **1.0** (unit unclear; 1.0 = comfortable alarm rate). `struct.pack_into('<f', g.b, g._range_off()+48, 1.0)` makes a critical-level gauge blink. Found via GUI probe byte-diff (probe_blink_base.rd vs probe_blink.rd).
- Binding hash u32 @arrayMarker−12 (`FFFFFFFF` = unbound; small ints = built-in target IDs; ECU-specific names use an unknown hash — NOT CRC32/FNV/djb2/etc., so **bindings can only be created in the GUI or copied from an already-bound gauge**; harvest all known hashes with `rd_fields.py`). Harvest workflow: bind via GUI on a THROWAWAY copy → FILE→SAVE → read the hash. Harvested round 4: `ST185: TC Intervention` = **0x5A59FBBD**.
- Decimal places u32 @arrayMarker−8.
- Color groups after u32 `0x01020304`: n × (u32 1, u32 flag, 6×ARGB). Group0 = background, group1 = image blend, group2 = text. Slots = [normal, warning, critical] ×2; flag 1 = "use dynamic color range" (c1→c2 value gradient — handy for 0/1 bit chips), flag 0 = static per-level. Bar/arc/graph default fill triad `FF46FF64/FFFFAA46/FFFF4664` (green/amber/red) appears in several places — restyle with `G2.replace_level_colors()`.
- Colors are ARGB u32 little-endian (bytes on disk: B,G,R,A).
- Paint order = record order. **Render limit (refined round 4): keep ACTIVE records at index ≤ 119** — a text record at tail index 120 rendered nothing (v1 A/C word); last two records = inert transparent pads.
- **App re-save rewrites everything**: FILE→SAVE in the app re-serializes all records (offsets/lengths change) and normalizes: it truncated a 127-record text dash to 122 and a later save dropped the 2 inert pads (122→120); but on a 128-record image dash, GUI ADD GAUGE ×3 + save did **not** truncate (131 records — pads + parked Image Gauge intact, binary edits survived the re-serialize). Truncation is not universal; still, never in-app-save a binarily built dash you intend to keep byte-editing — do GUI probes on throwaway copies and always re-parse after any in-app save. A save also strips unaccepted binary font strings (see Fonts per gauge) and migrates the asset-name→id map tail to the LAST record.

## Image-type gauges: hard-won constraints (each verified by experiment)

- **Assets**: adding needle/arc/bar/graph/indicator types via GUI embeds PNGs in the header (`roundface.png`, `needle.png`, `arc.png`, `arc_indicator.png`, `_indicators.png_`, `default_image.png`; ~345 KB). Binary building requires a donor file that already has them: `_build\backup\asset_donor_template.rd`.
- **Asset splice recipe**: each header asset = lpstr(name) + u32 size + blob, where blob = `00 00 00 00` + PNG bytes (the 4-byte prefix is included in size). Splicing a different-size PNG over an existing asset (e.g. `_indicators.png_`) works. All six assets end `AE 42 60 82` + u32 flag (1 on the last asset, 0 on the others) — leave those flags alone.
- **Record order (revised twice)**: image-first paint order WORKS on spliced donors — [Image Gauge (bg), texts, bar, parked image types] renders fine; the old "image record before text kills everything after" symptom was actually poisoned subframe writes (below). BUT round 4 (B1): a **GUI-added** Image gauge on the v1-derived font donor DID kill every text record painted after it — donor-dependent. With GUI-added image gauges use [texts…, Image gauge, inert pads] and verify. The asset-name→id map tail stays INSIDE the Image Gauge record wherever that record sits; splitting it off blanks the whole dash; on an in-app save the tail migrates to whichever record is LAST (binary re-orders keep working if the Image gauge record carries it). A bar placed after parked image types did not render — keep visible bars before the parked image records.
- **Subframe fields are POISON to write** (image-type records): u32 @rectAnchor+72 (subframe index, 1-BASED) and u32s @textEnd+104/+108 (grid X/Y counts). Writing ANY of them — even "safe-looking" values — blanks the record and every record painted after it → black dash (probe4/probe6/probe8 bisects).
- **Subframes are STATIC on 1.92** (B1 verdict): even a GUI-configured subframe grid (1x12) bound to a channel never frame-animates — SUBFRAME=0 clamps to frame 1; value-driven frame selection needs the 2.4.7+ XML dash system. Progressive LED strip recipe: ship frame 1 = unlit rail art, overlay threshold-lit lens records per cell (v7: 9 cells, thresholds k*6.25% etc.). Custom art maps 1:1 onto the gauge rect (stretch fill, no letterbox): overlay_x = rect_x + art_px × (rect_w/art_w).
- **Image gauge safe writes** (reconfirmed round 4): `set_rect_px` (rect1 only) + arr1 blend colors + hash/ranges/decimals. Set arr1 to static white ×6 flag=0 to kill the default green/amber/red level tint on custom art; or use arr1 flag=0 `[white/amber/red]` + a binding for per-level STATE RECOLOR of custom art (v8 badge on TC Intervention, sim-verified).
- **Needle/dial facts (A2/B2)**: arr2 colors the scale LABELS on needle gauges; arr1 tints roundface+bezel; the needle sprite's color is BAKED in `needle.png` — splice a recolored PNG to change it. `roundface.png` is 972x972 RGBA — repaint to bake majors/minors/red bands; a fully TRANSPARENT repaint = hidden-bezel floating dial (needle + scale render fine over bare canvas). autoscale maxdig=0 HIDES all scale digits (safe +52 write). Text records painted AFTER needle/arc/graph/bar records DO render (in-dial captions; tail-index gotcha didn't bite at idx 125/128 on an image dash).
- **Stuck-subframe workaround (full-canvas background art)**: the donor Image Gauge 1 (Indicator Light) permanently samples subframe 9 of a 9x6 grid = UV window u 0.875..1.0, v 0..0.125 of its texture (confirmed with a labeled calibration sheet). It cannot be retargeted (see poison above; writing the +36 UV quad is harmless but ignored for the crop origin). Fix: ship a **6400x3840 sheet PNG whose window region x5600..6400, y0..480 IS the 800x480 art**, with ~8 px edge extension to pad against filter bleed (`tools\gen_cf_png.py` writes both the 800x480 art and the shipping cf_sheet.png). Safe writes on the type-5 record: `set_rect_px` (rect1) + identity UV @rectAnchor+20, arr1 blend colors, hash, ranges, decimals.
- **Cloning**: needle clones render fine. Arc clones NEVER render (silently invisible). **Bar/Graph/Image clones hang the loader in the splash crash-loop — never clone; one instance each.**
- **Autoscale block** (needle/arc; locate via float pattern `0.75, 1.0, 1.0`, offset = match−4): `+0` size_scale f32, `+44` segments u32 (count includes the 0 label: segments=11 on 0–100 → 0,10..100), `+52` MAX DIGITS u32, `+56` use_auto u32. **Never write +40 or +56 on image-type records** — the record's extras desync and every image record painted after it goes blank (this is also why use_auto=False "worked" on a lone arc but blanked the needles painted after it).
- **MAX DIGITS truncates labels to N leading characters** (root cause of a user-reported bug: maxdig=1 rendered dial labels 10/12/14/16/18 as "1"). There is no shared divisor across labels, so mixed-magnitude scales (0–200000) need full width (maxdig=6) or few majors (segments=5 → 0/50000/100000/150000/200000).
- Bars and graphs render nothing at value 0 (offline): put a track-colored text panel behind bars; graphs need live data to show a trace.
- Indicator Light (GUI) = Image gauge using the `_indicators.png_` symbol sheet; the ADD flow opens a full-screen symbol picker (choose symbol, then DONE top-left (133,110)). Appear-on-alarm: group1 (image blend) flag=0 with transparent normal + colored warning/critical.
- Needle/arc angles: two consecutive f32 radians (start≈3.9, sweep≈4.7 defaults) — `G2.set_angles()` finds them by value pattern.

## ADD GAUGE menu (editor, physical px)

- Open reliably with **Shift+2** (avoids the top-menu reveal/hide toggle race; use `tools/probe_kb.py`).
- Dropdown rows at x≈536: INDICATORS 214 / COMPONENTS 268 / DATE&TIME 321 / UI 373 / GRAPH 428 / MAP 481 / IMAGE 534 / TEXT 586 / VIDEO 641.
- INDICATORS flyout at x≈1018: NEEDLE 231 / ARC 283 / AXIS 330 / BAR 379 / INDICATOR BAR 428 / INDICATOR CLUSTER 476 / INDICATOR LIGHT 525.
- **Esc in the editor opens the exit/save prompt** — do not use Esc to close dropdowns; click empty canvas instead.
- New gauges land ~center canvas named `<Type> Gauge 1`; learn their binary format via: add via GUI → FILE→SAVE → parse/diff offline (the "GUI probe" workflow that produced everything in this file).

## Crash recovery (loader hang)

Symptom: endless cycling progress bar on a black screen; survives app restart (startup restores the same dash file).
1. `taskkill /IM RealDash_uwp.exe /F`
2. Replace the offending `.rd` (same path/filename) with a known-good backup.
3. Relaunch: `explorer.exe "shell:appsFolder\Napko.RealDash_tsn2xah6q27qw!App"` — startup takes 30–60 s.
4. Rebuild the edit from the backup with a script instead of re-tweaking the broken file.

## GUI workflows (step lists)

**Load a dash:** run `python tools/load_dash.py <FULL-PATH.rd> <shot.png>` — **always pass the full path**: the UWP dialog inherits its last-used folder (e.g. `Downloads\catch` after font imports), so a bare filename can land in the wrong folder. It does: overlay → EDIT → FILE → LOAD → type path → Enter → DONE → screenshot.

**Audit a gauge's binding:** `python tools/audit_gauge.py "Text Gauge N" [close]` — selects via list search, opens INPUT & VALUES (Shift+4), screenshots to `_build\shots\iv_Text_Gauge_N.png`. `close` first X-closes a previously open panel (X = cancel, safe for read-only audits).

**Rebind a gauge:** select gauge → Shift+4 → SELECT DATA SOURCE → ECU SPECIFIC → next-arrow → search → click result → SELECT INPUT → **DONE (not X)** → FILE → SAVE → confirm LastWriteTime changed.

**Discover an unknown binary field:** snapshot the `.rd`, change exactly one property in the GUI, FILE → SAVE, byte-diff old vs new (align around string-length changes). This is how decimals, ranges, color semantics, gauge math, blink, and the static-text flag were found. **Do this on a throwaway copy** — the in-app save truncates/re-serializes the file.

**Verify with simulation mode:** toggle via top menu → SETTINGS → data source → connections/simulation. Sim cycles all bound values (~19 s full cycle). Animations/blink cannot be judged from one frame — burst-capture 8–10 screenshots over ~4 s and read 2–3; rare peak states (WOT ≥85% throttle) need ~26 frames at 0.8 s spacing. CORRECTED round 4: sim DOES sweep the FLAT/FAN bit channels 0→1 on 1.92 (old "never raises them" note was wrong). ROUND 5: **sim sweeps bit channels as continuous ANALOG ramps**, not clean 0/1 steps — flag=1 gradient fills therefore fade smoothly in sim (looks like strobing); flag=0 static per-level pills snap hard on/off. Sampling one pixel per frame across a burst (`tools/burst.py` + PIL getpixel) beats eyeballing. But a sim channel can be stuck at 0 for a whole session (ST185 Turbo Speed, two sessions running, then revived) — cross-check against a proven byte-identical recipe on another dash before blaming your build.

**Import a font (GUI, physical px, maximized):** select a text gauge → LOOK'N FEEL (688,165) → FONT & TEXT (163,617) → SELECT FONT button (881,111) → SELECT ASSET screen. The "+" tile opens a Win32 Open dialog (filter *.ttf/*.otf): File-name field (572,686), clear with End + backspaces, type the FULL path, Enter. The font becomes a tile (preview rendered in its own face); click the tile → DONE checkmark (133,110) applies it to the selected gauge. Tile slot centers ≈ (240,300), (720,300), (1198,300), (1678,300), wrapping to y≈585; the "+" shifts RIGHT as fonts accumulate (new fonts insert at slot 0). **TRAP (cost 20 min):** clicking with PREVIEW-image coords instead of physical px silently closes SELECT ASSET and looks like a broken importer — it isn't; no app restart needed. No importer crash on RaceHead.ttf / Aerospace.ttf / Draco.otf. Requires an in-app save to embed — do it on a donor BEFORE byte-editing (or skip the GUI entirely with the binary font splice above).

## Recipes proven in production dashes

- **Steady status pill (FAN) — RE-CORRECTED round 5; the round-4 flag=1 recipe strobes in sim**: a flag=1 "dynamic color range" bg **lerps off→lit with the channel VALUE**; sim sweeps bit channels as continuous analog 0→1→0 ramps, so a flag=1 pill FADES cyclically (~1.6 s apparent period) — this was the user-reported "FAN strobing" (isolated round 5 with a 3-way probe: flag=0 pill solid, flag=1 control pulsing, crit-window change irrelevant). Correct recipe (permanent, applied to all ten dashes): bit-bound text gauge, **bg group flag=0 STATIC `[off, lit, lit]`**, min 0 / max 1, `warn 0.5 / crit 0.7 / below 0`, **all 3 blink slots (@rangeAnchor+40/44/48) = 0 at every level** → hard off below 0.5, hard steady lit above; sim-burst-verified (consecutive identical lit frames). Per the round-5 permanent convention, status pills do NOT use blink at all; **zero the blink slots on every repurposed record** — round-3 halo/crit records carry critical blink=1.0 (`tools/r5_zero_blinks.py` audits+zeros a whole dash set; `r5_fan_flag0.py` converts FAN groups to flag=0).
- **Turbo "NNN k" readout**: `set_gauge_math("=V/1000")` FIRST, decimals 0, ranges 0/255 (warn 180 / crit 190 — thresholds compare the POST-math display value), label "Turbo", dim "k RPM" unit chip parked beside the value. (Matches the CAN encoding: turbo speed is 1 byte = thousands of RPM with conversion V*1000, so =V/1000 shows exactly the transmitted resolution.) Hardware fact: BorgWarner EFR 7163 max shaft speed = 150,000 rpm (official datasheet) → dial max 160k, red band 150–160k.
- **De-zeroed turbo dial (v4/v9/v10)**: `set_gauge_math("=V/1000")` on the NEEDLE record (first write; works on clones), min 0 / max 160, segments=5 maxdig=3 → labels 0/40/80/120/160, warn 140 / crit 150, red band 150–160k baked into the repainted face, "TURBO k RPM" caption as a text record painted after the needle.
- **Aspect compensation — ALL round gauges (round 5, mandatory)**: the design canvas renders at exactly **1920x1000 px** (the header canvas units at 0x34/0x38; scale-to-fit preserves the ratio on other windows), so per-axis scales are x 2.4 / y 2.0833 px per 800x480 design unit and any square design rect renders 1.152x wider than tall. **Formula: `h_design = K × w_design`, K = (1920/800)/(1000/480) = 1.152**, resize around the fixed center (`cx,cy` preserved). Applies to needle dials, arc gauges, AND anything circular baked in face art (the face texture stretch-fills the rect). Tick rings placed as satellite records need elliptical placement in design units: `x = cx + r·cos(θ)`, `y = cy − r·K·sin(θ)`. **Measure-adjust-verify**: splice a full-bleed magenta disc over `roundface.png` on a throwaway copy (`tools/r5_calib_probe.py`), load, measure the disc's pixel bbox (must be square, e.g. 648x648 ratio 1.0000 on v10); do NOT measure from white tick extremes — majors at 157.5°/22.5° give bogus ratios (a wrong 1.708 cost an iteration in round 5).
- **Threshold-lit tick LINES (v4, round 5 — replaces the round-4 square dots)**: hide in-arc digits (maxdig=0); each tick = a tiny (~9 design px) text record rendering an ASCII glyph `- / | \` chosen nearest the tick's radial angle (box-drawing U+2500/2571/2502/2572 render as "?" — defaultdashfont lacks them), text-color group flag=0 `[dim, lit, red]`, bound to the arc's channel with `warn = tick value` (crit = max(tick, arc crit)) → each line lights as the value passes it, red in critical. Recipe in `tools/r5_fix_v4.py`.
- **Graph warning shading (v9)**: `replace_level_colors()` + finite warn/crit ranges on a graph record → trace segments recolor above thresholds (cyan/amber/red, sim-verified).
- **Imported-art badge (v8)**: crop the mark from source art, luminance→alpha (white-on-transparent), splice over an existing sheet asset as frame 1 of the same grid (`b2_badge_gen.py`); optional per-level recolor via arr1 flag=0 `[white/amber/red]` + a binding (TC Intervention).
- **Progressive LED strip (v7)**: subframes are static (see above) — embed the sheet, show frame 1 = unlit rail art, overlay 9 threshold-lit lens records at the cell positions mapped through rect/art scale. Sheet: `_build\assets\led_strip_sheet_1x12.png` (1476x2040, cells at y 48–120 per frame).
- **Label/unit convention**: units live in a dim chip gauge next to the value readout, never inside the measurement-name label ("COOLANT P" + "kPa" chip, "CHARGE TEMP" + "°C" chip); `%` may stay in labels ("ETHANOL %"). Chips are cheap: repurpose parked/underline records.
- **Pillow-baked background (Carbon Forge, v5)**: generate the whole dark skin in Pillow — 2/2 twill carbon weave (6 px tows), recessed panel wells per tile, brushed-aluminum strip, bar track well, gunmetal pill housings — output both the 800x480 art and the 6400x3840 sheet (art in the stuck-UV window), splice the sheet over `_indicators.png_`, rebuild the dash from the `probe_base.rd` donor (clear static-text bits!), lay live gauges over the baked wells. See `tools\gen_cf_png.py` + `tools\round3_v5.py`.
- **3D indicator pill**: baked housing + machined bezel in the background PNG; on top, a fill-gauge "lens" (dynamic bg off→lit), a gloss glass layer record, and a glow halo record. Critical pills get real blink via the binary blink field (@rangeAnchor+48 = 1.0); constant-run bits use the steady recipe. Verified to read as physical lamps in zoomed screenshots.
- **Missing-label postmortem (v2 top strip)**: outlined boxes with no text were decorative sweep-bar segments that never had label records. Fix binarily: repurpose parked records into labels ("THROTTLE SWEEP / 25 / 50 / 75 / WOT") and optionally bind the track panel to a channel with a flag=1 bg gradient for a live glow. When a gauge shows a box but no text, check text content and text-color group first, then whether the record index exceeds the render limit.
- **File-name dialog typeahead**: the field is pre-filled — clear with `End` + ~40 backspaces before typing (Ctrl+A is unreliable in the UWP dialog); a wrong name pops a "File not found" modal (OK ≈ (1082,533)).
- **Desync recovery**: if a load script fires while the app is already in the editor, the click sequence lands wrong. Screenshot first, then recover: reveal menu → DONE (1774,165) → discard prompt X (733,727) → rerun `load_dash.py` from run mode.

## Environment facts

- Temperature display unit is an app setting (editor SETTINGS → UNITS & VALUES → TEMPERATURE UNITS), not per-gauge; keep it Celsius to match `units="C"` channels.
- Default value gauges show `0`/baked text offline; enum channels show nothing until CAN data arrives.
- RealDash storage root on this PC: `C:\projects\st185-link-ecu-config\rd-build\realdash-root\`.
- Python deps: `pyautogui`, `pygetwindow`, `Pillow` (see `tools/requirements.txt`).
- Console printing of λ/° chars needs `python -X utf8`.

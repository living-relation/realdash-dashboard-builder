---
name: realdash-dashboard-builder
description: Build, edit, restyle, and verify RealDash 1.92 dashboards on this Windows PC using PyAutoGUI automation and a direct binary .rd editing pipeline. Use when creating or editing RealDash dashboards or .rd files, binding Link G4X / ECU-specific CAN channels, styling gauges, embedding custom TTF/OTF fonts, setting warning/critical levels, or batch-producing dashboard variants.
---

# RealDash Dashboard Builder (Windows, RealDash 1.92)

Drives the RealDash 1.92 UWP app (window ~1936x1048 maximized) to create, edit, and verify dashboards, and edits `.rd` dashboard files directly at the byte level when that is faster and safer than GUI automation. All coordinates, offsets, and binary field maps live in [reference.md](reference.md) — read it before doing real work.

## When to use

- Creating/editing/styling RealDash dashboards on this PC.
- Binding gauges to Link G4X / ECU-specific CAN channels.
- Batch-producing dash variants (restyle a base `.rd` into new files).
- Beware: a separate RealDash 5.3 instance may be running — only ever touch the window titled "RealDash 1.92".

## Control pipeline

1. Run Python scripts (Python + PyAutoGUI) via the shell or Desktop Commander MCP `start_process`.
2. Every script must start with `ctypes.windll.shcore.SetProcessDpiAwareness(2)` and re-foreground the "RealDash 1.92" window (`pygetwindow` + `SetForegroundWindow`) before any input.
3. **One action → screenshot → read the screenshot → next action.** Batched blind clicks misfire (menus auto-hide, focus shifts). Screenshots go to `_build/shots/`.
4. Prefer the existing tools in `tools/` (see Key files) over writing new automation from scratch.

## Choose the right editing method

**Binary `.rd` editing (preferred)** for: geometry, colors, text, font size, decimals, ranges/thresholds, cloning gauges, reordering paint order, producing variants. Deterministic, fast, no focus problems.

**GUI automation (required)** for: binding/rebinding data sources (channel-name hashes are not computable), adding brand-new gauge types, app settings (units), and discovering unknown binary fields (edit one property in the GUI, save, byte-diff).

## Binary .rd pipeline

`.rd` files are proprietary binary: header + length-prefixed UTF-16LE strings + packed floats/ARGB colors. **Use `tools/rd_lib2.py` (`Dash2`/`G2`) — it handles ALL gauge types** (record marker is `<u16 type> BD 0C`: 1=needle 2=text 3=bar 5=image 8=arc 12=graph) and asset-carrying headers. `tools/rd_lib.py`/`rd_edit.py` are older text-gauge-only equivalents. Worked examples: `build_v1/v2/v3.py` (text-tile dashes), `build_v4/v5.py` (needle/arc/bar/graph/image dashes); round 4: `r4_v7.py` (custom fonts + LED rail), `b2_v8.py` (imported-art badge + staircase sweep), `b2_v9.py` (binary font splice + hidden-bezel dials), `a2_v4_build.py` (dial repaint + tick dots).

Rules:
- **ALWAYS back up the `.rd` first** (copy to `_build\backup\` with a timestamp).
- Keep the record count/shape proven to load. Render limit (refined round 4): a text record at tail index 120 rendered NOTHING — keep **active records at index ≤ 119** and the last two records inert transparent pads. In-app FILE→SAVE re-serializes every record and normalizes the file: on text dashes it truncated 127→122 records and a later save dropped the 2 inert pads (122→120); on a 128-record image dash, GUI ADD GAUGE ×3 + save did **not** truncate (131 records, binary edits survived) — truncation is not universal, but **never in-app-save a binarily built dash you intend to keep byte-editing** without re-parsing; use throwaway copies for GUI probes.
- Verify every edit by reloading in RealDash and reading a screenshot. If a "Dash is not saved. Save dash?" prompt appears, **discard** (X) so the app doesn't clobber disk edits.
- **Gauge math** (e.g. `=V/1000` for a turbo "NNN k" readout): the binary slot is an empty lp-string at `text_end+0x74`; `G2.set_gauge_math()` re-splices the record and shifts every later offset, so **call it before any other writes to that gauge**. GUI equivalent: INPUT & VALUES → gauge math field (proven sample: `probe_gm.rd`, Text Gauge 40).
- Rebuilding from the `probe_base.rd` donor: its text gauges ship with Static Text ON — clear bit `0x20000000` in the u32 at `states_end+76` on every bound value gauge, or they freeze at their baked text (see [reference.md](reference.md)).
- Text em-size = gauge rect height. Change font size by changing rect height, never by the stored font-size float (it is metadata only).
- One malformed record can stop the renderer for everything painted after it, and some malformed image-type records **hang the loader in an infinite splash loop** — see recovery in [reference.md](reference.md).

## Image-type gauges (needle / arc / bar / graph / indicator light)

The ADD GAUGE menu offers: INDICATORS > (Needle, Arc, Axis, Bar, Indicator Bar, Indicator Cluster, Indicator Light), plus Graph/Map/Image/Text/Video gauges. Adding any image-bearing type embeds its PNG assets (~345 KB: roundface/needle/arc/arc_indicator/_indicators_ sheet) into the header. To use these types binarily, start from the asset donor `_build\backup\asset_donor_template.rd` (one GUI-added instance of each type, saved). Hard rules learned by experiment — violating them blanks gauges or hangs the app:

- **Record order:** image-first paint order works on SPLICED donors (proven: [bg Image Gauge, texts, bar, parked image types]). Round-4 counterexample: a **GUI-added** Image gauge killed every text record painted after it on that donor — the hazard is donor-dependent. With GUI-added image gauges use [texts…, Image gauge, inert pads] and verify. The asset-name→id map tail stays INSIDE the Image Gauge record wherever it sits (splitting it off blanks the whole dash); on an in-app save the tail migrates to whichever record is LAST — binary re-orders keep working as long as the Image gauge record carries it.
- **Subframe fields are POISON:** never write u32 `rect_anchor+72` (1-based subframe index) or u32s `text_end+104/+108` (grid X/Y counts) on an image-type record — any write, even "safe-looking" values, blanks that record and everything painted after it.
- **Subframes are STATIC on 1.92** — even GUI-configured subframe grids bound to a channel never frame-animate (SUBFRAME=0 clamps to frame 1); value-driven frame selection needs the 2.4.7+ XML dash system. Progressive LED strips: ship frame 1 as unlit rail art and light the cells with threshold-lit lens records painted on top (proven, v7).
- **Per-level recolor of custom art:** arr1 (Image Blend) flag=0 colors + binding/ranges on the type-5 record recolor spliced art per level (v8 badge: white/amber/red on TC Intervention). Custom art maps 1:1 onto the gauge rect (stretch fill, no letterbox): overlay_x = rect_x + art_px × (rect_w/art_w).
- **Dial styling (round 4):** gauge math (`=V/1000`) works on NEEDLE records and their clones → de-zeroed "k" scales (`set_gauge_math` must be the FIRST write); autoscale maxdig=0 hides scale digits entirely; arr2 colors the scale LABELS, arr1 tints face+bezel, the needle sprite's color is BAKED in `needle.png` (splice a recolored PNG); repaint `roundface.png` (972x972 RGBA) to bake majors/red bands — a transparent repaint gives a hidden-bezel "floating" dial; replace tiny in-arc numbers with threshold-lit tick marks outside the ring. Text records painted AFTER image-type records DO render (in-dial captions work).
- **ROUND gauges must be aspect-compensated (round 5, MANDATORY for every dial/arc):** the 800x480 design canvas renders at exactly **1920x1000 px** (the header canvas units), so x-scale 2.4 ≠ y-scale 2.0833 and a square design rect renders as a wide ellipse (the round-5 user complaint). **Set `h_design = K × w_design` with K = (1920/800)/(1000/480) = 1.152**, keeping the center fixed. Full measure-adjust-verify procedure in [reference.md](reference.md).
- **Embedded background art (stuck-UV workaround):** donor image gauges permanently sample one subframe of a 9x6 grid and cannot be retargeted. Ship a **6400x3840 sheet PNG whose sampled window IS the 800x480 art** instead — full recipe and the header asset-splice format are in [reference.md](reference.md).
- **Cloning:** needle clones render fine; arc clones silently never render; **bar/graph/image clones hang the loader — never clone them** (one instance each per dash).
- **Autoscale block:** only `segments` (+44) and `maxdig` (+52) are safe to write. Writing +40 or +56 (`use_auto`) on any image-type record blanks every image record painted after it.
- **Scale labels truncate to `maxdig` leading characters** — maxdig=1 renders 10/12/14 as "1" (a real user-reported bug). Keep maxdig ≥ the widest label; labels share no divisor, so mixed-magnitude scales need full-width maxdig (e.g. 6 for 0–200000).
- Bars/graphs are invisible at value 0 offline; put a track panel behind bars. Indicator Light = an Image gauge + symbol picker; make it appear-on-alarm via per-level Image Blend colors.
- Full field maps, menu coordinates, and the GUI probe workflow: [reference.md](reference.md).

## Custom fonts (TTF/OTF)

RealDash embeds imported fonts inside the `.rd` (dev-confirmed) — no font install on the target device. Two ways in:

- **GUI import** on a donor dash: Look'n Feel → Font & Text → SELECT FONT → "+" tile (full click path and a nasty coordinate trap in [reference.md](reference.md)), then in-app save.
- **Binary splice** (round-4 proven, zero GUI): insert tag=5 font blocks into the header asset table and bump the asset count — byte format in [reference.md](reference.md).

THE critical fact: **what renders is the three per-level font lp-strings** — use `G2.set_level_fonts('RaceHead.ttf')`. The post-`$#V2#$` font string alone does NOTHING, and an in-app save silently STRIPS binary font references the renderer didn't accept. Clean donor with RaceHead + Aerospace + Draco embedded: `_build\assets\font_donor_3fonts.rd`. Glyph caveats: Aerospace has no λ and a broken minus glyph (renders a square box); RaceHead is caps-only — keep λ labels, unit chips, and negative-capable values on defaultdashfont or RaceHead/Draco (both have a real minus). Font size is still rect height.

## App interaction rules (hard-won)

- Run-mode top menu: ONE tap near top of screen (y≈55) shows it; tapping again hides it. Menu also auto-hides after actions — re-reveal before each menu click.
- **Never FILE → NEW** when a dash should be edited.
- Editor top menu: FILE / ADD GAUGE / LOOK'N FEEL / INPUT & VALUES / INFO / SETTINGS / DONE.
- Saving: Ctrl+S silently fails when the left gauge list has keyboard focus — prefer FILE → SAVE clicks, then **verify the file's LastWriteTime changed**.
- Save-confirm dialog: checkmark ≈ (1187,727) saves; X ≈ (733,727) discards.
- Loading: FILE → LOAD → type the **FULL PATH** into the dialog's File-name field → Enter. The dialog inherits its last-used folder (e.g. `Downloads\catch` after font imports), so a bare filename can silently miss. Keep working `.rd` copies in `C:\Users\danie\Downloads`; `tools/load_dash.py <full-path.rd> <shot.png>` does the whole load-and-screenshot loop.
- PyAutoGUI robustness: `pyautogui.hotkey()` gets swallowed — use `keyDown('shift')+press(n)+keyUp('shift')` after clicking a gauge-list ROW. The editor menu auto-hides fast: the menu reveal (960,40) and the menu-item click must run in the SAME script ~0.8 s apart.
- Left gauge list has a search box; results are ordered by **paint order**, not numerically — "Text Gauge 6" can match "Text Gauge 60" first. Verify the selected gauge via the X/Y/W/H readout.
- INPUT & VALUES panel: top-left DONE commits changes; top-right X cancels them.

## Keyboard shortcuts (prefer over clicking)

Shift+6 enter edit · Shift+1–7 = File/Add Gauge/Look'n Feel/Input & Values/Dash Info/Settings/Exit · Space toggle top menu · Tab/Shift+Tab cycle gauges · Ctrl+Q copy geometry · Del delete · arrows move / Shift+arrows resize · Ctrl+H/K/U/M align L/R/T/B · Ctrl+J space evenly · Ctrl+7 same size · Ctrl+S save · Ctrl+Z undo. Full table in [reference.md](reference.md).

## Styling

- Look'n Feel → Colors: set the **Editing Level** (All/Normal/Warning/Critical) BEFORE adjusting — editing while "All" is selected wipes per-level colors. "Use dynamic color range" turns Color1/Color2 into a value gradient.
- Look'n Feel → Font & Text: Static Text toggle, decimal places, leading zeros; text size = gauge height (see above).
- Bar gauges support gradient fills; blink-on-alarm lives in Look'n Feel → Special → Blink Speed (set per Warning/Critical level, leave Normal 0). Binarily: 3 f32 slots at `range_anchor+40/+44/+48` (Normal/Warning/Critical); 1.0 = comfortable alarm rate (see [reference.md](reference.md)).
- **Label/unit convention (permanent):** units go in a small dim "chip" gauge NEXT TO the value readout, never inside the label that names the measurement — "COOLANT P" label + "kPa" chip, "CHARGE TEMP" + "°C" chip, turbo value + "k" chip. Exception: `%` may stay in labels like "ETHANOL %" / "THROTTLE %".
- Tiles = text gauges with background colors; label/value/unit are separate stacked gauges.
- **Baked-texture backgrounds (Carbon Forge pattern):** for rich dark skins, generate the whole background in Pillow (weave texture, recessed panel wells, brushed strips, track wells, pill housings) as one PNG and splice it into the dash's header assets, then lay live gauges on top. **3D indicator pills** = baked gunmetal housing + machined bezel in the PNG, plus a fill-gauge lens with gloss layer and glow halo records on top — reads as a physical lamp; blink via the binary blink field.
- **Steady (non-blinking) status pill — RE-CORRECTED round 5 (supersedes the round-4 flag=1 recipe):** FAN and other constant-run status pills must NEVER blink — this is a **permanent user-mandated design convention**. Round-5 root cause of observed strobing: a **flag=1 "dynamic color range" bg LERPS off→lit with the channel VALUE**, and sim sweeps bit channels as continuous 0→1→0 analog ramps, so a flag=1 pill fades in and out (~1.6 s period) = visible strobe. Correct recipe for a 0/1 bit: **flag=0 STATIC per-level colors `[off, lit, lit]`** + finite `warn 0.5 / crit 0.7 / below 0` + **all three blink slots 0** → hard off below 0.5, hard steady lit above, in sim and on real CAN. **Audit rule: zero ALL blink slots (`@range_anchor+40/44/48`) at ALL levels on every repurposed record** — round-3 halo/crit records ship critical blink=1.0 (`tools/r5_zero_blinks.py` sweeps a whole dash set).
- **Graph warning shading:** `replace_level_colors()` + finite warn/crit ranges on a graph record — trace segments recolor (e.g. cyan/amber/red) above the thresholds (proven in sim, v9).
- **Design conventions (permanent, user-mandated):** turbo = label "Turbo" + dim "k RPM" chip + `=V/1000` math (thresholds compare the POST-math display value: ranges 0/255, warn 180 / crit 190); CRUISE / A-C = framed lenses with the state WORD rendered inside via the 3 per-level state strings (OFF/STBY/SET/RES/OVR · OFF/REQ/ON/FLT); NO Trigger Error tiles on new dashes; hero gauges only from Turbo "k RPM", Throttle %, Engine Load %; **FAN/status pills never blink** (flag=0 static steady recipe above); **round gauges always aspect-compensated** (h = 1.152×w); arc threshold ticks are thin LINE marks, not square dots (glyph recipe in [reference.md](reference.md)).

## Data accuracy (mandatory before labeling/binding)

1. Parse the CAN channel XML first — e.g. `descfiles/link_g4x_realdash.xml` — for exact channel names, units, conversions, ranges, and enums.
2. Set decimals to what the channel resolves (integer channels → 0 decimals; e.g. lambda ×0.001 → 2).
3. Always show the unit (°C, kPa, RPM, %, λ) — as a dim chip beside the value per the label/unit convention above — and make the app's temperature unit (Settings → UNITS & VALUES) match the XML's `units="C"`.
4. Bind via INPUT & VALUES → Select Data Source → ECU SPECIFIC → search box → channel → SELECT INPUT → DONE. Audit existing bindings with `tools/audit_gauge.py "Text Gauge N"` — bindings have been found silently shuffled before.
5. Binding hashes are not computable — harvest unknown ones with a GUI probe on a THROWAWAY copy (bind → FILE→SAVE → read u32 `@arrayMarker−12`). Harvested so far incl. `ST185: TC Intervention` = `0x5A59FBBD`.
6. Bound gauges ignore baked text at runtime; enum channels render blank until live CAN data arrives.
7. Hardware reference: BorgWarner EFR 7163 max shaft speed = **150,000 rpm** (official datasheet) — turbo dial max 160k with a red band 150–160k.

## Verifying with simulation mode

- Toggle: top menu → SETTINGS → data source → connections/simulation. In simulation mode all bound gauges cycle through their ranges (~19 s full cycle observed), so animations, alarm colors, and blink can be verified without CAN hardware.
- **Burst-capture, don't single-shot:** one screenshot cannot prove motion or blink. Capture 8–10 frames over ~4 s and read 2–3 of them to confirm sweeps/blinks; rare peak states (e.g. WOT ≥85% throttle) need a longer burst (~26 frames at 0.8 s spacing to cover a full sim cycle).
- CORRECTED round 4: sim DOES sweep the FLAT/FAN bit channels 0→1 on 1.92 (the old "sim never raises them" note was wrong) — steady pills can be verified lit in sim. But a sim channel can be stuck for a whole session (ST185 Turbo Speed sat at 0 across all dashes for two sessions, then revived) — before suspecting your dash, compare against a proven byte-identical recipe on another dash.

## Long sessions: keep a progress ledger

For multi-hour automation projects, maintain a ledger file (pattern: `_build\progress_ledger.md`) with a task checklist, discoveries section, environment notes, and an append-only log. **Every agent updates it after each milestone** (flip checkboxes, append terse log lines); successor agents read it first instead of re-deriving state. This is what makes staged/hand-off work survive context exhaustion — two workers died mid-task in round 3 and nothing was lost because the ledger held the byte patterns and app state.

## Key files

| Path | Purpose |
|---|---|
| `tools/` | All automation: `rd_lib2.py` (all gauge types, incl. `set_gauge_math` + `set_level_fonts`), `rd_lib.py`, `build_v1..v5.py`, `round3_*.py` (round-3 rebuilds), round-4 builders `r4_v1/v2/v3/v6/v7.py`, `a2_v4_build.py`/`a2_v5_build.py`, `b2_v8.py`/`b2_v9.py`, round-5 `r5_v10.py`/`r5_v10_it2.py` (v10 builder), `r5_fix_v4.py`/`r5_fix_v9.py` (aspect + line ticks), `r5_zero_blinks.py`/`r5_fan_flag0.py` (never-blink audit), `r5_calib_probe.py`/`r5_calib2.py` (magenta-disc aspect calibration), `burst.py` (sim frame bursts), generators `gen_cf_png.py`/`a2_gen_cf2.py`/`a2_gen_face.py`/`b2_gen_glacier_face.py`/`b2_badge_gen.py`, `b2_hdr_dump.py` (header asset-table dump), `load_dash.py`, `audit_gauge.py`, `probe_kb.py`, `rd_fields.py`, `fix_pills.py` |
| `dashboards/ and/or Downloads/` | The TEN production dashes: `st185_dash.rd` (v1) + `st185_dash_v2..v10.rd`, synced to realdash-root. Also the load-dialog working folder |
| `...\_build\backup\asset_donor_template.rd` | Donor .rd with embedded needle/arc/bar/graph/image assets + one record of each type |
| `...\_build\assets\font_donor_3fonts.rd` | Clean font donor: v1 layout + RaceHead/Aerospace/Draco embedded + per-level refs on TG34/35/36 |
| `...\_build\backup\b1_v7_guiphase.rd` | Post-GUI donor: LED sheet asset + throttle-bound image gauge + 3 fonts (source of verbatim font blocks) |
| `...\_build\assets\carbon\` | 3 seamless CC0/royalty-free carbon-weave textures, 2048² (ShareTextures 45° twill used on v5) |
| `...\_build\assets\imported\` + `manifest.md` | 14 PNGs from user art folders (Corsa/ECU-Master backgrounds, 12-frame LED shift-light strip → `..\led_strip_sheet_1x12.png`) |
| `...\_build\progress_ledger.md` / `progress_ledger_round4.md` / `progress_ledger_round5.md` | Round-3/4/5 progress ledgers (all closed; the staged-agent hand-off pattern) |
| `...\_build\b2_v9_donor.rd` | Ready v10-class donor: asset donor + 3 fonts spliced, 122 text records incl. all standard channel bindings (see r5_v10.py for the map) |
| `...\_build\backup\r4_*probe_gm*.rd` / `r4_*probe_base*.rd` | Archived probes (removed from Downloads in round 4): gauge-math byte-pattern sample / v5 donor (text gauges ship Static Text ON — clear it) |
| `...\_build\research\realdash_procedures.md` / `round4_prep.md` | Sourced app/file-format research / round-4 font+EFR+texture+CAN-channel findings |
| `...\_build\research\design_inspiration.md` | Two fully-specified design concepts (palettes, 800x480 coordinates) |
| `...\_build\shots\` / `...\_build\backup\` | Screenshots / timestamped `.rd` backups |
| `C:\projects\st185-link-ecu-config\rd-build\realdash-root\` | RealDash storage root (synced copies) |

## Additional resources

- Coordinates, shortcut table, binary field map, GUI click paths, crash recovery: [reference.md](reference.md)

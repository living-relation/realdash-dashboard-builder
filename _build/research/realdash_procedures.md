# RealDash Customization Research — Procedures & File Format

Research date: July 6, 2026. Target: RealDash 1.92+ on Windows (findings verified against official manuals, the official RealDash forum, the developer's GitHub (`janimm/RealDash-extras`), and direct inspection of an official `.rd` sample file). Note: forum threads reference RealDash versions up through 2.6.x; the editor menu structure (Look'n Feel / Input & Values / Add Gauge) has been stable across versions.

---

## 1. The .rd dashboard file format

### 1.1 VERDICT: .rd files are proprietary BINARY — hand-editing in a text editor is NOT viable

This was verified two ways:

1. **Direct byte inspection.** The official free `Multiview.rd` dashboard (published by the developer at [janimm/RealDash-extras — Dashboard-animation-examples](https://github.com/janimm/RealDash-extras/blob/master/Dashboard-animation-examples/README.md)) was downloaded and hex-dumped. It begins with a binary header (`06 40 03 00 04 00 00 00 02 00 00 00 09 00 00 00 ...`) followed by UTF-16LE length-prefixed strings (dashboard name, description text). It is a binary serialization with embedded image assets (the file is 3.4 MB), not XML, not a ZIP.
2. **Community/developer consensus.** Multiple forum threads confirm `.rd` files are edited only inside the app; there is no documented text-based workflow for the dashboard file itself. The developer's documented workflow for dashboards is entirely in-app: "Use 'File->Save as' option in Windows to save the file to any location you choose" — [Edit dash on Windows 10, use on Android? (RealDash Forum)](https://forum.realdash.net/t/edit-dash-on-windows-10-use-on-android/797). The developer also explicitly states "No XML needed of any kind when designing dashboards. XML:s are just for specifying custom connections." — [How do you create a custom dash design (RealDash Forum)](https://forum.realdash.net/t/how-do-you-create-a-custom-dash-design/3291)

**Consequence for the automation agent: the dashboard must be built by driving the RealDash editor UI (mouse + keyboard shortcuts). There is no supported path to generate a dashboard by writing an XML/text file.**

`.rd` files ARE fully cross-platform ("the .rd files are compatible between platforms. We create all our premium dashboards on Windows version of RealDash" — [forum thread 797](https://forum.realdash.net/t/edit-dash-on-windows-10-use-on-android/797)).

### 1.2 What IS XML in the RealDash ecosystem (three sidecar formats)

These are the only text-editable surfaces, and none of them defines gauge layout/appearance:

**(a) Animation XML (`<dashname>_anim.xml`)** — defines animations + triggers that get *imported into* and *embedded in* the `.rd` on save. Documented at [Dashboard-animation-examples README (GitHub)](https://github.com/janimm/RealDash-extras/blob/master/Dashboard-animation-examples/README.md). Verified real example from `RealDash_animation_example_anim.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<RealDash>
  <animations>
    <!-- type: fade | position | morph. end = opacity 0-1, or normalized coords -->
    <animation name="fade-in-rpm" type="fade" target="RPM needle gauge" end="1.0" duration="0.3"></animation>
    <animation name="move-rpm-top" type="position" target="RPM needle gauge"
               end="0.204573631286621,0.311304569244385" duration="0.3" easing="QuadOut"></animation>
    <animation name="move-speed-container-top" type="morph" target="Speed Container"
               end="0.037662863731384,0.055070161819458,0.314941763877869,0.656040966510773"
               duration="0.3" easing="QuadOut"></animation>
  </animations>
  <triggers>
    <trigger name="Show RPM" condition="smaller" variable="Dummy 01" tolerance="1.00" reset="1.00" cooldown="0.0">
      <actions><action name="fade-in-rpm"></action></actions>
    </trigger>
  </triggers>
</RealDash>
```

Key facts from the same source:
- Gauges are addressed by their **gauge name** (`target` attribute), so naming gauges deliberately in the editor matters.
- Positions/areas are **normalized 0–1 floats** (fraction of dash size). The editor will copy them for you: "you can copy gauge position from RealDash with SHIFT+Q" and "you can copy gauge area from RealDash with CTRL+Q" (comments inside the official example XML).
- Easing values seen: `QuadOut`, `BounceOut`; `delay` attribute supported.
- Windows import: edit mode → **File → Import** ("This is required since Windows Store apps are not allowed to access files without user interaction"); press **F2** to reload the dash after changing the XML. Every save of the `.rd` embeds the animations.
- WARNING: "when you import an animation XML, ALL animation related triggers and actions are deleted and replaced by the ones from the XML. That is by design" — [RD 2.6.5-2 animation import thread (RealDash Forum)](https://forum.realdash.net/t/rd-2-6-5-2-on-android-severe-issue-when-importing-animations/10379)

**(b) CAN channel description XML** — defines how CAN frames map to input channels (NOT gauges). Format documented at [realdash-can-description-file.md (GitHub)](https://github.com/janimm/RealDash-extras/blob/master/RealDash-CAN/realdash-can-description-file.md):

```xml
<?xml version="1.0" encoding="utf-8"?>
<RealDashCAN version="2">
  <frames baseId="3200">
    <frame id="1">
      <value targetId="..." offset="..." length="..."></value>
      <!-- OR create a new 'ECU Specific' input channel: -->
      <value name="MYECU: Special RPM" offset="..." length="..."></value>
    </frame>
  </frames>
</RealDashCAN>
```

Relevant to gauge binding: a `value` with a `name` attribute (instead of `targetId`) "creates new input into RealDash *ECU Specific* category … New custom input can be used like any other input in RealDash for gauges and triggers/actions." Built-in channel IDs are listed at [realdash.net/manuals/targetid.php](https://realdash.net/manuals/targetid.php). Input remapping lives in *Settings → Units & Values → Input Mapping* (same GitHub doc).

**(c) OBD2 description XML** — `<OBD2>` root with `init` and `rotation` sections; different format from the CAN XML. [OBD2 README (GitHub)](https://github.com/janimm/RealDash-extras/blob/master/OBD2/README.md)

### 1.3 What this means for gauge attributes

Gauge position, size, fonts, colors, gradients, borders, limits and blink are all stored inside the binary `.rd` and set only through the editor UI (Section 2). There are no publicly documented XML element/attribute names for gauge definitions because no such XML exists. The closest text handles available to automation are: gauge **names**, **normalized coordinates** via Ctrl+Q/Shift+Q clipboard copy, and the animation XML above.

---

## 2. Editor procedures in the app (exact menu paths)

### 2.0 Entering/leaving edit mode, and the top menu

- Tap/click the **top center** of the screen to drop down the top menu bar, then tap **Edit** (upper right). — [Basic gauge editing for dummies (RealDash Forum)](https://forum.realdash.net/t/basic-gauge-editing-for-dummies/1519)
- Keyboard (from run mode): **Shift+6** enters edit mode; **Space** shows/hides the top menu. — [Keyboard Shortcuts (official manual)](https://realdash.net/manuals/keyboard_shortcuts.php)
- Edit-mode top menu buttons and their shortcuts (official): **File (Shift+1), Add Gauge (Shift+2), Look'n Feel (Shift+3), Input & Values (Shift+4), Dash Info (Shift+5), Settings (Shift+6), Exit Edit Mode (Shift+7)**. — [Keyboard Shortcuts](https://realdash.net/manuals/keyboard_shortcuts.php)
- Exiting edit mode (tap **Done**) prompts to save the dashboard (confirm with the check mark). — [Editing gauges (RealDash Forum)](https://forum.realdash.net/t/editing-gauges/1514)

### 2.1 Selecting a gauge

- Click it directly, or open the **gauge selection list on the left side of the screen** ("Open it by tapping the narrow handle") — essential on layered dashes. — [Change color of text gauges (official tutorial)](https://realdash.net/manuals/change_color_of_text_gauges.php)
- **Tab / Shift+Tab** select next/previous gauge; **Ctrl+A** select all; **Ctrl+F** freeze gauges (locks them against accidental selection), **Shift+Ctrl+F** unfreeze. — [Keyboard Shortcuts](https://realdash.net/manuals/keyboard_shortcuts.php)
- Renaming a gauge: select gauge → bottom edit bar → **Context Menu → Edit → (gauge) Name**, or shortcut **Ctrl+R**. — [Basic gauge editing for dummies](https://forum.realdash.net/t/basic-gauge-editing-for-dummies/1519), [Keyboard Shortcuts](https://realdash.net/manuals/keyboard_shortcuts.php)

### 2.2 LOOK'N FEEL menu structure (submenus confirmed in sources)

| Submenu | Confirmed contents | Source |
|---|---|---|
| **Font & Text** | Static Text toggle + text edit box; text/unit strings; font selection (incl. fixed-width / mono-spaced fonts). No custom TTF import — only bundled fonts. | [Custom label thread](https://forum.realdash.net/t/adding-custom-label-for-text-gauge-or-display-gauge-name/1272), [Custom dash design thread](https://forum.realdash.net/t/how-do-you-create-a-custom-dash-design/3291) |
| **Colors** | Text Color, Background Color, Image Blend Color, Arc Blend Color — each opens a color popup with Red/Green/Blue/Opacity sliders and an **Editing Level** selector (All / Normal / Warning / Critical). | [Official color tutorial](https://realdash.net/manuals/change_color_of_text_gauges.php), [Official levels tutorial](https://realdash.net/manuals/using_normal_warning_and_critical_levels.php), [Bar gauge thread](https://forum.realdash.net/t/bar-gauge-and-text-issue/1097) |
| **Images** | Background Image (with big **+** to add a file, and a **No Image** option), Needle Image. | [Make an indicator (official)](https://realdash.net/manuals/make_an_indicator.php), [Custom dash design thread](https://forum.realdash.net/t/how-do-you-create-a-custom-dash-design/3291) |
| **Special** | Angles & Offsets (Start Angle, Sweep Angle); Autoscaling ("Use Automatic Scale" toggle, Size Scale, Text Size, Text Offset, Max digits, Segments, Mid segments); **Blink Speed** (per editing level). | [ARC gauge design guide](https://forum.realdash.net/t/dash-design-for-beginners-arc-gauge/7086), [Flashing indicators thread](https://forum.realdash.net/t/flashing-indicators/7487) |
| **Shadows** | Automatic shadow or custom shadow map image; shadow offset. | [One-off cluster graphics thread](https://forum.realdash.net/t/one-off-cluster-graphics/920) |

(Exact naming in-app is "Look'n Feel"; official tutorials sometimes write "Look & Feel".)

### 2.3 Change the text/label of a text gauge

Static label: **Add Gauge → Text Gauge** → (gauge selected) **Look'n Feel → Font & Text → enable 'Static Text'** → type the text in the edit box just above → back out and save. — developer instructions, [Custom label thread](https://forum.realdash.net/t/adding-custom-label-for-text-gauge-or-display-gauge-name/1272). If Static Text is disabled, the gauge shows the bound input's live value instead. — [Multiple text gauges thread](https://forum.realdash.net/t/multiple-text-gauges-in-1-place-and-switch-mode/480)

### 2.4 Set gauge colors (incl. per-level) — the canonical procedure

From the official tutorial [Change color of text gauges](https://realdash.net/manuals/change_color_of_text_gauges.php) ("applies to all kind of gauges"):
1. Edit mode → select gauge → **Look'n Feel → Colors → Text Color** (or Background Color, etc.)
2. Adjust the Red/Green/Blue/Opacity values.
3. **Back** until on dashboard → save.

Per-level colors, from [Using normal, warning and critical levels (official)](https://realdash.net/manuals/using_normal_warning_and_critical_levels.php):
1. In the color popup the **Editing Level** selector defaults to **All** (edits apply to Normal+Warning+Critical simultaneously).
2. Tap **Editing Level → Normal** and set the normal color; repeat for **Warning** and **Critical**.
3. GOTCHA: re-editing a color while Editing Level = **All** "will override all other editing levels" (wipes your per-level colors). — [Bar gauge thread (dev post)](https://forum.realdash.net/t/bar-gauge-and-text-issue/1097), same warning in [ARC guide](https://forum.realdash.net/t/dash-design-for-beginners-arc-gauge/7086)

Concrete RGB example from the developer (text gauge whose background turns yellow/red): Warning level → R255 G255 B0 Opacity 255; Critical level → R255 G0 B0 Opacity 255. — [Bar gauge thread](https://forum.realdash.net/t/bar-gauge-and-text-issue/1097)

**Gradients:** the Bar Gauge natively supports gradient colors — the developer suggests "add a Bar Gauge behind it. That also allows to use gradient colors etc." — [Custom dash design thread](https://forum.realdash.net/t/how-do-you-create-a-custom-dash-design/3291). (Gradient controls appear in the bar gauge's Colors popup; no page documenting the exact slider names was found.) For rounded corners/borders there is no documented native control — well-regarded designs achieve them with PNG background images (optionally 9-sliced) or leave tiles square. — [ARC guide](https://forum.realdash.net/t/dash-design-for-beginners-arc-gauge/7086)

### 2.5 Add and size a Bar Gauge

- **Add Gauge** → the gauge type list (Text Gauge, Image, Indicators → Needle Gauge, Bar Gauge, etc.). Bar Gauge is referenced by the developer as a standard addable type. — [Custom dash design thread](https://forum.realdash.net/t/how-do-you-create-a-custom-dash-design/3291), [Make an indicator](https://realdash.net/manuals/make_an_indicator.php)
- Size/move precisely with the keyboard: **Arrow keys** move, **Shift+Arrows** resize, **Shift+Ctrl+Arrows** resize around center; **Ctrl+7** make selected gauges same size, **Ctrl+6** match size *and* position; **Ctrl+2/Ctrl+3** center horizontally/vertically. — [Keyboard Shortcuts](https://realdash.net/manuals/keyboard_shortcuts.php)
- Then bind and color it exactly as in 2.4/2.6 (bar color per level; the whole bar takes the color of the currently active level).

### 2.6 Warning/critical ranges on a gauge (INPUT & VALUES)

From [Using normal, warning and critical levels (official)](https://realdash.net/manuals/using_normal_warning_and_critical_levels.php):
1. Select gauge → **Input & Values** (top menu). The popup contains: **Select Data Source**, **Range** (min/max), **Warning Level** (min/max), **Critical Level** (min/max).
2. Semantics: levels are "used for graphical effects only." A gauge is in Warning when the value exceeds the Warning min/max window but not the Critical one; in Critical when the value is below Critical min or above Critical max.
3. Tutorial example for RPM: Range 0–8000, Warning 0–4000, Critical 0–6000 (i.e., >4000 = warning look, >6000 = critical look).
4. GOTCHA: degenerate windows like "Warning 0 and above" keep the gauge permanently in warning; the developer's fix was to use a window like "40 ↔ 101" for a 0–100 sensor. — [Bar gauge thread](https://forum.realdash.net/t/bar-gauge-and-text-issue/1097)

### 2.7 Bind an ECU-specific channel (INPUT & VALUES)

Developer's exact steps ([Editing gauges thread](https://forum.realdash.net/t/editing-gauges/1514)):
1. In edit mode, select the gauge and tap **Input & Values** on top menu.
2. Tap the button underneath **Select Data Source** and pick e.g. **Engine/ECU inputs → Manifold Absolute Pressure**.
3. Tap upper-left **Done** until back on the dashboard; tap **Done** on the top menu → save prompt.

Channels created by a custom CAN XML `name="..."` attribute appear under the **ECU Specific** category in the same picker. — [CAN description file doc (GitHub)](https://github.com/janimm/RealDash-extras/blob/master/RealDash-CAN/realdash-can-description-file.md). To unlink a gauge (e.g., a static label), set **Select Data Source = None**. — [Basic gauge editing for dummies](https://forum.realdash.net/t/basic-gauge-editing-for-dummies/1519)

### 2.8 Delete a gauge

Select gauge(s) → **Del** key ("Delete selected gauges"). **Shift+Del** deletes the whole page. — [Keyboard Shortcuts](https://realdash.net/manuals/keyboard_shortcuts.php). Gauge delete also has Undo (**Ctrl+Z**). — [Google Play changelog](https://play.google.com/store/apps/details?hl=en_US&id=com.napko.RealDash)

### 2.9 Group / align gauges

All official, from [Keyboard Shortcuts](https://realdash.net/manuals/keyboard_shortcuts.php):
- Align: **Ctrl+H** left, **Ctrl+K** right, **Ctrl+U** top, **Ctrl+M** bottom; **Ctrl+J** space evenly ("Space Evenly" with exactly 2 gauges selected centers them relative to each other — [alignment feature thread](https://forum.realdash.net/t/aligning-two-or-more-objects-to-a-common-center/736)).
- Center: **Ctrl+1** center, **Ctrl+2** horizontal, **Ctrl+3** vertical; z-order: **Numpad+ / Numpad-**.
- Containers exist as a grouping mechanism ("Add/Remove with Container now has Undo", "Buttons can now be placed under the container" — [Google Play changelog](https://play.google.com/store/apps/details?hl=en_US&id=com.napko.RealDash)); containers are also animation targets (see `Speed Container` in the animation XML, Section 1.2).

### 2.10 Save under a NEW name (save-as) vs overwriting

- **Save-as (Windows):** edit mode → **File → Save as** → choose any name/location. — developer, [forum thread 797](https://forum.realdash.net/t/edit-dash-on-windows-10-use-on-android/797)
- **Overwrite/save:** **Ctrl+S** ("Save dashboard"), or exit edit mode (**Done** / Shift+7) and confirm the save prompt with the check mark. — [Keyboard Shortcuts](https://realdash.net/manuals/keyboard_shortcuts.php), [Basic gauge editing](https://forum.realdash.net/t/basic-gauge-editing-for-dummies/1519)
- **New dashboard:** **Edit → File → New dashboard**. — [official levels tutorial](https://realdash.net/manuals/using_normal_warning_and_critical_levels.php)
- **Load:** **Ctrl+O**, or run mode **Gallery → Recent → Open from file**. — [Keyboard Shortcuts](https://realdash.net/manuals/keyboard_shortcuts.php), [forum thread 797](https://forum.realdash.net/t/edit-dash-on-windows-10-use-on-android/797)
- The developer's standing advice: "Make backups while experimenting with editing." — [Editing gauges](https://forum.realdash.net/t/editing-gauges/1514)

---

## 3. Existing dashes for inspiration/reuse (Gallery)

### 3.1 How the Gallery works on Windows

- In-app **Gallery** (run mode, Shift+1) has premium dashboards, free dashboards/Gizmos, a **Community** section (dashes shared through the My RealDash web service), and **Recent → Open from file** for loading arbitrary `.rd` files from disk. — [Google Play listing](https://play.google.com/store/apps/details?hl=en_US&id=com.napko.RealDash), [Layout transfer thread](https://forum.realdash.net/t/layout-transfer-android-to-android/8412), [forum thread 797](https://forum.realdash.net/t/edit-dash-on-windows-10-use-on-android/797)
- **Where files live on Windows:** during first boot "RealDash is asking for a folder to store all its files" — settings, dashboards, downloads all go under that user-chosen folder. — developer, [Moving RD files to a new device (RealDash Forum)](https://forum.realdash.net/t/moving-rd-files-to-a-new-device/1512)
- Downloaded/gallery dashes are ordinary `.rd` files: they can be re-saved anywhere via **File → Save as** and are cross-platform. — [forum thread 797](https://forum.realdash.net/t/edit-dash-on-windows-10-use-on-android/797)
- **Rebinding inputs on a downloaded dash is fully supported and is the standard workflow:** edit mode → select gauge → Input & Values → new data source (the "Engineers Dream" / Boost→MAP examples in Section 2.7 are exactly this). — [Editing gauges](https://forum.realdash.net/t/editing-gauges/1514), [Basic gauge editing](https://forum.realdash.net/t/basic-gauge-editing-for-dummies/1519)
- **Limits:** premium fully-animated dashes cannot have their animations modified ("it is not possible to add or modify animations on our premium dashboards… decided to give an option to add some simple gauges etc." — [Editing Premium Dashboard](https://forum.realdash.net/t/editing-premium-dashboard/6064)); some premium dashes are explicitly "mostly fixed and not suitable for editing" (F40, Classic Italian — [official Gallery page](https://realdash.net/gallery.php)).

### 3.2 Candidate dashes with a modern flat/dark, data-tile character

Verified options (free first):

1. **Multiview** — FREE in the RealDash Gallery; fully animated 4-view dashboard; also distributed as raw `Multiview.rd` + `Multiview_anim.xml` on the developer's GitHub, so it can be loaded from file and dissected. Best free starting point for studying structure. — [Dashboard-animation-examples README](https://github.com/janimm/RealDash-extras/blob/master/Dashboard-animation-examples/README.md)
2. **Community dashes via Gallery → Community / my.realdash.net** — free user-shared dashes, including the developer-sponsored **DEATHFISH 2** three-screen set ("I'm planning to share all 3 DEATHFISH dashboards for free for my.realdash.net users") and free skins such as "True MuliCast free skin" in the showcase forum. Requires a (free-tier) My RealDash login to browse shares. — [DEATHFISH 2 showcase](https://forum.realdash.net/t/deathfish-2/1377?page=2), [Showcase category](https://forum.realdash.net/c/general/project-dashboard-showcase/14), [Introducing My RealDash](https://forum.realdash.net/t/introducing-my-realdash/1031)
3. **Data Engineers Dream** (premium, not free) — the closest official match to a "clean grid of data tiles": "super clean data tracking dashboard… 11 different arc gauges… 9 different graph gauges. They're easy adjust display whatever you want." Useful as visual reference even if not purchased. — [official Gallery page](https://realdash.net/gallery.php)
4. **Pole Position** (premium) — "super clear one page racing dashboard… really simple so it is easier to quickly check … or if you need to customize it"; flat text/number-driven design whose background color reacts to RPM — a good pattern reference for a flat tile dash built from text gauges + background colors. — [official Gallery page](https://realdash.net/gallery.php)

Practical note: since a flat grid of digital value tiles needs only **Text Gauges (with background colors) and Bar Gauges**, building from an empty dash (Edit → File → New dashboard) is genuinely competitive with adapting a downloaded dash — no image assets are required for that style. — [Bar gauge thread](https://forum.realdash.net/t/bar-gauge-and-text-issue/1097)

---

## 4. Tips & tricks

### 4.1 Video tutorials

- The official tutorial pages each embed a "Watch video" walkthrough: [Change color of text gauges](https://realdash.net/manuals/change_color_of_text_gauges.php), [Make an indicator](https://realdash.net/manuals/make_an_indicator.php), [Using normal, warning and critical levels](https://realdash.net/manuals/using_normal_warning_and_critical_levels.php) — all indexed at [realdash.net/manuals.php](https://realdash.net/manuals.php). When asked for editing-basics videos, the developer points users to "these couple of videos at the end of the page" on that manuals page. — [Custom light indicators thread](https://forum.realdash.net/t/help-custom-light-indicators-and-switchet-gauge-faces/8306). The app is published by Napko Oy ([Google Play listing](https://play.google.com/store/apps/details?id=com.napko.RealDash&hl=en)); searches did not surface a directly verifiable standalone YouTube channel URL, so treat the manuals-page embeds as the authoritative video source.

### 4.2 Flat/modern design techniques

- **Text gauge + Background Color = a tile.** The developer's own recipe colors a text gauge's background per level (Section 2.4). No images needed. — [Bar gauge thread](https://forum.realdash.net/t/bar-gauge-and-text-issue/1097)
- **Labels are separate static text gauges** — value, unit and label are typically 3 stacked gauges (see the Boost gauge = "arc + text + value + unit" anatomy). — [Basic gauge editing](https://forum.realdash.net/t/basic-gauge-editing-for-dummies/1519), [Custom label thread](https://forum.realdash.net/t/adding-custom-label-for-text-gauge-or-display-gauge-name/1272)
- **Depth:** Look'n Feel → **Shadows** (automatic shadow or custom shadow map, adjustable offset); Bar Gauges support **gradient colors**; grayscale images + per-level **Image Blend Color** recolor artwork live. — [One-off cluster graphics](https://forum.realdash.net/t/one-off-cluster-graphics/920), [Custom dash design](https://forum.realdash.net/t/how-do-you-create-a-custom-dash-design/3291)
- **Blink/strobe on alarm:** Look'n Feel → **Special → Blink Speed**, set per editing level (leave Normal at 0, set Warning/Critical > 0). — developer, [Flashing indicators](https://forum.realdash.net/t/flashing-indicators/7487)
- **Invisible-until-alarm indicators:** set Normal-level Image Blend/text Opacity near 0 so the gauge only "appears" in Warning/Critical. — [Make an indicator (official)](https://realdash.net/manuals/make_an_indicator.php)

### 4.3 Text gauge sizing behavior (why fonts render different sizes)

- **The gauge's height IS the text height**; text size is not set in points — resize the gauge to change the font size: "The height of the gauge is height of the text and width of the gauge can optionally be used to rotate the text in text area." — developer, [More documentation thread](https://forum.realdash.net/t/more-documentation-and-perhaps-a-design-tool/1254). So two "same font" tiles look different if their gauge rects differ — normalize with **Ctrl+7** (make same size).
- One font size per text gauge; multiple sizes require multiple gauges. — [Custom label thread](https://forum.realdash.net/t/adding-custom-label-for-text-gauge-or-display-gauge-name/1272)
- Digits right-align as they change width; for stable multi-digit readouts use a **Fixed Width / Mono Spaced font** (Font & Text). — [Custom dash design thread](https://forum.realdash.net/t/how-do-you-create-a-custom-dash-design/3291)
- Needle/arc gauges have separate text controls under Look'n Feel → Special → **Autoscaling** (Text Size, Text Offset, Max digits — e.g. Max digits turns "8000" RPM labels into "8"). — [ARC guide](https://forum.realdash.net/t/dash-design-for-beginners-arc-gauge/7086), [Build my own gauge](https://forum.realdash.net/t/build-my-own-gauge/497)

### 4.4 Known editor quirks on Windows

- **UWP app limitations:** RealDash for Windows is a UWP app; the window "cannot be exactly the width of the monitor" in windowed mode — use **F4** fullscreen and **F5–F8** aspect-ratio presets. — developer, [fix display resolution thread](https://forum.realdash.net/t/fix-display-resolution/1281), [Keyboard Shortcuts](https://realdash.net/manuals/keyboard_shortcuts.php)
- **Editing aspect ratio setting:** Settings → Application → **Editing** offers aspect-ratio options (e.g. 8:3) so the edit canvas matches the target screen. — [fix display resolution thread](https://forum.realdash.net/t/fix-display-resolution/1281)
- **Click-zone misalignment** has been reported in fullscreen with unusual resolutions ("the top bar's buttons' click zone doesn't match their icon zone"); if the top menu is unreachable by mouse, fall back to keyboard: **Space** (toggle top menu), **Ctrl+E** (toggle Edit Bar), Shift+1..7 menu shortcuts. — [Fullscreen Issues thread](https://forum.realdash.net/t/fullscreen-issues/6475), [Keyboard Shortcuts](https://realdash.net/manuals/keyboard_shortcuts.php)
- **Top/bottom tap zones:** UI is touch-first; mouse clicks emulate taps. Top-center tap = top menu; bottom-center tap in edit mode = bottom edit bar with Context Menu. — [Basic gauge editing](https://forum.realdash.net/t/basic-gauge-editing-for-dummies/1519)
- **Do not edit while "UltraWide haxxor" is active** — "It will completely skew all the gauge placements." — developer, [More documentation thread](https://forum.realdash.net/t/more-documentation-and-perhaps-a-design-tool/1254)
- **Hidden gauges stay hidden after save/load** ("if you save the dashboard and a gauge is hidden, it will remain hidden when dash is loaded"), and copy-pasted gauges have occasionally carried glitched state — when a pasted gauge misbehaves, delete and recreate it. — [Multiple text gauges thread](https://forum.realdash.net/t/multiple-text-gauges-in-1-place-and-switch-mode/480)
- **Editing Level = All wipes per-level colors** (worth repeating — it is the most common way to lose warning/critical styling). — [Bar gauge thread](https://forum.realdash.net/t/bar-gauge-and-text-issue/1097)
- **F2 reboots/reloads the app** (used to re-apply an edited animation XML); **F9** saves a screenshot — useful for automated visual verification. — [Keyboard Shortcuts](https://realdash.net/manuals/keyboard_shortcuts.php), [animation README](https://github.com/janimm/RealDash-extras/blob/master/Dashboard-animation-examples/README.md)

---

## Actionable summary for the automation agent

1. **Do not attempt to write or edit `.rd` files directly.** They are proprietary binary (verified by hex dump of the official `Multiview.rd`: binary header + UTF-16LE strings + embedded assets). All dashboard building must happen through the app UI.
2. **Drive the editor with keyboard shortcuts wherever possible** — they are officially documented and more reliable than hunting menu hit-zones: Shift+6 enter edit, Shift+1..7 = File/Add Gauge/Look'n Feel/Input & Values/Dash Info/Settings/Exit, Ctrl+S save, Ctrl+O load, Del delete gauge, Tab cycle gauges, Space toggle top menu, Ctrl+E toggle edit bar. ([Keyboard Shortcuts](https://realdash.net/manuals/keyboard_shortcuts.php))
3. **Canonical color path:** Select gauge → Look'n Feel → Colors → {Text Color | Background Color | Image Blend Color | Arc Blend Color} → set R/G/B/Opacity. Set **Editing Level** (All/Normal/Warning/Critical, selector in the color popup — gear icon bottom-left) BEFORE adjusting; editing while "All" is selected overwrites all per-level colors.
4. **Canonical text path:** Look'n Feel → Font & Text → enable "Static Text" + type text (labels), or leave off to show the bound value; font choice here (prefer a mono/fixed-width font for numeric tiles). Text size = gauge height, so set size by resizing the gauge (Shift+Arrows), not by a font-size field; Ctrl+7 equalizes sizes across selected gauges.
5. **Canonical binding path:** Select gauge → Input & Values → Select Data Source → category (e.g. "Engine/ECU inputs", or "ECU Specific" for channels created by a custom CAN XML `name` attribute) → channel; the same popup holds Range min/max, Warning Level min/max, Critical Level min/max. Warning/Critical are windows — the gauge alarms when the value *leaves* the window; never use a degenerate window (e.g. use "40 ↔ 101" not "0 and above").
6. **Flat dark tile recipe (no image assets needed):** Add Gauge → Text Gauge per tile; background color via Colors → Background Color; per-level yellow/red backgrounds (dev's example: Warning R255 G255 B0 O255, Critical R255 G0 B0 O255); Bar Gauge for level bars (supports gradient fills); blink via Look'n Feel → Special → Blink Speed on Warning/Critical levels only.
7. **Layout tooling:** Ctrl+H/K/U/M align left/right/top/bottom, Ctrl+J space evenly, Ctrl+1/2/3 centering, arrow keys move / Shift+arrows resize, Numpad+/- z-order, Ctrl+F freeze background gauges so clicks don't grab them. Ctrl+Q copies the selected gauge's normalized area (x,y,w,h as 0–1 floats) to the clipboard — the only machine-readable geometry export.
8. **Save-as vs overwrite:** edit mode → File → Save as (new name/location, Windows); Ctrl+S or Done→checkmark overwrites. New dash: Edit → File → New dashboard. Make a backup copy of the .rd before each editing session (developer's own advice).
9. **Gallery reuse:** free "Multiview" dash is downloadable both in-app (Gallery) and as a raw .rd from the developer's GitHub (`janimm/RealDash-extras/Dashboard-animation-examples`); community free dashes come via Gallery → Community (My RealDash login). Any loaded dash can be rebound gauge-by-gauge via Input & Values; avoid premium animated dashes (animations locked, some "not suitable for editing"). On Windows all files live in the folder chosen at first app start.
10. **Windows-specific fallbacks:** if mouse clicks on the top menu misfire (known UWP fullscreen click-zone quirk), use Space/Ctrl+E/Shift+N shortcuts instead; use F4 fullscreen + Settings → Application → Editing aspect ratio to match the target display before laying out gauges; F9 saves a screenshot for automated visual verification; F2 reloads the app/dash.

---

## Sources

- [RealDash Manuals & Tutorials index](https://realdash.net/manuals.php)
- [Tutorial: Change color of text gauges](https://realdash.net/manuals/change_color_of_text_gauges.php)
- [Tutorial: Using normal, warning and critical levels](https://realdash.net/manuals/using_normal_warning_and_critical_levels.php)
- [Tutorial: Make an indicator](https://realdash.net/manuals/make_an_indicator.php)
- [Manual: Keyboard Shortcuts](https://realdash.net/manuals/keyboard_shortcuts.php)
- [RealDash Gallery (premium dash descriptions)](https://realdash.net/gallery.php)
- [GitHub: Dashboard-animation-examples README + Multiview.rd + example anim XML](https://github.com/janimm/RealDash-extras/blob/master/Dashboard-animation-examples/README.md)
- [GitHub: RealDash CAN channel description file format](https://github.com/janimm/RealDash-extras/blob/master/RealDash-CAN/realdash-can-description-file.md)
- [GitHub: OBD2 XML description files](https://github.com/janimm/RealDash-extras/blob/master/OBD2/README.md)
- [Forum: Edit dash on Windows 10, use on Android? (File→Save as, .rd portability)](https://forum.realdash.net/t/edit-dash-on-windows-10-use-on-android/797) (Nov 2020)
- [Forum: Basic gauge editing for dummies](https://forum.realdash.net/t/basic-gauge-editing-for-dummies/1519) (Jan 2023)
- [Forum: Editing gauges (Input & Values binding steps)](https://forum.realdash.net/t/editing-gauges/1514) (Jan 2023)
- [Forum: Adding custom Label for text gauge (Static Text)](https://forum.realdash.net/t/adding-custom-label-for-text-gauge-or-display-gauge-name/1272) (Apr 2022)
- [Forum: Bar gauge and text issue (per-level background colors, level gotchas)](https://forum.realdash.net/t/bar-gauge-and-text-issue/1097) (2022)
- [Forum: Dash Design for Beginners - ARC Gauge](https://forum.realdash.net/t/dash-design-for-beginners-arc-gauge/7086) (2024)
- [Forum: How do you create a custom dash design (images, bar gauge gradients, mono font)](https://forum.realdash.net/t/how-do-you-create-a-custom-dash-design/3291) (2023)
- [Forum: Flashing indicators (Blink Speed)](https://forum.realdash.net/t/flashing-indicators/7487) (2025)
- [Forum: One-off cluster graphics (Shadows)](https://forum.realdash.net/t/one-off-cluster-graphics/920) (2021)
- [Forum: More documentation and perhaps a design tool (text height = gauge height; ultrawide warning)](https://forum.realdash.net/t/more-documentation-and-perhaps-a-design-tool/1254) (Apr 2022)
- [Forum: Build my own gauge (arc mechanics, max digits)](https://forum.realdash.net/t/build-my-own-gauge/497) (2020)
- [Forum: Aligning two or more objects to a common center (Space Evenly)](https://forum.realdash.net/t/aligning-two-or-more-objects-to-a-common-center/736) (Oct 2020)
- [Forum: Multiple text gauges in 1 place (hidden-gauge save behavior, copy-paste glitch)](https://forum.realdash.net/t/multiple-text-gauges-in-1-place-and-switch-mode/480) (2020)
- [Forum: Editing Premium Dashboard (premium animation lock)](https://forum.realdash.net/t/editing-premium-dashboard/6064) (Aug 2024)
- [Forum: Triggers/Actions Help (premium anim XML not shared; dummy-variable pattern)](https://forum.realdash.net/t/triggers-actions-help/5573) (2024)
- [Forum: Moving RD files to a new device (Windows storage folder chosen at first boot)](https://forum.realdash.net/t/moving-rd-files-to-a-new-device/1512) (Jan 2023)
- [Forum: Layout transfer - android to android (My RealDash upload/share → Gallery→Community)](https://forum.realdash.net/t/layout-transfer-android-to-android/8412) (Jun 2025)
- [Forum: Introducing My RealDash](https://forum.realdash.net/t/introducing-my-realdash/1031) (2021)
- [Forum: DEATHFISH 2 showcase (free community dash set)](https://forum.realdash.net/t/deathfish-2/1377?page=2) (2022)
- [Forum: Project & Dashboard Showcase category](https://forum.realdash.net/c/general/project-dashboard-showcase/14)
- [Forum: Fullscreen Issues (click-zone misalignment)](https://forum.realdash.net/t/fullscreen-issues/6475) (2024)
- [Forum: fix display resolution (UWP window limits, Settings→Application→Editing aspect)](https://forum.realdash.net/t/fix-display-resolution/1281) (Apr 2022)
- [Forum: RD 2.6.5-2 animation import behavior (import replaces all anim triggers)](https://forum.realdash.net/t/rd-2-6-5-2-on-android-severe-issue-when-importing-animations/10379) (2026)
- [Forum: Documentation on Actions and Triggers (action types, Gauge Math)](https://forum.realdash.net/t/documentation-on-actions-and-triggers/8280) (2025)
- [Forum: Unable to edit and parse example xml file (anim XML naming)](https://forum.realdash.net/t/unable-to-edit-and-parse-example-xml-file/7044) (Nov 2024)
- [Google Play: RealDash listing (feature list, changelog, Napko Oy)](https://play.google.com/store/apps/details?hl=en_US&id=com.napko.RealDash)

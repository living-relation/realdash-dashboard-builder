# Imported user assets — manifest (Stage P, round 4)

Source folders (OneDrive, all files read OK — no cloud-placeholder failures):
- `C:\Users\danie\.personal OneDrive\OneDrive\Desktop\Celica\Dashboard\PowerTune\Full PowerTune layouts\Corsa\CORSA v1.1_Dash wLights\Logos`
- `C:\Users\danie\.personal OneDrive\OneDrive\Desktop\Celica\Dashboard\PowerTune\Full PowerTune layouts\ECU Master`

| File | Dims / format | Good for |
|---|---|---|
| `corsa_CORSA_BG.png` | 1025x577 RGBA | Full PowerTune "Corsa" dash background (gauge furniture baked in). Style reference or donor background; will upscale to 1920x1000 canvas. |
| `corsa_SL_0000.png` … `corsa_SL_7000.png` (12 frames) | 1476x169/170 RGBA | Progressive shift-light LED strip, one frame per RPM threshold (0, 2800, 3250, 3500, 4000, 4500, 5000, 5250, 5500, 6000, 6500, 7000). Mostly transparent, small size. Use as stacked indicator images with RPM warn levels, or as art reference for an LED shift bar on a new dash. |
| `ecumaster_ECUM_BG.png` | 803x481 RGBA | PowerTune "ECU Master" dash background (800x480 layout). Style reference / donor background. |

NOT copied: `_ECU_MASTER_FINAL.txt` (PowerTune text layout definition, not an image — documents gauge positions/fonts of the ECU Master layout; uses Lato / Trebuchet MS).

NOTE: neither folder contains needle graphics, bezels, standalone gauge faces, or logo marks — only the two full backgrounds and the shift-light frame set.

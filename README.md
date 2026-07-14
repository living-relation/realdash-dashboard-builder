# RealDash Dashboard Builder

Cursor skill + tooling + ST185 dashboard layouts for creating and editing RealDash `.rd` dashboards on Windows (binary edit pipeline + PyAutoGUI automation).

## What's in this repo

| Path | Contents |
|------|----------|
| `skill/` | Cursor Agent skill (`SKILL.md` + `reference.md`) |
| `dashboards/` | Ten production ST185 `.rd` layouts (v1–v10), 800×480 |
| `descfiles/` | Link G4X RealDash CAN channel XML |
| `tools/` | Binary `.rd` editors, builders, GUI automation helpers |
| `docs/` | Build plan, findings, progress ledgers, simulation reference |
| `_build/` | Donor `.rd` files, face/background assets used by builders |

## Install the skill

Copy or symlink into your personal Cursor skills folder:

```powershell
New-Item -ItemType Junction -Path "$env:USERPROFILE\.cursor\skills\realdash-dashboard-builder" -Target "C:\projects\realdash-dashboard-builder\skill"
```

(Or copy `skill/` to `~/.cursor/skills/realdash-dashboard-builder/`.)

## Scope

**Included:** dashboard creation, binary `.rd` editing, Windows RealDash automation, ST185 layout variants.

**Not included:** Raspberry Pi kiosk/deploy scripts, host credentials, or account passwords. Never commit a `CREDENTIALS.md`.

## Quick start

```powershell
cd tools
pip install -r requirements.txt
python load_dash.py ..\dashboards\st185_dash_v5.rd smoke.png
```

See `skill/SKILL.md` before editing production dashes.

## License / ownership

Private tooling for the ST185 TrackCluster RealDash head unit project.

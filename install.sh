#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SKIN_HOME="${CODEX_SKIN_HOME:-$HOME/.codex-skin-app}"
PET_ID="xilian"
THEME_ID="custom-mu0wrtsv"

mkdir -p "$CODEX_HOME/pets/$PET_ID" "$SKIN_HOME/themes/$THEME_ID"
cp "$ROOT_DIR/pet/pet.json" "$CODEX_HOME/pets/$PET_ID/pet.json"
cp "$ROOT_DIR/pet/spritesheet.webp" "$CODEX_HOME/pets/$PET_ID/spritesheet.webp"
cp "$ROOT_DIR/theme/theme.json" "$SKIN_HOME/themes/$THEME_ID/theme.json"
cp "$ROOT_DIR/theme/background.jpg" "$SKIN_HOME/themes/$THEME_ID/background.jpg"
cp "$ROOT_DIR/theme/hero.webp" "$SKIN_HOME/themes/$THEME_ID/hero.webp"
cp "$ROOT_DIR/theme/watermark.webp" "$SKIN_HOME/themes/$THEME_ID/watermark.webp"
cp "$ROOT_DIR/theme/custom.css" "$SKIN_HOME/themes/$THEME_ID/custom.css"

python3 - "$SKIN_HOME/settings.json" "$SKIN_HOME/manifest.json" "$SKIN_HOME/themes/$THEME_ID/custom.css" "$THEME_ID" <<'PY'
import json
import sys
from pathlib import Path

settings_path = Path(sys.argv[1])
manifest_path = Path(sys.argv[2])
css_path = Path(sys.argv[3])
theme_id = sys.argv[4]

settings = json.loads(settings_path.read_text()) if settings_path.exists() else {"schemaVersion": 1}
settings["activeTheme"] = {"css": css_path.read_text(), "theme_id": theme_id}
settings_path.parent.mkdir(parents=True, exist_ok=True)
settings_path.write_text(json.dumps(settings, ensure_ascii=False, separators=(",", ":")))

manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {"schemaVersion": 1, "themes": []}
themes = manifest.setdefault("themes", [])
if theme_id not in themes:
    themes.append(theme_id)
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
PY

cat <<EOF
Installed:
  pet:   $CODEX_HOME/pets/$PET_ID
  theme: $SKIN_HOME/themes/$THEME_ID

Restart CodexSkin, then refresh Pets in Codex Settings and select “昔涟 · 3D Q版”.
EOF

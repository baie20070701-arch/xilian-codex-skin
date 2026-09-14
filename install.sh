#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SKIN_HOME="${CODEX_SKIN_HOME:-$HOME/.codex-skin-app}"
PET_ID="xilian"
ORIGINAL_THEME_ID="custom-mu0wrtsv"
COMFORT_THEME_ID="custom-xilian-comfort"

install_theme() {
  local source_dir="$1"
  local theme_id="$2"
  local target_dir="$SKIN_HOME/themes/$theme_id"

  mkdir -p "$target_dir"
  for file in theme.json background.jpg hero.webp watermark.webp custom.css; do
    if [[ -f "$source_dir/$file" ]]; then
      cp "$source_dir/$file" "$target_dir/$file"
    fi
  done
}

mkdir -p "$CODEX_HOME/pets/$PET_ID"
cp "$ROOT_DIR/pet/pet.json" "$CODEX_HOME/pets/$PET_ID/pet.json"
cp "$ROOT_DIR/pet/spritesheet.webp" "$CODEX_HOME/pets/$PET_ID/spritesheet.webp"

install_theme "$ROOT_DIR/theme" "$ORIGINAL_THEME_ID"
install_theme "$ROOT_DIR/theme-eye-comfort" "$COMFORT_THEME_ID"

if [[ -f "$SKIN_HOME/settings.json" ]]; then
  cp "$SKIN_HOME/settings.json" "$SKIN_HOME/settings.json.backup"
fi

python3 - "$SKIN_HOME/settings.json" "$SKIN_HOME/manifest.json" "$SKIN_HOME/themes/$COMFORT_THEME_ID/custom.css" "$COMFORT_THEME_ID" "$ORIGINAL_THEME_ID" <<'PY'
import json
import sys
from pathlib import Path

settings_path = Path(sys.argv[1])
manifest_path = Path(sys.argv[2])
css_path = Path(sys.argv[3])
comfort_theme_id = sys.argv[4]
original_theme_id = sys.argv[5]

settings = json.loads(settings_path.read_text()) if settings_path.exists() else {"schemaVersion": 1}
settings["activeTheme"] = {"css": css_path.read_text(), "theme_id": comfort_theme_id}
settings_path.parent.mkdir(parents=True, exist_ok=True)
settings_path.write_text(json.dumps(settings, ensure_ascii=False, separators=(",", ":")))

manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {"schemaVersion": 1, "themes": []}
themes = manifest.setdefault("themes", [])
for theme_id in (original_theme_id, comfort_theme_id):
    if theme_id not in themes:
        themes.append(theme_id)
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
PY

cat <<EOF
Installed:
  pet:   $CODEX_HOME/pets/$PET_ID
  theme (active, 护眼版): $SKIN_HOME/themes/$COMFORT_THEME_ID
  theme (original):      $SKIN_HOME/themes/$ORIGINAL_THEME_ID

Restart CodexSkin, then refresh Pets in Codex Settings and select “昔涟 · 3D Q版”.
EOF

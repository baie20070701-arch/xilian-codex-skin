# XiLian Codex Skin

A XiLian-inspired glass theme and 3D chibi pet for the Codex desktop app.

The repository now ships two theme variants. The **Eye-comfort Edition（护眼版）** is installed as the default active theme.

![Theme hero](preview/theme-hero.webp)

![Pet animation sheet](preview/pet-contact-sheet.png)

## Theme variants

| Directory | Theme name | Description |
| --- | --- | --- |
| `theme/` | 昔涟 · 云端回响（完整修复） | Original bright pink/lavender glass theme with the full-screen XiLian watermark. |
| `theme-eye-comfort/` | 昔涟 · 云端回响（护眼版） | Lower-glare mauve-pink palette, deeper reading layers, stronger surface separation, and a clearer full-screen character background. |

The eye-comfort variant keeps the same fonts, pet, and layout while reducing glare, preserving text contrast, and avoiding the pale washed-out look.

## Features

- Pink, lavender, and glass-style Codex theme
- Eye-comfort Edition with a lower-glare, low-saturation palette
- Full-screen XiLian image watermark layer
- Custom sidebar, conversation bubbles, composer, cards, and focus states
- Codex v2 pet atlas with 8 columns and 11 animation rows
- Idle, directional movement, waving, jumping, waiting, processing, review, and look states
- Transparent pet overlay with safe animation margins

## Repository layout

```text
theme/                Original CodexSkin theme files
theme-eye-comfort/    Eye-comfort Edition theme files
pet/                  Codex custom pet files
preview/              Preview images
scripts/              Portable pet atlas builder
install.sh
CHANGELOG.md
```

## Requirements

- macOS
- Codex desktop app
- CodexSkin for the full UI theme
- Python 3 with Pillow for the optional pet builder

## Install

```bash
git clone https://github.com/baie20070701-arch/xilian-codex-skin.git
cd xilian-codex-skin
./install.sh
```

The installer copies both themes and activates the **护眼版** by default:

- `pet/` to `~/.codex/pets/xilian/`
- `theme/` to `~/.codex-skin-app/themes/custom-mu0wrtsv/`
- `theme-eye-comfort/` to `~/.codex-skin-app/themes/custom-xilian-comfort/`
- the active CodexSkin theme configuration to `~/.codex-skin-app/settings.json`

Restart CodexSkin after installation. In Codex, open **Settings → Pets**, refresh, and select **昔涟 · 3D Q版**.

To switch back to the original theme, select **昔涟 · 云端回响（完整修复）** in CodexSkin.

## Build a pet atlas from a 4×2 pose sheet

Prepare an image with eight equal cells on a flat magenta (`#FF00FF`) background:

1. front idle
2. look left
3. look right
4. wave right hand
5. raise left hand
6. crouch
7. airborne jump
8. landing

Then run:

```bash
python3 scripts/build_pet.py \
  --input /path/to/pose-sheet.png \
  --output ./build
```

The script writes a Codex-compatible `spritesheet.webp`, `spritesheet.png`, and a QA contact sheet.

## Uninstall

```bash
rm -rf ~/.codex/pets/xilian
rm -rf ~/.codex-skin-app/themes/custom-mu0wrtsv
rm -rf ~/.codex-skin-app/themes/custom-xilian-comfort
```

Remove the matching theme ids from `~/.codex-skin-app/manifest.json` if they remain listed.

## License and assets

Scripts and configuration code are released under the MIT License.

The character artwork and derived image assets are fan-made materials for personal, non-commercial use only. Rights remain with their respective owners. See [ASSETS.md](ASSETS.md).

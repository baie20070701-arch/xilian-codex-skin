#!/usr/bin/env python3
"""Build a Codex v2 pet atlas from a 4x2 magenta pose sheet."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance

CELL = (192, 208)
ROWS = 11
COLS = 8
ORDER = [
    "idle",
    "running-right",
    "running-left",
    "waving",
    "jumping",
    "failed",
    "waiting",
    "running",
    "review",
    "look-a",
    "look-b",
]


def remove_magenta(cell: Image.Image) -> Image.Image:
    data = np.asarray(cell.convert("RGB")).astype(np.float32)
    distance = np.sqrt(
        (data[:, :, 0] - 255) ** 2
        + data[:, :, 1] ** 2
        + (data[:, :, 2] - 255) ** 2
    )
    alpha = np.clip((distance - 16) / 65, 0, 1) * 255
    rgba = np.dstack([data.astype(np.uint8), alpha.astype(np.uint8)])
    return Image.fromarray(rgba, "RGBA")


def sheet_poses(path: Path) -> list[Image.Image]:
    sheet = Image.open(path).convert("RGB")
    width, height = sheet.size
    if width % 4 or height % 2:
        raise SystemExit("pose sheet must divide evenly into a 4x2 grid")
    cell_width, cell_height = width // 4, height // 2
    poses = []
    for row in range(2):
        for col in range(4):
            box = (
                col * cell_width,
                row * cell_height,
                (col + 1) * cell_width,
                (row + 1) * cell_height,
            )
            pose = remove_magenta(sheet.crop(box))
            bbox = pose.getbbox()
            if bbox is None:
                raise SystemExit(f"empty pose at row={row}, column={col}")
            poses.append(pose.crop(bbox))
    return poses


def normalize(
    image: Image.Image,
    target_height: int,
    bottom: int = 198,
    max_width: int = 178,
) -> Image.Image:
    scale = min(target_height / image.height, max_width / image.width)
    image = image.resize(
        (max(1, round(image.width * scale)), max(1, round(image.height * scale))),
        Image.Resampling.LANCZOS,
    )
    canvas = Image.new("RGBA", CELL, (0, 0, 0, 0))
    canvas.alpha_composite(image, ((CELL[0] - image.width) // 2, bottom - image.height))
    return canvas


def transform(
    image: Image.Image,
    dx: int = 0,
    dy: int = 0,
    sx: float = 1.0,
    sy: float = 1.0,
    angle: float = 0.0,
    desaturate: float = 1.0,
    alpha: float = 1.0,
    flip: bool = False,
) -> Image.Image:
    source = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT) if flip else image
    if desaturate != 1.0:
        rgb = ImageEnhance.Color(source.convert("RGB")).enhance(desaturate)
        source = Image.merge("RGBA", (*rgb.split(), source.getchannel("A")))
    if angle:
        source = source.rotate(angle, resample=Image.Resampling.BICUBIC, expand=False)
    if sx != 1.0 or sy != 1.0:
        source = source.resize(
            (max(2, round(source.width * sx)), max(2, round(source.height * sy))),
            Image.Resampling.LANCZOS,
        )
    if alpha < 1.0:
        source.putalpha(source.getchannel("A").point(lambda p: int(p * alpha)))
    canvas = Image.new("RGBA", CELL, (0, 0, 0, 0))
    canvas.alpha_composite(
        source,
        ((CELL[0] - source.width) // 2 + dx, (CELL[1] - source.height) // 2 + dy),
    )
    bbox = canvas.getchannel("A").getbbox()
    if bbox:
        shift_x = 4 - bbox[0] if bbox[0] < 4 else 188 - bbox[2] if bbox[2] > 188 else 0
        shift_y = 4 - bbox[1] if bbox[1] < 4 else 204 - bbox[3] if bbox[3] > 204 else 0
        if shift_x or shift_y:
            moved = Image.new("RGBA", CELL, (0, 0, 0, 0))
            moved.alpha_composite(canvas, (shift_x, shift_y))
            canvas = moved
    return canvas


def build_frames(poses: list[Image.Image]) -> dict[str, list[Image.Image]]:
    front, look_left, look_right, wave, raise_left, crouch, airborne, land = poses
    base = [
        normalize(front, 178),
        normalize(look_left, 176),
        normalize(look_right, 176),
        normalize(wave, 174),
        normalize(raise_left, 174),
        normalize(crouch, 158),
        normalize(airborne, 142, bottom=158),
        normalize(land, 160),
    ]
    frames: dict[str, list[Image.Image]] = {}
    frames["idle"] = [
        transform(base[0], dy=round(1.2 * math.sin(2 * math.pi * i / 6)), sy=1 + 0.012 * math.sin(2 * math.pi * i / 6), angle=0.8 * math.sin(2 * math.pi * i / 6))
        for i in range(6)
    ]
    frames["running-right"] = [
        transform(base[0], dx=round(4 * math.sin(2 * math.pi * i / 8)), dy=round(2 * math.sin(4 * math.pi * i / 8)), sx=0.985, sy=1 + 0.022 * math.sin(2 * math.pi * i / 8), angle=2.8 * math.sin(2 * math.pi * i / 8))
        for i in range(8)
    ]
    frames["running-left"] = [
        transform(base[0], dx=-round(4 * math.sin(2 * math.pi * i / 8)), dy=round(2 * math.sin(4 * math.pi * i / 8)), sx=0.985, sy=1 + 0.022 * math.sin(2 * math.pi * i / 8), angle=-2.8 * math.sin(2 * math.pi * i / 8), flip=True)
        for i in range(8)
    ]
    frames["waving"] = [
        transform(base[3], dx=[0, 1, 3, 1][i], dy=[2, -2, -6, -1][i], sx=[1, 1.02, 1.04, 1.01][i], sy=[1, 0.99, 0.97, 1.01][i], angle=[-2, 2, 5, 1][i])
        for i in range(4)
    ]
    frames["jumping"] = [
        transform(base[5], dy=4, sx=1.03, sy=0.96),
        transform(base[6], dy=-34, sx=0.96, sy=1.02),
        transform(base[6], dy=-44),
        transform(base[6], dy=-28, sx=0.98, sy=1.02),
        transform(base[7], dy=2, sx=1.01, sy=0.98),
    ]
    frames["failed"] = [
        transform(base[7], dy=5 + round(math.sin(2 * math.pi * i / 8)), sx=1.01, sy=0.98, angle=-2.5 + 0.8 * math.sin(2 * math.pi * i / 8), desaturate=0.55, alpha=0.9)
        for i in range(8)
    ]
    frames["waiting"] = [
        transform(base[4], dy=round(1.8 * math.sin(2 * math.pi * i / 6)), sy=1 + 0.018 * math.sin(2 * math.pi * i / 6), angle=1.3 * math.sin(2 * math.pi * i / 6))
        for i in range(6)
    ]
    running_seq = [base[0], base[3], base[4], base[5], base[0], base[3]]
    frames["running"] = [
        transform(p, dx=[0, -2, 2, 0, 2, -2][i], dy=[1, -3, 1, -2, 1, 2][i], sx=[0.99, 0.97, 1.01, 0.98, 0.97, 1.0][i], sy=[1.01, 1.03, 0.99, 1.02, 1.03, 1.0][i], angle=[0, -2, 2, -1, 3, -2][i])
        for i, p in enumerate(running_seq)
    ]
    review_seq = [base[0], base[1], base[2], base[1], base[0], base[2]]
    frames["review"] = [
        transform(p, dy=[1, 0, -1, 0, 1, 0][i], sx=[1, 1.02, 1.04, 1.02, 1, 1.01][i], sy=[1, 1.01, 1.02, 1.01, 1, 1.01][i], angle=[0, -2, 0, 2, 1, 0][i])
        for i, p in enumerate(review_seq)
    ]
    look_a_seq = [base[0], base[1], base[1], base[2], base[2], base[0], base[1], base[2]]
    frames["look-a"] = [
        transform(p, dx=round(1.5 * math.sin(i * math.pi / 4)), sx=0.99)
        for i, p in enumerate(look_a_seq)
    ]
    look_b_seq = [base[0], base[2], base[2], base[1], base[1], base[0], base[2], base[1]]
    frames["look-b"] = [
        transform(p, dx=-round(1.5 * math.sin(i * math.pi / 4)), sx=0.99, flip=True)
        for i, p in enumerate(look_b_seq)
    ]
    for row, name in enumerate(ORDER):
        required = [6, 8, 8, 4, 5, 8, 6, 6, 6, 8, 8][row]
        if len(frames[name]) != required:
            raise RuntimeError(f"{name}: expected {required} frames")
    return frames


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    frames = build_frames(sheet_poses(args.input))
    args.output.mkdir(parents=True, exist_ok=True)
    atlas = Image.new("RGBA", (COLS * CELL[0], ROWS * CELL[1]), (0, 0, 0, 0))
    contact = Image.new("RGBA", atlas.size, (24, 28, 42, 255))
    for row, name in enumerate(ORDER):
        for col, image in enumerate(frames[name]):
            atlas.alpha_composite(image, (col * CELL[0], row * CELL[1]))
            contact.alpha_composite(image, (col * CELL[0], row * CELL[1]))
    atlas.save(args.output / "spritesheet.png", optimize=True)
    atlas.save(args.output / "spritesheet.webp", quality=95, method=6)
    contact.convert("RGB").save(args.output / "contact-sheet.png", quality=93)
    print(json.dumps({"atlas": str(args.output / "spritesheet.webp"), "size": atlas.size}, ensure_ascii=False))


if __name__ == "__main__":
    main()

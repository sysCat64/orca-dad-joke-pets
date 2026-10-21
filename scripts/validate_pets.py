#!/usr/bin/env python3
"""Read-only validation of this collection's four 8-column, 9-row pet bundles."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import json
from pathlib import Path, PureWindowsPath
import sys
import warnings

try:
    from PIL import Image, UnidentifiedImageError
except ImportError:
    Image = None


PET_NAMES = ("orca", "dolphin", "ladybug", "penguin")
ANIMATIONS = frozenset((
    "idle", "running-right", "running-left", "waving", "jumping",
    "failed", "waiting", "running", "review",
))
FRAME_SIZE = (192, 208)
COLUMNS, ROWS = 8, 9
SHEET_SIZE = (1536, 1872)
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
# stablyai/orca@84af8efee3e4307ad13c800b45a5ab938ad4de7b:
# src/main/ipc/pet-bundle-manifest-schema.ts
TEXT_LIMITS = {"id": 128, "displayName": 120, "description": 2000, "spritesheetPath": 255}
MAX_FPS = 60
MAX_FRAME_DURATION_MS = 60_000
MAX_DURATION_COUNT = 512


@dataclass
class Result:
    bundle: Path
    pet_id: str | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    details: list[str] = field(default_factory=list)

    def error(self, code: str, message: str) -> None:
        self.errors.append(f"{code}: {message}")


def positive_number(value: object, maximum: int) -> bool:
    # bool is a subclass of int; it is not a valid duration or FPS.
    # Compare before any float conversion: enormous integers cannot overflow,
    # and NaN/infinities cannot satisfy this finite, inclusive upper bound.
    return type(value) in (int, float) and 0 < value <= maximum


def utf16_length(value: str) -> int:
    # Zod uses JavaScript String.length; supplementary characters occupy 2 units.
    return sum(2 if ord(character) > 0xFFFF else 1 for character in value)


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate JSON key {key!r}")
        obj[key] = value
    return obj


def reject_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON number {value}")


def safe_sprite_path(bundle: Path, value: object) -> Path:
    """Accept portable relative paths and contain resolved symlinks in the bundle."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("spritesheetPath must be a non-empty relative path")
    if utf16_length(value) > TEXT_LIMITS["spritesheetPath"]:
        raise ValueError("spritesheetPath must contain at most 255 UTF-16 code units")
    if ("\\" in value or ":" in value or "\x00" in value
            or PureWindowsPath(value).drive
            or any(part in ("", ".", "..") for part in value.split("/"))):
        raise ValueError("spritesheetPath must not contain roots, drives, or traversal")
    candidate = bundle / value
    candidate.resolve().relative_to(bundle.resolve())
    return candidate


def validate_manifest(manifest: dict, result: Result) -> list[tuple[str, int, int]]:
    for name in ("id", "displayName"):
        value = manifest.get(name)
        if not isinstance(value, str) or not value.strip():
            result.error("MANIFEST_FIELD", f"{name} must be a non-empty string")
        elif utf16_length(value) > TEXT_LIMITS[name]:
            result.error("MANIFEST_FIELD", f"{name} must contain at most "
                         f"{TEXT_LIMITS[name]} UTF-16 code units")
        elif name == "id":
            result.pet_id = value
    if "description" in manifest:
        description = manifest["description"]
        if not isinstance(description, str):
            result.error("MANIFEST_FIELD", "description must be a string when supplied")
        elif utf16_length(description) > TEXT_LIMITS["description"]:
            result.error("MANIFEST_FIELD", "description must contain at most 2000 UTF-16 code units")
    if "fps" in manifest and not positive_number(manifest["fps"], MAX_FPS):
        result.error("FPS", "fps must be finite and in (0, 60] when supplied")

    frame = manifest.get("frame")
    if (not isinstance(frame, dict)
            or any(type(frame.get(key)) is not int or frame[key] <= 0
                   for key in ("width", "height"))):
        result.error("FRAME", "frame must contain positive integer width and height")
    elif (frame["width"], frame["height"]) != FRAME_SIZE:
        result.error("FRAME_SIZE", f"expected frame size {FRAME_SIZE}, got {frame}")

    animations = manifest.get("animations")
    if not isinstance(animations, dict):
        result.error("ANIMATIONS", "animations must be an object with nine states")
        return []
    if set(animations) != ANIMATIONS:
        result.error("ANIMATIONS", f"expected exactly nine states; "
                     f"missing={sorted(ANIMATIONS - animations.keys())}, "
                     f"unexpected={sorted(animations.keys() - ANIMATIONS)}")
    default = manifest.get("defaultAnimation")
    if not isinstance(default, str) or default not in animations:
        result.error("DEFAULT_ANIMATION", "defaultAnimation must name a defined state")

    used = []
    seen_rows = {}
    for name, animation in animations.items():
        if not isinstance(animation, dict):
            result.error("ANIMATION", f"{name} must be an object")
            continue
        row, frames = animation.get("row"), animation.get("frames")
        valid_row = type(row) is int and 0 <= row < ROWS
        valid_frames = type(frames) is int and 1 <= frames <= COLUMNS
        if not valid_row:
            result.error("ROW", f"{name}.row must be an integer in 0..8")
        elif row in seen_rows:
            result.error("DUPLICATE_ROW", f"{name} and {seen_rows[row]} use row {row}")
        else:
            seen_rows[row] = name
        if not valid_frames:
            result.error("FRAMES", f"{name}.frames must be an integer in 1..8")
        if valid_row and valid_frames:
            used.append((name, row, frames))

        durations = animation.get("frameDurationsMs")
        if not isinstance(durations, list):
            result.error("DURATIONS", f"{name}.frameDurationsMs must be an array")
            continue
        if valid_frames and len(durations) != frames:
            result.error("DURATION_COUNT", f"{name}: {frames} frames but "
                         f"{len(durations)} durations")
        if len(durations) > MAX_DURATION_COUNT:
            result.error("DURATION_LIMIT", f"{name}: frameDurationsMs must contain at most 512 values")
        if any(not positive_number(value, MAX_FRAME_DURATION_MS) for value in durations):
            result.error("DURATION_VALUE", f"{name}: every duration must be finite and in (0, 60000]")
    return used


def validate_image(path: Path, manifest: dict, used: list, result: Result) -> None:
    if Image is None:
        result.error("DEPENDENCY", "install requirements-validation.txt (Pillow)")
        return
    try:
        # Treat oversized-image warnings as errors and force a full pixel decode.
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(path) as image:
                if image.format != "WEBP":
                    result.error("IMAGE_FORMAT", f"expected WebP, got {image.format}")
                    return
                if getattr(image, "n_frames", 1) != 1:
                    result.error("ANIMATED_WEBP", "spritesheet must be a single static atlas")
                    return
                image.load()
                size = image.size
                result.details.append(f"WebP {size[0]}x{size[1]}, mode={image.mode}")
                if size != SHEET_SIZE:
                    result.error("SHEET_SIZE", f"expected {SHEET_SIZE}, got {size}")
                frame = manifest.get("frame")
                frame_size = None
                if (isinstance(frame, dict)
                        and all(type(frame.get(key)) is int and frame[key] > 0
                                for key in ("width", "height"))):
                    frame_size = (frame["width"], frame["height"])
                if (frame_size is not None
                        and size != (frame_size[0] * COLUMNS, frame_size[1] * ROWS)):
                    result.error("MANIFEST_IMAGE_SIZE", "image does not match frame x 8 columns x 9 rows")
                if "A" not in image.getbands():
                    result.error("ALPHA_CHANNEL", "decoded image has no alpha channel")
                    return
                alpha = image.getchannel("A")
                histogram = alpha.histogram()
                transparent, opaque = histogram[0], histogram[255]
                partial = sum(histogram[1:255])
                result.details.append(f"alpha: transparent={transparent}, "
                                      f"partial={partial}, opaque={opaque}")
                if not transparent:
                    result.error("TRANSPARENCY", "sheet has no fully transparent background pixels")
                if size != SHEET_SIZE or frame_size != FRAME_SIZE:
                    return
                opaque_cells = []
                used_cells = set()
                for name, row, frames in used:
                    for column in range(frames):
                        used_cells.add((row, column))
                        box = (column * 192, row * 208, (column + 1) * 192, (row + 1) * 208)
                        cell = alpha.crop(box)
                        if cell.getbbox() is None:
                            result.error("EMPTY_FRAME", f"{name}: row={row}, column={column} is fully transparent")
                        elif cell.getextrema()[0] > 0:
                            opaque_cells.append(f"{name}[{column}]")
                if opaque_cells:
                    result.warnings.append("FRAME_BACKGROUND: no fully transparent pixels in "
                                           + ", ".join(opaque_cells))
                result.details.append(f"checked {len(used_cells)} used frames")
    except (OSError, ValueError, UnidentifiedImageError,
            Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        result.error("IMAGE_DECODE", f"cannot decode {path.name}: {exc}")


def validate_bundle(bundle: Path) -> Result:
    result = Result(bundle)
    manifest_path = bundle / "pet.json"
    try:
        manifest_path.resolve().relative_to(bundle.resolve())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"),
                              object_pairs_hook=unique_object, parse_constant=reject_constant)
    except (OSError, ValueError, RuntimeError, RecursionError) as exc:
        result.error("MANIFEST_READ", f"cannot read pet.json: {exc}")
        return result
    if not isinstance(manifest, dict):
        result.error("MANIFEST_TYPE", "pet.json must contain an object")
        return result
    used = validate_manifest(manifest, result)
    try:
        sprite_path = safe_sprite_path(bundle, manifest.get("spritesheetPath"))
    except (ValueError, OSError, RuntimeError) as exc:
        result.error("SPRITE_PATH", f"unsafe spritesheetPath: {exc}")
        return result
    if not sprite_path.is_file():
        result.error("SPRITE_MISSING", f"missing sprite file: {sprite_path}")
        return result
    validate_image(sprite_path, manifest, used, result)
    return result


def validate_collection(root: Path) -> list[Result]:
    results = [validate_bundle(root / "pets" / name / f"{name}.codex-pet")
               for name in PET_NAMES]
    seen = {}
    for result in results:
        if result.pet_id is None:
            continue
        if result.pet_id in seen:
            other = seen[result.pet_id]
            result.error("DUPLICATE_ID", f"{result.pet_id!r} also appears in {other.bundle}")
            other.error("DUPLICATE_ID", f"{result.pet_id!r} also appears in {result.bundle}")
        else:
            seen[result.pet_id] = result
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPOSITORY_ROOT,
                        help="repository root (default: script's parent repository)")
    args = parser.parse_args(argv)
    if Image is None:
        print("ERROR: Pillow is required; run: python -m pip install -r "
              "requirements-validation.txt", file=sys.stderr)
        return 2
    results = validate_collection(args.root)
    for result in results:
        status = "FAIL" if result.errors else "WARN" if result.warnings else "PASS"
        print(f"{status} {result.bundle.name} (id={result.pet_id or '?'})")
        for message in result.details:
            print(f"  {message}")
        for message in result.errors:
            print(f"  ERROR {message}")
        for message in result.warnings:
            print(f"  WARNING {message}")
    errors = sum(len(result.errors) for result in results)
    warning_count = sum(len(result.warnings) for result in results)
    print(f"Validated {len(results)} pets: {errors} error(s), {warning_count} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

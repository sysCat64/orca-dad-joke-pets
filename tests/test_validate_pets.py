"""Use unchanged WebP copies; simulate image faults without generating/editing art."""

from copy import deepcopy
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import MagicMock, patch

from scripts import validate_pets as validator


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "pets/orca/orca.codex-pet"
SCRIPT = ROOT / "scripts/validate_pets.py"


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bundle = self.root / "pets/orca/orca.codex-pet"
        self.bundle.mkdir(parents=True)
        self.manifest = json.loads((SOURCE / "pet.json").read_text())
        shutil.copyfile(SOURCE / "spritesheet.webp", self.bundle / "spritesheet.webp")
        self.write_manifest(self.manifest)

    def write_manifest(self, manifest):
        (self.bundle / "pet.json").write_text(json.dumps(manifest), encoding="utf-8")

    def assert_error(self, code):
        result = validator.validate_bundle(self.bundle)
        self.assertTrue(any(message.startswith(code + ":") for message in result.errors),
                        (code, result.errors))
        return result

    def mock_image(self, **attributes):
        # All pixel operations use the existing, decoded atlas. No Image.new/save.
        image = validator.Image.open(SOURCE / "spritesheet.webp")
        image.load()
        self.addCleanup(image.close)
        proxy = MagicMock(wraps=image)
        proxy.format, proxy.mode, proxy.size, proxy.n_frames = "WEBP", "RGBA", image.size, 1
        for key, value in attributes.items():
            setattr(proxy, key, value)
        context = MagicMock()
        context.__enter__.return_value = proxy
        return context, proxy

    def test_valid_bundle_and_read_only(self):
        before = {p.name: (sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns)
                  for p in self.bundle.iterdir()}
        result = validator.validate_bundle(self.bundle)
        self.assertEqual([], result.errors)
        self.assertEqual([], result.warnings)
        self.assertIn("checked 57 used frames", result.details)
        after = {p.name: (sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns)
                 for p in self.bundle.iterdir()}
        self.assertEqual(before, after)

    def test_missing_bundle(self):
        result = validator.validate_bundle(self.root / "missing.codex-pet")
        self.assertTrue(result.errors[0].startswith("MANIFEST_READ:"))

    def test_missing_manifest(self):
        (self.bundle / "pet.json").unlink()
        self.assert_error("MANIFEST_READ")

    def test_invalid_json(self):
        for text in ('{', '{"id": "orca", "id": "duplicate"}',
                     '{"fps": NaN}', '{"fps": Infinity}'):
            with self.subTest(text=text):
                (self.bundle / "pet.json").write_text(text)
                self.assert_error("MANIFEST_READ")

    def test_invalid_utf8(self):
        (self.bundle / "pet.json").write_bytes(b"\xff")
        self.assert_error("MANIFEST_READ")

    def test_manifest_must_be_object(self):
        for value in (None, [], "text", 3, True):
            with self.subTest(value=value):
                self.write_manifest(value)
                self.assert_error("MANIFEST_TYPE")

    def test_required_text_fields(self):
        for field in ("id", "displayName"):
            for value in (None, "", "  ", 3, [], False):
                with self.subTest(field=field, value=value):
                    manifest = deepcopy(self.manifest)
                    manifest[field] = value
                    self.write_manifest(manifest)
                    self.assert_error("MANIFEST_FIELD")

    def test_optional_description_and_fps(self):
        manifest = deepcopy(self.manifest)
        manifest["description"] = False
        self.write_manifest(manifest)
        self.assert_error("MANIFEST_FIELD")
        for value in (0, -1, True, "8", None):
            with self.subTest(fps=value):
                manifest = deepcopy(self.manifest)
                manifest["fps"] = value
                self.write_manifest(manifest)
                self.assert_error("FPS")

    def test_frame_structure(self):
        for frame in (None, [], {}, {"width": True, "height": 208},
                      {"width": 0, "height": 208}, {"width": 192, "height": "208"}):
            with self.subTest(frame=frame):
                manifest = deepcopy(self.manifest)
                manifest["frame"] = frame
                self.write_manifest(manifest)
                self.assert_error("FRAME")

    def test_manifest_frame_size_mismatch(self):
        self.manifest["frame"]["width"] = 191
        self.write_manifest(self.manifest)
        result = self.assert_error("FRAME_SIZE")
        self.assertTrue(any(e.startswith("MANIFEST_IMAGE_SIZE:") for e in result.errors))

    def test_default_animation(self):
        for value in (None, [], {}, "absent"):
            with self.subTest(value=value):
                self.manifest["defaultAnimation"] = value
                self.write_manifest(self.manifest)
                self.assert_error("DEFAULT_ANIMATION")

    def test_animations_structure(self):
        for value in (None, [], 9):
            with self.subTest(value=value):
                self.manifest["animations"] = value
                self.write_manifest(self.manifest)
                self.assert_error("ANIMATIONS")

    def test_exact_nine_standard_animation_names(self):
        for change in ("missing", "extra", "renamed"):
            with self.subTest(change=change):
                manifest = deepcopy(self.manifest)
                if change == "extra":
                    manifest["animations"]["extra"] = deepcopy(manifest["animations"]["idle"])
                else:
                    animation = manifest["animations"].pop("review")
                    if change == "renamed":
                        manifest["animations"]["typo"] = animation
                self.write_manifest(manifest)
                self.assert_error("ANIMATIONS")

    def test_animation_must_be_object(self):
        self.manifest["animations"]["idle"] = []
        self.write_manifest(self.manifest)
        self.assert_error("ANIMATION")

    def test_duplicate_row(self):
        self.manifest["animations"]["review"]["row"] = 0
        self.write_manifest(self.manifest)
        self.assert_error("DUPLICATE_ROW")

    def test_row_types_and_bounds(self):
        for value in (None, -1, 9, True, 1.5, "1", []):
            with self.subTest(row=value):
                self.manifest["animations"]["idle"]["row"] = value
                self.write_manifest(self.manifest)
                self.assert_error("ROW")

    def test_frame_count_types_and_bounds(self):
        for value in (None, 0, -1, 9, True, 1.5, "6", []):
            with self.subTest(frames=value):
                self.manifest["animations"]["idle"]["frames"] = value
                self.write_manifest(self.manifest)
                self.assert_error("FRAMES")

    def test_frame_count_boundaries(self):
        for value in (1, 8):
            with self.subTest(frames=value):
                self.manifest["animations"]["running-right"]["frames"] = value
                self.manifest["animations"]["running-right"]["frameDurationsMs"] = [100] * value
                self.write_manifest(self.manifest)
                self.assertEqual([], validator.validate_bundle(self.bundle).errors)

    def test_duration_array_required(self):
        for value in (None, "100", {}, 100):
            with self.subTest(durations=value):
                self.manifest["animations"]["idle"]["frameDurationsMs"] = value
                self.write_manifest(self.manifest)
                self.assert_error("DURATIONS")

    def test_duration_count_mismatch(self):
        for count in (0, 5, 7):
            with self.subTest(count=count):
                self.manifest["animations"]["idle"]["frameDurationsMs"] = [100] * count
                self.write_manifest(self.manifest)
                self.assert_error("DURATION_COUNT")

    def test_positive_finite_duration_values(self):
        for value in (0, -1, True, "100", None, [], {}):
            with self.subTest(duration=value):
                durations = [100] * 6
                durations[2] = value
                self.manifest["animations"]["idle"]["frameDurationsMs"] = durations
                self.write_manifest(self.manifest)
                self.assert_error("DURATION_VALUE")
        for value in (float("nan"), float("inf"), float("-inf")):
            self.assertFalse(validator.positive_number(value, 60_000))
        self.assertTrue(validator.positive_number(0.5, 60_000))

    def test_official_text_length_boundaries(self):
        # Literal limits from Orca's schema, independent of validator constants.
        for field, maximum in (("id", 128), ("displayName", 120), ("description", 2000)):
            for length in (maximum, maximum + 1):
                with self.subTest(field=field, length=length):
                    manifest = deepcopy(self.manifest)
                    manifest[field] = "a" * length
                    self.write_manifest(manifest)
                    if length == maximum:
                        self.assertEqual([], validator.validate_bundle(self.bundle).errors)
                    else:
                        self.assert_error("MANIFEST_FIELD")

    def test_official_text_lengths_use_utf16_units(self):
        for field, maximum in (("id", 128), ("displayName", 120), ("description", 2000)):
            for suffix in ("", "a"):
                with self.subTest(field=field, suffix=suffix):
                    manifest = deepcopy(self.manifest)
                    manifest[field] = "\U0001f43e" * (maximum // 2) + suffix
                    self.write_manifest(manifest)
                    if not suffix:
                        self.assertEqual([], validator.validate_bundle(self.bundle).errors)
                    else:
                        self.assert_error("MANIFEST_FIELD")

    def test_official_sprite_path_length_boundaries(self):
        for value in ("nested/" + "a" * 243 + ".webp",
                      "/".join(["\U0001f43e" * 30] * 4 + ["xxtail.webp"])):
            with self.subTest(path=value):
                target = self.bundle / value
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(SOURCE / "spritesheet.webp", target)
                self.manifest["spritesheetPath"] = value
                self.write_manifest(self.manifest)
                self.assertEqual([], validator.validate_bundle(self.bundle).errors)
                self.manifest["spritesheetPath"] = value + "a"
                self.write_manifest(self.manifest)
                with patch.object(validator.Image, "open") as opener:
                    self.assert_error("SPRITE_PATH")
                    opener.assert_not_called()

    def test_official_numeric_boundaries(self):
        for field, maximum in (("fps", 60), ("frameDurationsMs", 60_000)):
            for value in (maximum, maximum + 0.5, maximum + 1):
                with self.subTest(field=field, value=value):
                    manifest = deepcopy(self.manifest)
                    if field == "fps":
                        manifest[field] = value
                    else:
                        manifest["animations"]["idle"][field][2] = value
                    self.write_manifest(manifest)
                    if value == maximum:
                        self.assertEqual([], validator.validate_bundle(self.bundle).errors)
                    else:
                        self.assert_error("FPS" if field == "fps" else "DURATION_VALUE")

    def test_duration_array_schema_cap_preserves_collection_count_rule(self):
        for count in (512, 513):
            with self.subTest(count=count):
                self.manifest["animations"]["idle"]["frameDurationsMs"] = [100] * count
                self.write_manifest(self.manifest)
                result = self.assert_error("DURATION_COUNT")
                # At 512 the schema's array cap passes, but the existing rule
                # requiring one duration per used frame still rejects the data.
                self.assertEqual(count > 512,
                                 any(e.startswith("DURATION_LIMIT:") for e in result.errors))

    def test_huge_integers_and_nonfinite_numbers_are_rejected(self):
        for field in ("fps", "frameDurationsMs"):
            for value in (10 ** 1000, -(10 ** 1000), 1e308,
                          float("nan"), float("inf"), float("-inf")):
                with self.subTest(field=field, value=value):
                    manifest = deepcopy(self.manifest)
                    if field == "fps":
                        manifest[field] = value
                    else:
                        manifest["animations"]["idle"][field][2] = value
                    # Exercise numeric validation directly, including NaN/Inf,
                    # without relying on the JSON parser to reject constants.
                    result = validator.Result(self.bundle)
                    validator.validate_manifest(manifest, result)
                    code = "FPS" if field == "fps" else "DURATION_VALUE"
                    self.assertTrue(any(e.startswith(code + ":") for e in result.errors))
                    self.write_manifest(manifest)
                    if type(value) is float and value != value or value in (float("inf"), float("-inf")):
                        self.assert_error("MANIFEST_READ")
                    else:
                        self.assert_error(code)

    def test_json_exponent_overflow_is_rejected(self):
        for field in ("fps", "frameDurationsMs"):
            with self.subTest(field=field):
                manifest = deepcopy(self.manifest)
                if field == "fps":
                    manifest[field] = "EXPONENT_OVERFLOW"
                else:
                    manifest["animations"]["idle"][field][2] = "EXPONENT_OVERFLOW"
                # 1e1000 is legal JSON syntax but becomes inf in Python's parser.
                text = json.dumps(manifest).replace('"EXPONENT_OVERFLOW"', "1e1000")
                (self.bundle / "pet.json").write_text(text)
                self.assert_error("FPS" if field == "fps" else "DURATION_VALUE")

    def test_unsafe_sprite_paths_never_open_image(self):
        for value in (None, "", " ", "/tmp/sprite.webp", "../sprite.webp",
                      "nested/../../sprite.webp", "C:/sprite.webp", "C:sprite.webp",
                      "\\\\host\\share\\sprite.webp", "nested\\sprite.webp",
                      "https://example.com/sprite.webp", "./spritesheet.webp",
                      "nested//sprite.webp", "spritesheet.webp\x00", [], 3):
            with self.subTest(path=value):
                self.manifest["spritesheetPath"] = value
                self.write_manifest(self.manifest)
                with patch.object(validator.Image, "open") as opener:
                    self.assert_error("SPRITE_PATH")
                    opener.assert_not_called()

    def test_safe_nested_path(self):
        (self.bundle / "nested").mkdir()
        (self.bundle / "spritesheet.webp").rename(self.bundle / "nested/spritesheet.webp")
        self.manifest["spritesheetPath"] = "nested/spritesheet.webp"
        self.write_manifest(self.manifest)
        self.assertEqual([], validator.validate_bundle(self.bundle).errors)

    def test_sprite_symlink_escape(self):
        (self.bundle / "spritesheet.webp").unlink()
        (self.bundle / "spritesheet.webp").symlink_to(SOURCE / "spritesheet.webp")
        self.assert_error("SPRITE_PATH")

    def test_manifest_symlink_escape(self):
        (self.bundle / "pet.json").unlink()
        (self.bundle / "pet.json").symlink_to(SOURCE / "pet.json")
        self.assert_error("MANIFEST_READ")

    def test_missing_sprite_and_directory_as_sprite(self):
        (self.bundle / "spritesheet.webp").unlink()
        self.assert_error("SPRITE_MISSING")
        (self.bundle / "spritesheet.webp").mkdir()
        self.assert_error("SPRITE_MISSING")

    def test_truncated_webp_decode(self):
        real_open = validator.Image.open
        truncated = (SOURCE / "spritesheet.webp").read_bytes()[:64]
        with patch.object(validator.Image, "open", side_effect=lambda _: real_open(BytesIO(truncated))):
            self.assert_error("IMAGE_DECODE")

    def test_decode_forced_beyond_header(self):
        context, image = self.mock_image()
        image.load.side_effect = OSError("truncated pixel data")
        with patch.object(validator.Image, "open", return_value=context):
            self.assert_error("IMAGE_DECODE")

    def test_wrong_image_format(self):
        context, _ = self.mock_image(format="PNG")
        with patch.object(validator.Image, "open", return_value=context):
            self.assert_error("IMAGE_FORMAT")

    def test_animated_webp_rejected(self):
        context, _ = self.mock_image(n_frames=2)
        with patch.object(validator.Image, "open", return_value=context):
            self.assert_error("ANIMATED_WEBP")

    def test_image_dimensions_mismatch(self):
        context, _ = self.mock_image(size=(1535, 1872))
        with patch.object(validator.Image, "open", return_value=context):
            self.assert_error("SHEET_SIZE")

    def test_missing_alpha(self):
        context, image = self.mock_image(mode="RGB")
        image.getbands.return_value = ("R", "G", "B")
        with patch.object(validator.Image, "open", return_value=context):
            self.assert_error("ALPHA_CHANNEL")

    def test_fully_opaque_sheet(self):
        context, image = self.mock_image()
        # Return a mocked histogram; retain real source pixels for frame checks.
        alpha = MagicMock(wraps=image.getchannel("A"))
        alpha.histogram.return_value = [0] * 255 + [1536 * 1872]
        image.getchannel.return_value = alpha
        with patch.object(validator.Image, "open", return_value=context):
            self.assert_error("TRANSPARENCY")

    def test_used_frame_fully_transparent(self):
        context, image = self.mock_image()
        alpha = MagicMock(wraps=image.getchannel("A"))
        alpha.crop.return_value = MagicMock()
        alpha.crop.return_value.getbbox.return_value = None
        image.getchannel.return_value = alpha
        with patch.object(validator.Image, "open", return_value=context):
            result = self.assert_error("EMPTY_FRAME")
        self.assertEqual(57, sum(e.startswith("EMPTY_FRAME:") for e in result.errors))

    def test_frame_background_warning(self):
        context, image = self.mock_image()
        alpha = MagicMock(wraps=image.getchannel("A"))
        alpha.crop.return_value = MagicMock()
        alpha.crop.return_value.getbbox.return_value = (0, 0, 192, 208)
        alpha.crop.return_value.getextrema.return_value = (1, 255)
        image.getchannel.return_value = alpha
        with patch.object(validator.Image, "open", return_value=context):
            result = validator.validate_bundle(self.bundle)
        self.assertEqual([], result.errors)
        self.assertTrue(result.warnings[0].startswith("FRAME_BACKGROUND:"))

    def test_extra_frame_metadata_does_not_skip_pixel_checks(self):
        self.manifest["frame"]["metadata"] = "extra fields are allowed"
        self.write_manifest(self.manifest)
        context, image = self.mock_image()
        alpha = MagicMock(wraps=image.getchannel("A"))
        alpha.crop.return_value = MagicMock()
        alpha.crop.return_value.getbbox.return_value = None
        image.getchannel.return_value = alpha
        with patch.object(validator.Image, "open", return_value=context):
            self.assert_error("EMPTY_FRAME")

    def test_duplicate_ids_marks_both_bundles(self):
        for name in validator.PET_NAMES[1:]:
            target = self.root / "pets" / name / f"{name}.codex-pet"
            shutil.copytree(self.bundle, target)
            manifest = deepcopy(self.manifest)
            manifest["id"] = "orca" if name == "dolphin" else name
            (target / "pet.json").write_text(json.dumps(manifest))
        results = validator.validate_collection(self.root)
        for result in results[:2]:
            self.assertTrue(any(e.startswith("DUPLICATE_ID:") for e in result.errors))
        for result in results[2:]:
            self.assertEqual([], result.errors)

    def test_all_four_repository_bundles_read_only(self):
        paths = sorted((ROOT / "pets").glob("*/*.codex-pet/*"))
        before = {str(p): (sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns) for p in paths}
        self.assertEqual(8, len(paths))
        results = validator.validate_collection(ROOT)
        self.assertEqual(list(validator.PET_NAMES), [r.pet_id for r in results])
        for result in results:
            self.assertEqual([], result.errors, result.bundle)
            self.assertEqual([], result.warnings, result.bundle)
        self.assertEqual(before, {str(p): (sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns)
                                  for p in paths})

    def test_cli_success_independent_of_current_directory(self):
        process = subprocess.run([sys.executable, str(SCRIPT)], cwd=self.root,
                                 capture_output=True, text=True)
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertIn("Validated 4 pets: 0 error(s), 0 warning(s)", process.stdout)

    def test_cli_failure_and_root_option(self):
        process = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root)],
                                 capture_output=True, text=True)
        self.assertEqual(1, process.returncode, process.stderr)
        self.assertIn("MANIFEST_READ", process.stdout)
        self.assertNotIn("Traceback", process.stderr)

    def test_missing_pillow_has_actionable_error(self):
        process = subprocess.run([sys.executable, "-S", str(SCRIPT)],
                                 capture_output=True, text=True)
        self.assertEqual(2, process.returncode)
        self.assertIn("requirements-validation.txt", process.stderr)
        self.assertNotIn("Traceback", process.stderr)


if __name__ == "__main__":
    unittest.main()

# Pet validation

Run from the repository root with Python 3.9 or newer. Pillow is the only external
dependency; tests use the standard library's `unittest`.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-validation.txt
.venv/bin/python scripts/validate_pets.py
.venv/bin/python -m unittest discover -s tests -v
```

Pillow must include WebP decoding support. The validator fully decodes each atlas;
a missing decoder or unreadable image is reported as an error. The validator can
also be run from any working directory: it defaults to the repository containing
the script. Use `--root /path/to/repository` to validate another local copy.

The script only reads the four named bundles under `pets/`. It never saves images,
repairs manifests, or changes pet files. Output goes to the terminal. Exit codes
are `0` for no errors (warnings are allowed), `1` for invalid pet data, and `2` for
a missing Pillow dependency or invalid command-line arguments.

## Checks

- `pet.json` must be valid UTF-8 JSON with an object at the top level. Duplicate
  keys and non-standard `NaN`/`Infinity` values are rejected.
- Required fields are non-empty `id` and `displayName`, `spritesheetPath`, `frame`,
  `defaultAnimation`, and `animations`. IDs must be unique across all four pets.
  Optional `description` must be a string; optional `fps` must be finite and in `(0, 60]`.
- Exactly these nine animation names must be present: `idle`, `running-right`,
  `running-left`, `waving`, `jumping`, `failed`, `waiting`, `running`, and `review`.
  Each state explicitly selects a unique row in `0..8`; row order can differ
  between pets. Frame counts must be integers in `1..8`. Every state needs exactly
  that many finite `frameDurationsMs` values in `(0, 60000]`. Booleans are not numbers.
- Frame size must be **192×208**, and the static WebP atlas must be **1536×1872**
  (**8 columns × 9 rows**), consistent with the manifest's frame dimensions.
- Sprite paths must be portable relative paths within the bundle. Absolute paths,
  Windows drives/UNC paths, backslashes, traversal, and symlinks escaping the bundle
  are rejected. A manifest symlink escaping the bundle is also rejected.
- An alpha channel and fully transparent background pixels must exist. The report
  counts fully transparent, partially transparent, and opaque pixels. Every used
  frame must contain visible pixels. A used frame with no fully transparent pixels
  produces a `FRAME_BACKGROUND` warning. Partial alpha is allowed.

## Official manifest limits

Limits were checked against Orca's official
[`pet-bundle-manifest-schema.ts`](https://github.com/stablyai/orca/blob/84af8efee3e4307ad13c800b45a5ab938ad4de7b/src/main/ipc/pet-bundle-manifest-schema.ts)
at commit `84af8efee3e4307ad13c800b45a5ab938ad4de7b`.

| Field | Inclusive upper limit |
| --- | --- |
| `id` | 128 UTF-16 code units |
| `displayName` | 120 UTF-16 code units |
| `description` | 2000 UTF-16 code units |
| `spritesheetPath` | 255 UTF-16 code units |
| `fps` | 60 |
| Each `frameDurationsMs` value | 60,000 ms |
| `frameDurationsMs` array | 512 elements in the official schema |

String lengths follow JavaScript/Zod semantics: a supplementary character such as
an emoji counts as two UTF-16 code units. No trimming occurs before length checks.
Values exactly at each upper limit are allowed; larger values are errors. Existing
path safety and file existence checks still apply to a path within the length limit.
For this collection, the existing 1–8 frame count and matching duration count are
stricter than the schema's 512-element array cap; 512 durations still fail the
collection's count rule. This validator retains its collection-specific required
fields and 8×9 geometry rather than accepting every schema-valid Orca manifest.
Numeric bounds reject huge integers without converting them to floats, as well as
`NaN`, infinities, and JSON exponent overflow such as `1e1000`.

This is structural and pixel validation of the existing 8×9 bundles. It does not
judge animation quality, pose semantics, or installation/runtime behavior in Orca.
Unused cells are outside the used-frame check.

Tests cover the real four bundles, invalid manifests, duplicate IDs/rows, missing
files, unsafe paths, decode failures, size/alpha issues, blank used frames, CLI
exit codes, exact/over-limit boundaries (including emoji), huge integers, and
non-finite numbers. Tests mutate only temporary manifests and copy existing WebP bytes
unchanged. Image faults use decoder mocks or an in-memory truncated byte stream;
no new artwork is generated or saved. Hashes and modification times verify that
validation leaves the existing pet files unchanged.

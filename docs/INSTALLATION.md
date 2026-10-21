# Installation

[Collection](../README.md) · [日本語の概要](../README.ja.md)

These pets are an unofficial community collection for Orca ADE. This project is not affiliated with or endorsed by Orca ADE or its developers.

## Requirements

- Orca ADE with **Settings → Experimental → Pet** and **Import .codex-pet bundle…** available. Get Orca from its [official installation page](https://www.onorca.dev/docs/install).
- A local copy of the desired `.codex-pet` directory, with both `pet.json` and `spritesheet.webp` inside it.

The menu labels below use Orca's English interface. Labels may differ when another interface language is selected.

## Get the pet files

Clone this repository:

```sh
git clone https://github.com/sysCat64/orca-dad-joke-pets.git
cd orca-dad-joke-pets
```

Alternatively, use **Code → Download ZIP** on the repository's GitHub page, then extract the archive. While the repository is private, either method requires repository access; HTTPS cloning also requires configured Git authentication.

Choose one of these directories from your local copy:

| Pet | Bundle directory, relative to the repository root |
| --- | --- |
| Orca | [pets/orca/orca.codex-pet/](../pets/orca/orca.codex-pet/) |
| Dolphin | [pets/dolphin/dolphin.codex-pet/](../pets/dolphin/dolphin.codex-pet/) |
| Ladybug | [pets/ladybug/ladybug.codex-pet/](../pets/ladybug/ladybug.codex-pet/) |
| Penguin | [pets/penguin/penguin.codex-pet/](../pets/penguin/penguin.codex-pet/) |

For example, the Orca bundle has this layout:

```text
pets/orca/orca.codex-pet/
├── pet.json
└── spritesheet.webp
```

## Import into Orca ADE

1. Open **Settings → Experimental** and enable **Pet**.
2. Click the current pet's name in Orca's status bar to open the pet menu.
3. Open **Choose pet → Import .codex-pet bundle…**.
4. Select the desired `.codex-pet` directory from the table above and confirm the selection. If the file picker takes you inside the directory, selecting its `pet.json` is also supported by Orca's importer.
5. Orca copies the bundle into its own pet storage, selects the imported pet, and makes it visible. Repeat these steps to add another pet.

Use **Choose pet** in the same status-bar menu to switch between imported pets. **Hide pet**, **Show pet**, and **Size** are also available in that menu.

Use bundle import to preserve the manifest's frame layout and animation timings. The `spritesheet.webp` file alone is a sprite atlas containing many frames.

## Troubleshooting

- **The pet menu is missing:** check that **Settings → Experimental → Pet** is enabled.
- **Bundle import is missing:** use an Orca build that includes **Import .codex-pet bundle…**. A minimum released Orca version has not been established for this collection.
- **Orca asks for a restart:** fully quit and reopen Orca. The official menu implementation distinguishes a full app restart from a window reload when the import API is unavailable.
- **“Bundle is missing pet.json.”:** select the `.codex-pet` directory itself, or its `pet.json`, rather than the repository root or a parent directory. Keep `spritesheet.webp` beside the manifest.
- **An imported pet is hidden:** choose **Show pet** from the status-bar pet menu.

## Verification and official sources

The instructions were checked on **2026-10-21** against the official [stablyai/orca](https://github.com/stablyai/orca) source at commit `505d6719c075eb0344dac86867a4e4030e970a1d`.

| Source | What was verified |
| --- | --- |
| [Experimental settings](https://github.com/stablyai/orca/blob/505d6719c075eb0344dac86867a4e4030e970a1d/src/renderer/src/components/settings/ExperimentalPane.tsx#L70-L101) | The Pet toggle in the Experimental pane. |
| [Status-bar pet menu](https://github.com/stablyai/orca/blob/505d6719c075eb0344dac86867a4e4030e970a1d/src/renderer/src/components/status-bar/PetStatusSegment.tsx) | Choose pet, bundle import, selection and visibility after import, size controls, and restart guidance. |
| [Bundle importer](https://github.com/stablyai/orca/blob/505d6719c075eb0344dac86867a4e4030e970a1d/src/main/ipc/pet-bundle-import.ts) | Directory or file selection, manifest loading, and copying the bundle into Orca's pet storage. |

This is source verification, not an in-app installation test. A minimum released version and platform-specific installation and animation behavior remain unverified. The `.codex-pet` directory name describes the package format; this guide covers Orca ADE.

Licensing remains undecided; no license has been selected for this repository.

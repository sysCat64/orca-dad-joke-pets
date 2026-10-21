# Orca Dad Joke Pets

English | [日本語](README.ja.md)

An unofficial community collection of cute animated pets for [Orca ADE](https://www.onorca.dev/), with a dad joke for every companion.

This project is not affiliated with or endorsed by Orca ADE or its developers.

## Meet the pets

| Pet | The joke | Details |
| --- | --- | --- |
| Orca | “Orca ni orca wa oruka?” — “Is there an orca in Orca?” | [Orca](pets/orca/README.md) |
| Dolphin | “Orca ni iruka wa iruka?” — “Is there a dolphin in Orca?” | [Dolphin](pets/dolphin/README.md) |
| Ladybug | “There's a bug in Orca! Don't fix it. It's my pet!” | [Ladybug](pets/ladybug/README.md) |
| Penguin | “Status: PENGUIN. Still pending...” | [Penguin](pets/penguin/README.md) |

The first two jokes play on Japanese sounds. **Orca** becomes *oruka* in Japanese, which sounds like *oru ka?* (“Is it there?”). **Iruka** means “dolphin” and sounds exactly like *iru ka?*, another way to ask “Is it there?”. The pet pages explain each joke in more detail.

Ladybug gives a software “bug” a friendlier meaning: an insect companion. Penguin pairs **Pending** with **Penguin** as a silly status label. The penguin joke is invented wordplay, not a conventional English expression.

## Installation

Use Orca's **Import .codex-pet bundle…** menu to import one of the folders below. You need an Orca build with the experimental **Pet** feature and bundle import support.

Follow the [installation guide](docs/INSTALLATION.md) for download steps, the exact menu path, troubleshooting, and official source references. The procedure has been checked against Orca's source code; installation and animation behavior have not been tested in the app during this documentation phase.

## Repository layout

```text
.
├── .gitignore
├── README.md
├── README.ja.md
├── docs/
│   └── INSTALLATION.md
└── pets/
    ├── orca/
    │   ├── README.md
    │   └── orca.codex-pet/
    ├── dolphin/
    │   ├── README.md
    │   └── dolphin.codex-pet/
    ├── ladybug/
    │   ├── README.md
    │   └── ladybug.codex-pet/
    └── penguin/
        ├── README.md
        └── penguin.codex-pet/
```

Each `.codex-pet` directory is a pet bundle containing `pet.json` and `spritesheet.webp`. Keep those files together when importing. Each manifest defines nine animation states; see the individual pet READMEs for package details.

## Validation

See [pet validation](docs/VALIDATION.md) for the read-only Python validator, dependencies, and automated tests.

## License

Licensing is undecided. No license has been selected for this repository.

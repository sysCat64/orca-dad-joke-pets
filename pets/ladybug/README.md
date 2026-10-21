# Ladybug

[Collection](../../README.md) · [Installation](../../docs/INSTALLATION.md)

A cute ladybug companion for Orca ADE.

## The joke

> There's a bug in Orca! Don't fix it. It's my pet!

In software, a “bug” is usually something to fix. This one is a little insect you invited to stay. The joke turns a bug report into a request to keep your companion around.

## Bundle

Import [ladybug.codex-pet/](ladybug.codex-pet/) using the [installation guide](../../docs/INSTALLATION.md).

| Property | Value |
| --- | --- |
| Pet ID | `ladybug` |
| Display name | Ladybug |
| Manifest | [pet.json](ladybug.codex-pet/pet.json) |
| Sprite atlas | [spritesheet.webp](ladybug.codex-pet/spritesheet.webp) |
| Frame size | 192 × 208 pixels |
| Default animation | `idle` |

The manifest defines nine animation states: `idle`, `running-right`, `running-left`, `jumping`, `waiting`, `running`, `review`, `waving`, and `failed`, with explicit frame durations. Keep the manifest and sprite atlas together inside the bundle directory.

## Project status

Part of Orca Dad Joke Pets, an unofficial community collection not affiliated with or endorsed by Orca ADE or its developers. Licensing is undecided. Installation and animation behavior have not been tested in Orca ADE during this documentation phase.

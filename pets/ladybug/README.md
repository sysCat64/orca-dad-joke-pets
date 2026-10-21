# Ladybug 🐞

[Collection](../../README.md) · [Installation](../../docs/INSTALLATION.md)

![Ladybug preview](preview.png)

A cute little ladybug companion for Orca ADE.

## The joke

> There's a bug in Orca! 🐞
> 
> Don't fix it. It's my pet! ❤️

In software development, a "bug" is something you usually want to fix.

But this bug is different. It's an adorable little companion living in Orca!

**Some bugs are worth keeping.** ❤️

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

Part of Orca Dad Joke Pets, an unofficial community collection not affiliated with or endorsed by Orca ADE or its developers. Licensed under the [MIT License](../../LICENSE). Basic in-app checks have passed. Comprehensive testing of all animation states and platforms has not yet been completed.

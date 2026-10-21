# Dolphin

[Collection](../../README.md) · [Installation](../../docs/INSTALLATION.md)

A gentle blue dolphin companion for Orca ADE.

## The joke

> Orca ni iruka wa iruka?

“Is there a dolphin in Orca?”

The Japanese word **iruka** (イルカ) means “dolphin”. Split the same sounds into *iru ka?* (いるか？), and they become “Is it there?”. The sentence asks whether Orca has a dolphin while saying *iruka* twice: once for the animal and once for the question.

## Bundle

Import [dolphin.codex-pet/](dolphin.codex-pet/) using the [installation guide](../../docs/INSTALLATION.md).

| Property | Value |
| --- | --- |
| Pet ID | `dolphin` |
| Display name | Dolphin |
| Manifest | [pet.json](dolphin.codex-pet/pet.json) |
| Sprite atlas | [spritesheet.webp](dolphin.codex-pet/spritesheet.webp) |
| Frame size | 192 × 208 pixels |
| Default animation | `idle` |

The manifest defines nine animation states: `idle`, `running-right`, `running-left`, `waving`, `jumping`, `failed`, `waiting`, `running`, and `review`, with explicit frame durations. Keep the manifest and sprite atlas together inside the bundle directory.

## Project status

Part of Orca Dad Joke Pets, an unofficial community collection not affiliated with or endorsed by Orca ADE or its developers. Licensing is undecided. Installation and animation behavior have not been tested in Orca ADE during this documentation phase.

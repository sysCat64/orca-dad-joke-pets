# Orca Dad Joke Pets

[English](README.md) | 日本語

[Orca ADE](https://www.onorca.dev/) のための、かわいいアニメーションペットを集めた非公式コミュニティコレクションです。どのペットにも、ひとつずつダジャレを添えています。

本プロジェクトは Orca ADE およびその開発者とは関係がなく、公認・推奨を受けたものではありません。

## ペットたち

| ペット | ダジャレ | 詳細 |
| --- | --- | --- |
| Orca（シャチ） | “Orca ni orca wa oruka?” — 「Orca にオルカはおるか？」 | [Orca（英語）](pets/orca/README.md) |
| Dolphin（イルカ） | “Orca ni iruka wa iruka?” — 「Orca にイルカはいるか？」 | [Dolphin（英語）](pets/dolphin/README.md) |
| Ladybug（テントウムシ） | “There's a bug in Orca! Don't fix it. It's my pet!” — 「Orca にバグが！ 直さないで。私のペットだから！」 | [Ladybug（英語）](pets/ladybug/README.md) |
| Penguin（ペンギン） | “Status: PENGUIN. Still pending...” — 「状態：ペンギン。まだ保留中……」 | [Penguin（英語）](pets/penguin/README.md) |

最初のふたつは日本語の音を使ったダジャレです。**Orca** の読み「オルカ」を「おるか？」に、**イルカ**を「いるか？」に重ねています。英語の各ペットページでも、日本語を知らない読者向けに意味を説明しています。

Ladybug は、ソフトウェアの不具合を意味する **bug** と、虫としての **bug** をかけたジョークです。Penguin は **Pending**（保留中）と **Penguin**（ペンギン）を組み合わせ、ふざけた状態表示に見立てています。これはこのコレクションのために作った言葉遊びで、一般的な英語表現ではありません。

## インストール

Orca の **Import .codex-pet bundle…** メニューから、下記のペットフォルダーを読み込みます。実験的機能の **Pet** と、ペットバンドルの読み込みに対応した Orca が必要です。

取得方法、正確なメニュー操作、トラブルシューティング、公式ソースへの参照は、[インストールガイド（英語）](docs/INSTALLATION.md)をご覧ください。手順は Orca のソースコードで確認しています。このドキュメント整備の段階では、アプリ上でのインストールやアニメーション動作は検証していません。

## リポジトリ構成

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

各 `.codex-pet` ディレクトリは、`pet.json` と `spritesheet.webp` を含むペットバンドルです。読み込む際は、このふたつのファイルを同じフォルダーに保ってください。各マニフェストには9種類のアニメーション状態が定義されています。パッケージの詳細は、各ペットの README に記載しています。

## ライセンス

ライセンスは未定です。このリポジトリのライセンスは、まだ選択していません。

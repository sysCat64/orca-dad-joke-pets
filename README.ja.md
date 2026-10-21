# Orca Dad Joke Pets

[English](README.md) | 日本語

[Orca ADE](https://www.onorca.dev/) のための、かわいいアニメーションペットを集めた非公式コミュニティコレクションです。どのペットにも、ひとつずつダジャレを添えています。

本プロジェクトは Orca ADE およびその開発者とは関係がなく、公認・推奨を受けたものではありません。

| 🐋 Orca | 🐬 Dolphin |
|:---:|:---:|
| [![Orca](pets/orca/preview.png)](pets/orca/README.md) | [![Dolphin](pets/dolphin/preview.png)](pets/dolphin/README.md) |
| 🐞 Ladybug | 🐧 Penguin |
| [![Ladybug](pets/ladybug/preview.png)](pets/ladybug/README.md) | [![Penguin](pets/penguin/preview.png)](pets/penguin/README.md) |

## ペットたち

| ペット | ダジャレ | 詳細 |
| --- | --- | --- |
| Orca（シャチ）  🐋 | “Orca ni orca wa oru ka?” — 「Orca にオルカはおるか？」 | [Orca（英語）](pets/orca/README.md) |
| Dolphin（イルカ）  🐬 | “Orca ni iruka wa iru ka?” — 「Orca にイルカはいるか？」 | [Dolphin（英語）](pets/dolphin/README.md) |
| Ladybug（テントウムシ）   🐞 | “There's a bug in Orca! Don't fix it. It's my pet!” — 「Orca にバグが！ 直さないで。私のペットだから！」 | [Ladybug（英語）](pets/ladybug/README.md) |
| Penguin（ペンギン）  🐧 | “Status: PENGUIN! Oops, I mean PENDING...” — 「状態：ペンギン！ あっ、保留中の間違い……」 | [Penguin（英語）](pets/penguin/README.md) |

最初の2つは日本語の音を使ったダジャレです。**Orca** の読み「オルカ」を「おるか？」に、**イルカ**を「いるか？」に重ねています。英語の各ペットページでも、日本語を知らない読者向けに意味を説明しています。

**Ladybug** は、ソフトウェアの不具合を意味する **bug** と、虫としての **bug** をかけたジョークです。普段なら直すべきバグも、かわいいペットなら直したくない！

**Penguin** は、**Pending**（保留中）と **Penguin**（ペンギン）を取り違えたような、遊び心のある状態表示です。このコレクションのために作った言葉遊びで、一般的な英語表現ではありません。

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

## 検証

読み取り専用のPython検証スクリプト、依存関係、自動テストの実行方法は[検証ガイド（英語）](docs/VALIDATION.md)をご覧ください。

## ライセンス

**Orca Dad Joke Pets** は [MIT License](LICENSE) で公開しています。

本リポジトリに含まれる独自のソースコード、ドキュメント、ペットの設定ファイル、キャラクター画像、スプライトシート、およびプレビュー画像の独自部分には、**プロジェクトの制作者が許諾できる権利の範囲で** MITライセンスを適用します。

MITライセンスに従い、必要な著作権表示とライセンス表示を保持することで、商用利用・改変・再配布が可能です。

**第三者の権利について：** Orca ADEの名称、商標、ロゴ、スクリーンショットに写るアプリのUIなどは本プロジェクトのライセンス対象に含まれず、それぞれの権利者の権利に従います。本プロジェクトは非公式のコミュニティ作品であり、Orca ADEや開発者との提携・公認関係はありません。

キャラクター画像はAIを利用して制作しています。著作権保護の対象にならない要素について独占的な著作権を主張するものではなく、第三者が保有する権利を許諾するものでもありません。
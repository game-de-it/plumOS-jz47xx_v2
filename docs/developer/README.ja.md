# plumOS JZ47xx_v2 開発者ガイド

[English](README.md) · [プロジェクト概要](../../README.ja.md) · [ユーザーガイド](../user/README.ja.md)

[エミュレーター別ライセンスと上流リビジョン](emulator-licenses.ja.md)

## 起動とストレージ

起動にはJZ4770向けUBIBoot、OpenDingux Linux 6.8、mininitを使います。共通ブートローダーは液晶を初期化する前に、押下でLowになる4方向の十字キー信号を確認します。方向が押されていれば、p1の `BOOTMOD.CFG` に保存した選択より優先します。機種別のカーネルファイルは、共通バイナリに各機種のDTBを連結したものです。Linux側は読み込まれたDTの `compatible` を使って機種別の設定を適用します。

| 領域 | 形式と役割 |
| --- | --- |
| SD1のp1より前 | MBRとUBIBoot。ブートローダーはセクター1から配置。 |
| SD1 p1、128 MiB | FAT32 `PLUMOSBOOT`。マウント先は `/boot`。機種別カーネル、mininit、検証済みの組であるrootfsとmodules、前回選んだ機種を保存。 |
| SD1 p2、1.5 GiB | ext4 `PLUMOSDATA`。マウント先は `/media/data`。フロントエンド、エミュレータ、アプリ、設定、セットアップ状態を管理。 |
| SD1 p3、初期値64 MiB | 初回起動時にカード末尾まで拡張し、FAT32 `PLUMOS` を作成して `/media/user` にマウント。 |
| SD2（任意） | ROM、BIOS、サムネイルを配置。通常は読み取り専用でマウント。 |

`S00expand-multimodel-user` は起動カードと初期レイアウトを確認し、p3のパーティション表とカーネルが認識するサイズを更新してから、p3をフォーマットしてマウントします。完了状態はp2に保存します。`S96remember-boot-model` は選択した機種をp1に保存します。機種切り替えでp3のセットアップ状態はリセットされません。変更時はブートローダー領域と、p1・p2の開始位置およびサイズを維持してください。

## ソース構成

| パス | 役割 |
| --- | --- |
| [configs/plumos_rg280v_defconfig](../../configs/plumos_rg280v_defconfig) | 共通MIPS基盤のBuildroot設定。 |
| [board/rg280v/overlay](../../board/rg280v/overlay) | 起動、マウント、ハードウェアサービス。 |
| [patches](../../patches) | ブートローダー、カーネル、エミュレータへの変更。 |
| [src/frontend](../../src/frontend) | フロントエンド、ライブラリ検索、描画、起動処理。 |
| [assets/frontend/systems.json](../../assets/frontend/systems.json) | ROMフォルダー別名、拡張子、起動経路のソース定義。イメージに組み込んだ定義を照合する。 |
| [assets/frontend/bin](../../assets/frontend/bin) | 機種別設定とエミュレータ起動処理。 |

## OPKアプリを開発用SDに追加する

FEの **START → Apps** はSD1のp2にある `/media/data/apps/` を走査します。対象は小文字の `.opk` で終わる通常ファイルです。ファイル名には英数字、ハイフン、アンダースコア、ピリオドを使い、先頭のピリオドや連続するピリオドは避けてください。対応する `.desktop` の `Name` と `Exec` を設定し、JZ47xx向けのMIPS実行ファイルと必要なライブラリを用意します。

1. 開発用SD1の本体をシャットダウンし、カードリーダーでLinuxに接続します。`lsblk -f` でそのカードのext4領域 `PLUMOSDATA`（p2）を確認します。
2. p2をLinux上の任意のディレクトリに読み書き可能でマウントします。たとえば `/mnt/plumos-data` にマウントした場合は、`sudo install -m 0644 my-app.opk /mnt/plumos-data/apps/my-app.opk` で配置します。
3. アンマウントしてSD1を戻し、**START → Apps** で表示・起動・FEへの復帰を確認します。

独自イメージに同梱する場合は、ビルド成果物を `output/rg280v-apps/<名前>-rg280v.opk` に用意し、[検証候補の `APPLICATIONS`](../../scripts/stage-jz47xx-validation.py) に `<名前>` を追加して再ビルドします。

## 基盤をビルドする

Git、Bash、Linux ARM64コンテナを実行できるDockerを用意します。コマンドはリポジトリのルートから実行します。Buildrootの成果物には大文字・小文字を区別するDockerボリュームを使います。ダウンロードしたソースや生成物は `work/` と `output/` に置かれます。

```sh
./scripts/configure-rg280v.sh
./scripts/build-rg280v.sh
./scripts/verify-rg280v-build.sh
```

設定スクリプトは固定したOpenDingux Buildrootのリビジョンを取得します。defconfigを変えたら設定からやり直します。共通版の4機種分のDTBと連結カーネルは [build-jz47xx-boot-in-container.sh](../../scripts/build-jz47xx-boot-in-container.sh)、機種選択対応のUBIBootは [build-jz47xx-multimodel-ubiboot-in-container.sh](../../scripts/build-jz47xx-multimodel-ubiboot-in-container.sh) で生成します。後者は上流アーカイブの照合、4機種の十字キーGPIOの検査、ブートローダーのサイズ検査を行います。

共通版の起動ファイル生成には、`output/jz47xx-multimodel/reference-boot/` に基準となるrootfs、modules、mininitが必要です。組み立て前にカーネルとの組み合わせと各ファイルの出所を確認してください。

[make-jz47xx-test-image-in-container.sh](../../scripts/make-jz47xx-test-image-in-container.sh) は、従来の開発用スナップショットを復元するスクリプトです。過去の実機結果は比較に使えます。スナップショットには実機や開発機固有のデータが含まれる場合があります。

## 同じSDイメージを検証して配布する

最終実機検証でSD1に書いた元のIMGを配布します。リリース時は、検証した機能・同梱物・起動経路・設定・サービスをすべて保持し、元のIMGを圧縮してチェックサムを作成します。バージョン情報だけを更新する場合も、最終実機検証の前に反映します。

1. 直近の検証済み構成を土台に候補を用意し、構成差分と最終検証の範囲を確認します。ソースのリビジョン、再配布条件、ユーザーデータの有無は試験前に確認します。公開について懸念が見つかった場合はユーザーに共有します。バージョン情報以外の変更が必要なら、変更内容を合意したうえで新しい候補として実機検証します。
2. 試験用SD1に書き込んだ元のIMGを保管し、実機検証の結果とSHA-256を一緒に記録します。初回起動、p3拡張、各機種への切り替えと記憶、FE操作、代表的なエミュレーターとアプリ、ユーザー領域を確認します。
3. 記録したSHA-256を指定して元IMGを圧縮します。入力のIMGと、7zを展開したIMGを照合します。元IMGは読み取りのみで扱い、7zと `SHA256SUMS` を出力します。

```sh
bash scripts/package-jz47xx-release.sh /path/to/plumOS-JZ47xx-0.1.0.img VERIFIED_SHA256
```

既定の出力先は `output/release/` です。第3引数で変更できます。7-Zip（`7zz` または `7z`）とSHA-256の計算コマンドが必要です。検証済みのアーカイブとともに日英のユーザー・開発者ガイド、必要なライセンス表記を公開します。現在の確認結果は[候補イメージの検証記録](../validation/jz47xx-release-candidate-2026-11-20.md)にあります。

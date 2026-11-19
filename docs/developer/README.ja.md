# plumOS JZ47xx 開発者ガイド

[English](README.md) · [プロジェクト概要](../../README.ja.md) · [ユーザーガイド](../user/README.ja.md)

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

## 基盤をビルドする

Git、Bash、Linux ARM64コンテナを実行できるDockerを用意します。コマンドはリポジトリのルートから実行します。Buildrootの成果物には大文字・小文字を区別するDockerボリュームを使います。ダウンロードしたソースや生成物は `work/` と `output/` に置かれます。

```sh
./scripts/configure-rg280v.sh
./scripts/build-rg280v.sh
./scripts/verify-rg280v-build.sh
```

設定スクリプトは固定したOpenDingux Buildrootのリビジョンを取得します。defconfigを変えたら設定からやり直します。共通版の4機種分のDTBと連結カーネルは [build-jz47xx-boot-in-container.sh](../../scripts/build-jz47xx-boot-in-container.sh)、機種選択対応のUBIBootは [build-jz47xx-multimodel-ubiboot-in-container.sh](../../scripts/build-jz47xx-multimodel-ubiboot-in-container.sh) で生成します。後者は上流アーカイブの照合、4機種の十字キーGPIOの検査、ブートローダーのサイズ検査を行います。

共通版の起動ファイル生成には、`output/jz47xx-multimodel/reference-boot/` に基準となるrootfs、modules、mininitが必要です。組み立て前にカーネルとの組み合わせと各ファイルの出所を確認してください。

[make-jz47xx-test-image-in-container.sh](../../scripts/make-jz47xx-test-image-in-container.sh) は**実機検証用のイメージを作る**スクリプトです。`multimodel` では動作確認済みのrootfsとmodulesの組、および既存のランタイムのスナップショットを使います。配布用イメージを作るときは、配布可能と確認した成果物をクリーンな環境で組み立て、個人データを除外してください。

[配布候補ビルダー](../../scripts/make-jz47xx-release-image-in-container.sh) はSDKコンテナ内でバージョンを引数に取り、`output/release/` にイメージとSHA-256を出力します。[同梱リストと検査処理](../../scripts/stage-jz47xx-release.py) が、個別のビルド成果物から初期状態を構築します。配布前の確認結果は[候補イメージの検証記録](../validation/jz47xx-release-candidate-2026-11-20.md)に記載しています。

## リリース準備と検証

1. ソースのリビジョン、ツールチェーン、各コンポーネントの出所を記録します。再配布条件を確認し、同梱するバイナリに対応するライセンス表記、ソース、パッチ、ビルド手順を条件に従って用意します。
2. 配布物はクリーンな作業ツリーで作成します。試験用スナップショット、ROM、再配布できないBIOS、セーブ、認証情報、端末識別子、ネットワーク設定、非公開ログを除外します。イメージ内のファイルと画像のメタデータも確認します。既存のリポジトリを公開する場合はGit履歴も確認します。
3. パーティション表とファイルシステムを検査します。イメージ内のブートローダー、4機種のカーネル、rootfsとmodulesを生成元と照合し、公開するファイルのSHA-256を作成します。
4. 予備のSD1に書き込み、初回のp3拡張、フロントエンドの起動、設定とファイルの保持、各機種への切り替え、キー入力なしでのコールドブートを確認します。同じカードを差し替えてもセットアップが再実行されないことを確認します。
5. 配布候補で液晶、物理ボタン、内蔵音声、シャットダウン、スリープを確認します。フロントエンドから代表的なタイトルを起動し、メニュー、終了後の復帰、セーブ、SD2のサムネイルを試します。結果は機種別に記録し、未検証項目を明示します。
6. イメージ、チェックサム、英語版と日本語版のユーザー・開発者ガイド、必要なライセンス表記を揃えます。公開ファイル名とチェックサムを使って、ユーザー向け導入手順を確認します。

実機検証用イメージでは、1枚のSD1を差し替えて4機種すべてで起動し、選択を記憶した後のキーなし起動も全機種で確認済みです。p3の初回拡張はRG280Vで、拡張した領域の保持は同じSD1をRG350Mに差し替えて確認しました。配布候補でも同じ項目を再検証してください。

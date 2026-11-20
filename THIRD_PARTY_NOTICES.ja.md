# plumOS JZ47xx_v2 v0.1.0 第三者ライセンス表記

[English](THIRD_PARTY_NOTICES.md)

plumOS独自のコードとフロントエンドには[MITライセンス](LICENSE)を適用します。同梱する第三者のプログラム、ライブラリ、フォント、画像素材には、それぞれの著作権表示と利用条件が適用されます。対象は4機種共通のv0.1.0 SDイメージです。ソース確認用アーカイブには、対象イメージと同梱バイナリのSHA-256、ソースの出所、確認が残る項目を収録しています。

[エミュレーター別ライセンスと上流リビジョン一覧](docs/developer/emulator-licenses.ja.md)

| 同梱物 | 表記・対応ソースの参照先 |
| --- | --- |
| Linux、UBIBoot、OpenDingux／Buildroot | `platform/target-components.csv`にバージョンと宣言されたライセンスを記録しています。`platform/licenses/`、`platform/archives/`、Buildrootのスナップショット、Linuxの設定と差分、プロジェクト側のUBIBootパッチとビルド手順を参照してください。 |
| システムライブラリと互換ライブラリ | ベースシステムの一覧と`platform/compatibility-components.tsv`を参照してください。旧版ncurses、GNU Readline、OpenSSL、libpngのソースは`runtime-sources/legacy-libraries/`にあります。OpenSSL 1.0.xの著作権表示と謝辞の要件は同梱の`LICENSE`にあります。 |
| PicoArchとLibretroコア | `runtime-sources/PicoArch/`にPicoArchのライセンスとlibpicofeの各ファイルを収録しています。`runtime-sources/libretro-*/`には各コアのライセンス原文とソースのリビジョンがあります。 |
| PCSX4ALLとソースビルドした単体エミュレータ | `runtime-provenance.json`に実行ファイルと確保したソースの対応を記録しています。各フォルダーのライセンス原文とソース内の著作権表示を維持してください。 |
| 計算機、Commander、Bard、FFPlay、GMU、SDL Terminal、PDF Viewer | `runtime-sources/provided-app-archives/`に確保したアプリのソースとライセンスを収録しています。OPK内のライブラリも個別に確認が必要です。FFPlayとFFmpegライブラリには同梱版のビルド設定に応じた条件が適用されます。 [FFmpegのライセンス要件](https://ffmpeg.org/legal.html) |
| Noto Sans JP、WenQuanYi Micro Hei、画像素材 | `as-shipped-notices/`にイメージ内のフォント表記を収録しています。Noto Sans JPにはOFL 1.1、WenQuanYi Micro HeiはApache 2.0またはフォント埋め込み例外付きGPLv3で提供され、イメージにはApacheの表記が入っています。フロントエンドの機種ロゴと既成OPK由来の画像素材は個別に再配布条件を確認します。 [WenQuanYiの原文](https://sources.debian.org/src/fonts-wqy-microhei/0.2.0-beta-3.1/README.txt) |

[再配布監査の詳細](docs/validation/jz47xx-v0.1.0-release-rights.ja.md)に追加のソース・画像照合と、OPK内共有ライブラリ34ファイルの結果を記録しています。

## 個別の条件があるもの

- **fMSX**は非商用の独自ライセンスです。原著作者の表記を残し、改変していないLibretro版を配布候補に収録します。上流の配布条件に関する確認状況は再配布監査に記録しています。対象版の原文は`runtime-sources/libretro-fmsx/LICENSE`です。 [fMSXのドキュメント](https://docs.libretro.com/library/fmsx/)
- **PicoDrive**には非商用の条件があります。単体版とLibretroコアの両方について、改変版のソースと著作権表示を配布する条件を`COPYING`で確認できます。 [PicoDriveのライセンス原文](https://github.com/irixxxx/picodrive/blob/master/COPYING)
- **Snes9x 2005、Snes9x 2005 Plus、ChimeraSNES**には非商用条件のあるSnes9x由来のコードが含まれます。バイナリ再配布と著作権表記の条件は各`copyright`または`LICENSES`を参照してください。 [Snes9x 2005の著作権表記](https://github.com/libretro/snes9x2005/blob/master/copyright)
- **FBA44**は非商用です。配布候補に収録します。ライセンス全文の掲載、変更の公開、利益・寄付、発売時期の近いゲームへの対応、ROMの同梱、動的ライブラリの利用に関する条件があります。`runtime-sources/FBA44/src/license.txt`の全文と、取り込まれたMAMEその他のコードの表記を維持します。
- **blueMSX**には複数のライセンスが適用されます。`runtime-sources/libretro-bluemsx/license.txt`と、各ソースファイルの表記を参照してください。

## 公開前に完了が必要な確認

1. PocketSNES 2019、FCEUX 2.2.3、RACEの対応ソースを確定するか、ソースが明確な置換版を検証します。PokeMini GCW0の対応ソースとminizipは補足アーカイブに収録済みです。FCEUX 2.6.6 GCW0とGambatte-DMS 2020／2021は、実行ファイルが公式配布版と一致し、対応するリリースタグのソースを収録済みです。 [FCEUXのリリース](https://github.com/plrguez/fceux-for-retrogame/releases/tag/2023-08-30) [Gambatte-DMSのリリース](https://github.com/bardeci/gambatte-dms/releases)
2. 保存済みパッケージとビルド時点のソースとの対応など、バイナリ一覧で確認が残る項目を解消します。OPK内の共有ライブラリ34ファイルの出所は補足アーカイブで特定済みです。対応ソースの提供が必要な場合は、同梱版の改変ソースとビルド・インストールに必要なファイルを収録します。該当するライブラリについては、ライセンス原文に加えて再リンクの要件も確認します。
3. 個別条件のあるコンポーネントと画像素材の再配布条件を確認し、必要な表記をSDイメージ内とダウンロード先に置きます。公開するビルドに対応したソースとSHA-256をSDイメージと同じ場所から取得できるようにします。

現時点のアーカイブは入手・照合できたソースの確認用です。現在のイメージ全体の対応ソースとして公開するには、上記の確認が残っています。

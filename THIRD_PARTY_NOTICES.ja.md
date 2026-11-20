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

## 画像・フォントの著作者表示

以下の条件は表に記載した素材に適用されます。配布物には該当する著作権表示とライセンス原文を添付します。

| 検証済みIMGの素材 | 作者・権利者 | 出典・ライセンス |
| --- | --- | --- |
| plumOS起動ロゴ | plumOSプロジェクト | [原版の著作者表示](https://github.com/game-de-it/plumOS-Bubble/blob/main/THIRD_PARTY_NOTICES.md)。JZ47xx_v2では起動画像用の形式に変換しています。 |
| plumOS FEの共通アイコンとROMギャラリー背景 | plumOS contributors（plumOS制作部分） | [plumOS A30の元画像](https://github.com/game-de-it/plumOS-A30/tree/68d92d5d950f4d2e247316cf0d7bac776e6d6861/package/frontend/plumos/themes/default) · [同梱用の出典・MIT表記](assets/frontend/licenses/plumOS-frontend-artwork-NOTICE.txt)。第三者の商標等は各権利者に帰属します。 |
| GMenu2XのOpenDinguxアイコン、機種カテゴリ画像、ボタン画像 | Paul Cercueil | [テーマの原版と表記](https://github.com/OpenDingux/gmenu2x-theme/blob/17682816622b31008bb9a498c78797a02aeae166/README)、[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。OpenDinguxが原版を2種類の画面サイズ用のPNGに変換しています。 |
| PocketSNESの背景とアイコン | hi-ban | [上流の素材とライセンス表記](https://github.com/soarqin/PocketSNES/blob/1a627d83288721fba1eb14d08eefa22860a05e0e/dist/PocketSNES.man.txt)、[CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/)。差し替え用OPKは上流の元画像を使用します。 |
| SimpleMenu 0Aのテーマ作者による画像 | FGL82、RafaVico。RafaVicoのPixelテーマが原案。 | [0Aの作者表記と原文](https://github.com/fgl82/simplemenu/blob/e70a861b1f05fd83cd1b19be53be11c0a0ecd510/simplemenu/output/OD/themes/320x240/0A/README.md)、[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)。外部から取り込んだ画像とフォントには個別の条件が適用されます。 |
| SimpleMenu 0Aのロゴの出典 | rxbrad（GBZ35）、GBZ35が参照するCarbonなどの素材作者、各ロゴ・商標の権利者 | [GBZ35のCC BY-NC-SA 3.0表記と出典](https://github.com/rxbrad/es-theme-gbz35/blob/05895874b2920ab6ffeeb574d053f3d9e976c000/README.md) · [Carbonのロゴ注記](https://github.com/RetroPie/es-theme-carbon)。0Aの個別画像に関する確認状況は[画像監査](docs/validation/jz47xx-v0.1.0-release-rights.ja.md#simplemenu-0a-の画像と同梱アーカイブ)を参照。 |
| SimpleMenu 0AのBebas Neue Bold 1.300 | Ryoichi Tsunekawa（Dharma Type） | [作者の更新履歴](https://github.com/dharmatype/Bebas-Neue/blob/master/FONTLOG.txt)。同梱フォントの表記は[SIL OFL 1.1](https://openfontlicense.org/open-font-license-official-text/)です。 |
| SimUIの作者による画像とレイアウト | Dariusz Kuśnierek（dkodr） | [SimUI v1.2のMITライセンス](https://github.com/dkodr/SimUI/blob/13d35f79f9b6c75f034c51838496aa922b272045/LICENSE)。上流の原文をテーマと一緒に保持します。 [同梱用原文](assets/frontend/licenses/SimUI-MIT.txt) |
| 350tericのFlatスキン | peeweek、GoogleのMaterial Design Icons | [FlatのCC0 1.0原文](https://github.com/peeweek/gmenu2x-skin-flat/blob/e613a6b677ae4c6f74b6135b777005ede2b0a041/LICENSE.md) · [Material Design IconsのApache 2.0表記](https://github.com/peeweek/gmenu2x-skin-flat/blob/e613a6b677ae4c6f74b6135b777005ede2b0a041/3DRPARTY-LICENSE.md)。同梱の上流通知を保持します。 |
| CrystalMenuのM+ビットマップフォント | COZ | [M+ BITMAP FONTSのライセンス](https://sources.debian.org/src/xfonts-mplus/1%3A2.2.4-6/LICENSE_E/)、[Pyxelのサンプル素材](https://github.com/kitao/pyxel/tree/ddff52645739c4a4d1575b85e87c16681a45514a/python/pyxel/examples/assets)。同梱のBDF 2本はPyxelの配布物と一致し、M+の許諾原文を付属しています。 |
| Noto Sans JP | Adobe、Googleとの共同開発。フォントに西塚涼子、Paul D. Hunt、Sandoll Communications、Soo-young Jang、Joo-yeon Kangの記載があります。 | [Noto上流プロジェクト](https://github.com/notofonts/noto-cjk)、[同梱のSIL OFL 1.1原文](assets/frontend/licenses/NotoSansJP-OFL.txt)。 |
| WenQuanYi Micro Hei | WenQuanYi Board of Trustees、Qianqian Fang。デジタル化データはGoogle。 | [上流README](https://sources.debian.org/src/fonts-wqy-microhei/0.2.0-beta-3.1/README.txt)、[同梱のApache 2.0原文](assets/frontend/licenses/WQYMicroHei-Apache-2.0.txt)。上流はフォント埋め込み例外付きのGPLv3も選択肢にしています。 |

## 個別の条件があるもの

- **fMSX**は今回の配布候補から外しました。MSXの既定経路はblueMSXです。
- **PicoDrive**には非商用の条件があります。単体版とLibretroコアの両方について、改変版のソースと著作権表示を配布する条件を`COPYING`で確認できます。 [PicoDriveのライセンス原文](https://github.com/irixxxx/picodrive/blob/master/COPYING)
- **Snes9x 2005、Snes9x 2005 Plus、ChimeraSNES**には非商用条件のあるSnes9x由来のコードが含まれます。バイナリ再配布と著作権表記の条件は各`copyright`または`LICENSES`を参照してください。 [Snes9x 2005の著作権表記](https://github.com/libretro/snes9x2005/blob/master/copyright)
- **Temper**は今回の配布候補から外しました。PC Engineの既定経路はBeetle PCE Fastです。[過去の再配布監査](docs/validation/jz47xx-v0.1.0-release-rights.ja.md#temper-の再配布条件)
- **FBA44**は非商用です。配布候補に収録します。ライセンス全文の掲載、変更の公開、利益・寄付、発売時期の近いゲームへの対応、ROMの同梱、動的ライブラリの利用に関する条件があります。`runtime-sources/FBA44/src/license.txt`の全文と、取り込まれたMAMEその他のコードの表記を維持します。
- **blueMSX**には複数のライセンスが適用されます。`runtime-sources/libretro-bluemsx/license.txt`と、各ソースファイルの表記を参照してください。

## 公開前に完了が必要な確認

1. RACE、PocketSNES、FCEUX 2.2.3は対応ソースを付属した差し替え版をRG350Mで確認済みです。差し替え版は4機種で起動確認した候補に収録済みです。PokeMini GCW0の対応ソースとminizipは補足アーカイブに収録済みです。FCEUX 2.6.6 GCW0とGambatte-DMS 2020／2021は、実行ファイルが公式配布版と一致し、対応するリリースタグのソースを収録済みです。 [FCEUXのリリース](https://github.com/plrguez/fceux-for-retrogame/releases/tag/2023-08-30) [Gambatte-DMSのリリース](https://github.com/bardeci/gambatte-dms/releases)
2. 保存済みパッケージとビルド時点のソースとの対応など、バイナリ一覧で確認が残る項目を解消します。OPK内の共有ライブラリ34ファイルの出所は補足アーカイブで特定済みです。対応ソースの提供が必要な場合は、同梱版の改変ソースとビルド・インストールに必要なファイルを収録します。該当するライブラリについては、ライセンス原文に加えて再リンクの要件も確認します。
3. 個別条件のあるコンポーネントと画像素材の再配布条件を確認し、必要な表記をSDイメージ内とダウンロード先に置きます。公開するビルドに対応したソースとSHA-256をSDイメージと同じ場所から取得できるようにします。

現在の候補ではSimple Questの2版とArtBookを外し、350tericの共通フォントをNoto Sans JPに差し替えました。CrocoDSの単体版とPicoArch版は利用者のBIOSを参照します。残る公開条件と対応ソースは監査記録を参照してください。[現行候補の検証](docs/validation/jz47xx-v0.1.0-update-validation.md) · [再配布監査](docs/validation/jz47xx-v0.1.0-release-rights.ja.md)

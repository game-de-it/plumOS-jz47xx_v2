# v0.1.0 同梱物の再配布監査

[English](jz47xx-v0.1.0-release-rights.md)

対象は4機種共通SDイメージです。非圧縮イメージのSHA-256は `ac6d8a38cc802001992ea233774de38d7405de678ad66c43438cbb92545d6f2c` です。補足アーカイブに個別のハッシュ、ソース、ライセンス原文を収録しています。

## 既成OPKの対応ソース

| 同梱版 | 照合結果 |
| --- | --- |
| PokeMini 0.60 GCW0 | gameblablaの `37e3324ebf481a5f6ece725ae5c052332e3b84d1` にあるOPKが元の配布OPKと一致し、同コミットのGCW0実行ファイルもイメージの実行ファイルとSHA-256が一致。コミットで欠けているminizipはJustBurnの0.60版から確保し、後日移植元で復元されたツリーと同一であることを確認。組み込みのFreeBIOSは上流のバイト列と一致し、アセンブリと生成済みCソースを収録した。 [GCW0移植元](https://github.com/gameblabla/pokemini/tree/37e3324ebf481a5f6ece725ae5c052332e3b84d1) [PokeMini 0.60ソース](https://sourceforge.net/p/pokemini/code/ci/801da9e5f53a14857852c5eb9a0ddf299c666a47/tree/) |
| FCEUX 2.2.3-interim | Soar Qinの `bf89b7fd8b879cae6390bb1bbf41e71a88d53b03` が有力。2019-11-15の変更で導入された連射パターンの文字列とGUI用BMP 2点が同梱版と一致。現行SDKでソフトフロート版をビルドできた。旧版の実行ファイルとはSHA-256と依存ライブラリが異なるため、旧版の厳密な対応関係と新ビルドの実機互換性は未確定。 [2019-11-15のソース変更](https://github.com/soarqin/fceux-for-retrogame/commit/bf89b7fd8b879cae6390bb1bbf41e71a88d53b03) |
| PocketSNES 2019-12-12 | Soar Qinの公式20191111 OPKを展開し、公開Git履歴内の7個の実行ファイルも照合した。すべて同梱の12月版とは異なる。12月版に対応するソースは未確定。 [公式20191111配布](https://github.com/soarqin/PocketSNES/releases/tag/20191111) |
| RACE GCW-ZERO V1.2 | 同梱READMEは2013-09-21版で、ステートセーブとBIOS対応を記載。Alekmaulの公開ソースはそれらの変更を含むV1.2ツリーと確認できない。元OPKと公開コードの対応は未確定。 [Alekmaulの公開ソース](https://github.com/alekmaul/race) |

PokeMiniのGPLv3原文とFBA44のライセンス全文を、次のイメージ生成で該当OPKと共通ライセンスディレクトリに収録するようにした。ステージ生成後に原文を照合し、両OPKの実行ファイルが監査対象と一致することを確認した。

## OPK内の共有ライブラリ

対象の34ファイル（重複を除くと24バイナリ）は、保存済みのSDK／ソースツリーの出力、またはレシピと同じMIPS用ストリップ処理を施した出力と一致した。補足アーカイブの `opk-library-provenance.json` にファイル単位のSHA-256、ライセンス原文の位置、動的依存関係を記録した。

| OPK | 出所 |
| --- | --- |
| Handy、Oswan、SMS Plus GG／MS、Stella、UAE4All | SDKのSDL_image 1.2系（`5d792dde`）とlibpng 1.6.40 |
| Bard | SDKのFlite 2.2（6本）とlibzip 1.10.1 |
| GMU | GMUの同一ビルドから4プラグイン。SDKのFLAC 1.4.3、mpg123 1.32.3、Ogg 1.3.5、Tremor `7c30a663` |
| FFPlay | `0ffa36e68a70ef9e3a6d3555427c60df98453edc` のビルドツリーからFFmpeg 7本。配布バイナリの設定にはGPL・version3・nonfreeの有効化フラグがなく、FFPlayはライブラリに動的リンクする。 [FFmpegの配布条件](https://ffmpeg.org/legal.html) |

ソースの取得先と原文に加え、公開時には適用されるLGPLのライブラリ交換・デバッグ条件を維持する。FFPlayのソースは同じ公開先に置き、ダウンロードページにもFFmpegの利用とライセンスを明記する。

## fMSX、FBA44、画像素材

- **fMSX**は改変のないLibretroソース `4de11755` からのビルド。作者の一般案内は著作者表示付きの非商用利用を認め、同梱版の原文は移植・改変について作者への連絡を求めている。plumOSでのバイナリ再配布に適用できる明示的な回答は確認できていない。上流の12個のROMと照合し、それらの完全なバイト列が同梱コアに埋め込まれていないことを確認した。 [作者の案内](https://www.emulation.org/) [同梱版のライセンス](https://github.com/libretro/fmsx-libretro/blob/4de11755ce4f196ac1c8a7bb20bb4eccbc87a7d4/LICENSE)
- **FBA44**はソースと実行ファイルを照合済み。上流ライセンスは原文の掲載、変更の公開、営利・寄付・新しいゲーム・ROM・DLLに関する条件を定めている。ドライバー宣言から抽出した12,085件の年情報では判読できた最新が2019年で、540件には年範囲、注記、または年の不明が含まれる。日付表記の検査で各ゲームの権利を確定したわけではない。実行ファイルはSDL、SDL_image、libpng、zlib、ALSA等に動的リンクする。ネットプレイ以外のDLLを制限する条項が今回のLinux共有ライブラリにどう適用されるか確認が残る。 [このビルドのFBAライセンス原文](https://github.com/plrguez/fba-sdl/blob/9448a9c6f1040ad8ec204b5e9cb83e25574ac0c8/src/license.txt)
- **画像素材**は677ファイルを照合。起動ロゴはV90S原版から同じ変換を行うと一致した。FEの31画像はV90S・A30・Bubbleの既定テーマと一致する。共通起動ロゴはBubbleの上流記録でplumOS所有のデザインと明記されている。機種ロゴ等の第三者由来部分については、同じ画像が各リポジトリにあることまで確認できた。個別の著作者表示や再配布条件は確認が残る。 [V90Sのライセンス表記](https://github.com/game-de-it/plumOS-V90S_V2/blob/main/THIRD_PARTY_NOTICES.md) [A30のライセンス表記](https://github.com/game-de-it/plumOS-A30/blob/main/THIRD_PARTY_NOTICES.md)
- **OpenDinguxの画像**はrootfsの410点がGMenu2XかBuildrootのソースと一致した。OpenDinguxテーマのPNGはPaul CercueilのCC BY 4.0で、帰属表示と上流SVGへのリンクを確認した。既定テーマの壁紙には別のCC条件が記載されており、テーマ全体を同じライセンスとして扱えない。OPK内235点のうち232点はソースまたは保存済みOPKと一致した。PocketSNESの2点とRACEのアイコンは対応する元画像を確定できていない。OPKステージとの一致だけでライセンスが確定しない画像も残る。 [OpenDinguxテーマ](https://github.com/OpenDingux/gmenu2x-theme) [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

この監査で確定したのは対応資料とライセンス原文です。公開するSDイメージは、未確定項目に対する許諾の確認または配布構成の変更、構成変更後の実機検証を経て確定する。

## 現行の配布候補での追加照合

対象は `plumOS-JZ47xx-0.1.0.img`、非圧縮SHA-256は `97767f5fde51de275c148ae8b3b55fbdf7391ef2059202d1e88f9d643e0dae65`。実行ファイルは上記の監査時点と同一で、日英のライセンス表記とFBA44・PokeMiniのライセンス原文を収録済み。

| 旧版 | 今回確認できたこと |
| --- | --- |
| FCEUX 2.2.3-interim | 元のOPKに記録された実行ファイルとGUI画像2点の更新日は2019-11-15。連射パターンが追加された `bf89b7fd` の著者日付と一致し、ELFには旧Buildroot GCC 4.9.1の識別子がある。公開リリースにある10月版は連射追加前。当時のアーカイブにある11月版OPKが元OPKとSHA-256で一致し、同アーカイブの一覧もSoar Qinのツリーを案内している。[当時の配布一覧](https://github.com/SeongGino/RetroGame350-AppRepo/blob/d7e0cde52b4e5d86df5644d595ec128816205b69/README.md) 11月版を生成した作者の元ビルド一式は確保できていない。 [連射パターンを追加した変更](https://github.com/soarqin/fceux-for-retrogame/commit/bf89b7fd8b879cae6390bb1bbf41e71a88d53b03) [作者の公開リリース](https://github.com/soarqin/fceux-for-retrogame/releases) |
| PocketSNES 2019-12-12 | 同梱ELFには `PocketSNES - built Dec 13 2019` と入っている。ROGUE 1.7.10の作者配布OPKは2020-06-29の別ビルドで、実行ファイルのSHA-256は異なる。Ninoh-FOXの公開ツリーには2019-11-25のGoldfinger変更と2020-06-29の移植変更がある。同梱ELFには前者が追加したメニュー文字列 `Cheats` がなく、Goldfinger版とは一致しなかった。当時の配布一覧では同一ハッシュの12月版OPKのソースとしてSoar Qin版が案内されている。MIPS逆アセンブルでは12月版の押下イベントとキー状態がSDLK_HOME（278）を参照し、11月配布版のSDLK_END（279）と異なる。押下イベント処理を追加した `0a13add` と、その後ビルド設定だけを変更した `1a627d8` が有力。正確なビルド設定は未確定。 [当時の配布一覧](https://github.com/SeongGino/RetroGame350-AppRepo/blob/d7e0cde52b4e5d86df5644d595ec128816205b69/README.md) [キー処理の変更](https://github.com/soarqin/PocketSNES/commit/0a13addffd8868d23e03f02a93df8e41c954cd41) [ビルド設定の変更](https://github.com/soarqin/PocketSNES/commit/1a627d83288721fba1eb14d08eefa22860a05e0e) [ROGUE 1.7.10](https://github.com/Ninoh-FOX/RG350-ROGUE-CFW/releases/tag/1.7.10) [Goldfinger変更](https://github.com/Ninoh-FOX/PocketSNES/commit/2fa8a3cb8418e043910e7094db2b89fe2461a35c) |
| RACE GCW-ZERO V1.2 | AlekmaulツリーのOpenDingux用READMEの変更履歴はV1.1まで。同じ公開履歴を継承する複数のフォークを調べ、retrofw版のステートセーブ実装は2020年の別系統と確認した。両方のカタログ配布OPKの本体が同梱ELFとSHA-256で一致し、アイコンはデコード後の32×32 RGBAが一致する。2013-09-21版の対応ソース、アイコンの制作者と再配布条件は未確定。 [Alekmaulのソース](https://github.com/alekmaul/race/blob/ed8deb0223c76a63dda53f34cdda9ed15c5573a1/opendingux/readme-od.txt) [retrofwのステートセーブ変更](https://github.com/retrofw/race-od/commit/2982e9cb74d69d8cb8761e8b3882709ac0905add) |

- **PocketSNESの画像**は `backdrop.png` がhi-banを記載したコミットの `data/pocketsnes_bg.png` とバイト一致。`sfc.png` はSoar Qin版の `opk/sfc.png` とデコード後の32×32 RGBAが一致した。上流履歴はSuper Famicomアイコンもhi-ban作と記録している。画像固有の再配布条件は確認できていない。 [背景の上流記録](https://github.com/Ninoh-FOX/PocketSNES/commit/8070247148a082d90549b650352c53fe0c0da34b) [アイコンの上流記録](https://github.com/soarqin/PocketSNES/commit/39f2a8e086f35bb49124c394111233e74103278d)
- **fMSX**は非商用表記と著作者表示を付けて候補に維持した。作者が、別プロジェクトにfMSXが同梱された件で、許可を求められていないと指摘した公開投稿も確認した。plumOSでのLibretroバイナリ再配布を対象とする作者の回答は未確認。 [同梱版の原文](https://github.com/libretro/fmsx-libretro/blob/4de11755ce4f196ac1c8a7bb20bb4eccbc87a7d4/LICENSE) [作者の公開投稿](https://jonathan-cauldwell.itch.io/multi-platform-arcade-game-designer/comments?after=65)
- **FBA44**は非商用表記、原文、変更ソースを用意し、候補に維持した。上流Fix 06の `fbasdl.dge` と候補のELFの `DT_NEEDED` を比較すると、SDL、SDL_image、zlib、libpng、C/C++ランタイムが共通。音声出力は上流が `libao.so.4`、候補が `libasound.so.2`。上流配布物も動的リンクを使っているが、DLL条項の適用範囲を説明する権利者の文書は確認できていない。 [上流Fix 06](https://github.com/plrguez/fba-sdl/releases/tag/r19_2021-10-18-.44_od_beta-fix-06) [原文](https://github.com/plrguez/fba-sdl/blob/9448a9c6f1040ad8ec204b5e9cb83e25574ac0c8/src/license.txt)
- **Temper**はExophaseが2015年にPandora／GP2X系ソースの利用を呼びかけ、特定のPandora用バイナリの掲載を承諾した投稿を確認した。当時のアーカイブURLから取得できるのは現在HTMLのみ。同梱するGCW0派生版に適用される条件の確認は残る。 [作者の投稿 #122・#124](https://pyra-handheld.com/boards/threads/temper-split-from-other-thread.63264/page-7)

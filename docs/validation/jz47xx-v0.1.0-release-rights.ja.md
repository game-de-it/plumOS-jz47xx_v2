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
- **OpenDinguxの画像**はrootfsの410点がGMenu2XかBuildrootのソースと一致した。OpenDinguxテーマのPNGはPaul CercueilのCC BY 4.0で、帰属表示と上流SVGへのリンクを確認した。既定テーマの壁紙には別のCC条件が記載されており、テーマ全体を同じライセンスとして扱えない。OPK内235点のうち232点はソースまたは保存済みOPKと一致した。PocketSNESの画像2点は後続の照合で元画像とCC BY-SA 3.0の表記を確認した。RACEのアイコンは引き続き確認が必要。OPKステージとの一致だけでライセンスが確定しない画像も残る。 [OpenDinguxテーマ](https://github.com/OpenDingux/gmenu2x-theme) [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

公開判断は冒頭の監査結果と末尾の「v0.1.0の公開判断」を参照する。

## 現行の配布候補での追加照合

対象は `plumOS-JZ47xx-0.1.0.img`、非圧縮SHA-256は `97767f5fde51de275c148ae8b3b55fbdf7391ef2059202d1e88f9d643e0dae65`。実行ファイルは上記の監査時点と同一で、日英のライセンス表記とFBA44・PokeMiniのライセンス原文を収録済み。

| 旧版 | 今回確認できたこと |
| --- | --- |
| FCEUX 2.2.3-interim | 元のOPKに記録された実行ファイルとGUI画像2点の更新日は2019-11-15。連射パターンが追加された `bf89b7fd` の著者日付と一致し、ELFには旧Buildroot GCC 4.9.1の識別子がある。公開リリースにある10月版は連射追加前。当時のアーカイブにある11月版OPKが元OPKとSHA-256で一致し、同アーカイブの一覧もSoar Qinのツリーを案内している。[当時の配布一覧](https://github.com/SeongGino/RetroGame350-AppRepo/blob/d7e0cde52b4e5d86df5644d595ec128816205b69/README.md) 11月版を生成した作者の元ビルド一式は確保できていない。 [連射パターンを追加した変更](https://github.com/soarqin/fceux-for-retrogame/commit/bf89b7fd8b879cae6390bb1bbf41e71a88d53b03) [作者の公開リリース](https://github.com/soarqin/fceux-for-retrogame/releases) |
| PocketSNES 2019-12-12 | 同梱ELFには `PocketSNES - built Dec 13 2019` と入っている。ROGUE 1.7.10の作者配布OPKは2020-06-29の別ビルドで、実行ファイルのSHA-256は異なる。Ninoh-FOXの公開ツリーには2019-11-25のGoldfinger変更と2020-06-29の移植変更がある。同梱ELFには前者が追加したメニュー文字列 `Cheats` がなく、Goldfinger版とは一致しなかった。当時の配布一覧では同一ハッシュの12月版OPKのソースとしてSoar Qin版が案内されている。MIPS逆アセンブルでは12月版の押下イベントとキー状態がSDLK_HOME（278）を参照し、11月配布版のSDLK_END（279）と異なる。押下イベント処理を追加した `0a13add` と、その後ビルド設定だけを変更した `1a627d8` が有力。正確なビルド設定は未確定。 [当時の配布一覧](https://github.com/SeongGino/RetroGame350-AppRepo/blob/d7e0cde52b4e5d86df5644d595ec128816205b69/README.md) [キー処理の変更](https://github.com/soarqin/PocketSNES/commit/0a13addffd8868d23e03f02a93df8e41c954cd41) [ビルド設定の変更](https://github.com/soarqin/PocketSNES/commit/1a627d83288721fba1eb14d08eefa22860a05e0e) [ROGUE 1.7.10](https://github.com/Ninoh-FOX/RG350-ROGUE-CFW/releases/tag/1.7.10) [Goldfinger変更](https://github.com/Ninoh-FOX/PocketSNES/commit/2fa8a3cb8418e043910e7094db2b89fe2461a35c) |
| RACE GCW-ZERO V1.2 | AlekmaulツリーのOpenDingux用READMEの変更履歴はV1.1まで。同じ公開履歴を継承する複数のフォークを調べ、retrofw版のステートセーブ実装は2020年の別系統と確認した。両方のカタログ配布OPKの本体が同梱ELFとSHA-256で一致し、アイコンはデコード後の32×32 RGBAが一致する。2013-09-21版の対応ソース、アイコンの制作者と再配布条件は未確定。 [Alekmaulのソース](https://github.com/alekmaul/race/blob/ed8deb0223c76a63dda53f34cdda9ed15c5573a1/opendingux/readme-od.txt) [retrofwのステートセーブ変更](https://github.com/retrofw/race-od/commit/2982e9cb74d69d8cb8761e8b3882709ac0905add) |

- **PocketSNESの画像**は `backdrop.png` がhi-banを記載したコミットの `data/pocketsnes_bg.png` とバイト一致。`sfc.png` はSoar Qin版の `opk/sfc.png` とデコード後の32×32 RGBAが一致した。上流履歴はSuper Famicomアイコンもhi-ban作と記録している。同じファイルを収録する上流版マニュアルにhi-banの帰属とCC BY-SA 3.0が明記されている。 [マニュアルとライセンス表記](https://github.com/soarqin/PocketSNES/blob/1a627d83288721fba1eb14d08eefa22860a05e0e/dist/PocketSNES.man.txt) [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) [背景の上流記録](https://github.com/Ninoh-FOX/PocketSNES/commit/8070247148a082d90549b650352c53fe0c0da34b) [アイコンの上流記録](https://github.com/soarqin/PocketSNES/commit/39f2a8e086f35bb49124c394111233e74103278d)
- **fMSX**は非商用表記と著作者表示を付けて候補に維持した。作者が、別プロジェクトにfMSXが同梱された件で、許可を求められていないと指摘した公開投稿も確認した。plumOSでのLibretroバイナリ再配布を対象とする作者の回答は未確認。 [同梱版の原文](https://github.com/libretro/fmsx-libretro/blob/4de11755ce4f196ac1c8a7bb20bb4eccbc87a7d4/LICENSE) [作者の公開投稿](https://jonathan-cauldwell.itch.io/multi-platform-arcade-game-designer/comments?after=65)
- **FBA44**は非商用表記、原文、変更ソースを用意し、候補に維持した。上流Fix 06の `fbasdl.dge` と候補のELFの `DT_NEEDED` を比較すると、SDL、SDL_image、zlib、libpng、C/C++ランタイムが共通。音声出力は上流が `libao.so.4`、候補が `libasound.so.2`。上流配布物も動的リンクを使っているが、DLL条項の適用範囲を説明する権利者の文書は確認できていない。 [上流Fix 06](https://github.com/plrguez/fba-sdl/releases/tag/r19_2021-10-18-.44_od_beta-fix-06) [原文](https://github.com/plrguez/fba-sdl/blob/9448a9c6f1040ad8ec204b5e9cb83e25574ac0c8/src/license.txt)
- **Temper**はExophaseが2015年にPandora／GP2X系ソースの利用を呼びかけ、特定のPandora用バイナリの掲載を承諾した投稿を確認した。当時のアーカイブURLから取得できるのは現在HTMLのみ。同梱するGCW0派生版に適用される条件の確認は残る。 [作者の投稿 #122・#124](https://pyra-handheld.com/boards/threads/temper-split-from-other-thread.63264/page-7)

## 4機種で検証した整理版IMGの追加調査

SHA-256が `ca1fee2b7bcd736e0a795d4b2dff1da6565c2772c08a61c975e86dbae93c801e` の保存済みIMGを読み取り専用で開き、初期配置と実機試験後のテーマ、OPK内の実行ファイルを照合しました。

### 画像・フォント

| 素材 | 同梱物と上流の照合結果 | 公開に向けた確認 |
| --- | --- | --- |
| Simple Quest・Simple Quest 2 | 実機で使用するSimpleMenuのホームに両方のテーマが残っています。62点と60点が、それぞれ作者配布版と全ファイルでバイト一致しました。初期配置からのコピーを廃止した後も、検証用のスナップショットに残っていました。 [作者の配布ページと条件](https://yoshives.com/simplemenu-theme-simple-quest/) | 作者は改変を認め、二次配布を控えるよう求めています。このIMGに両版が収録されています。 |
| ArtBook | 125点のうち122点がanthonycacceseの320×240版と一致しました。BBC Micro、CPS、Super Game Boyのロゴ3点は一致しません。上流には導入手順があり、テーマの画像に対する再配布ライセンスは見つかっていません。Cabin BoldはSIL OFL 1.1の表記を確認しました。 [ArtBookのソース](https://github.com/anthonycaccese/sm-theme-art-book/tree/f64636382fbcc5c5bb9b9e79fbf116e43cbcc79b) | Cabin Boldの帰属を追記しました。テーマ画像とロゴ3点の出所・許諾が未確認です。 |
| SimUI | 71点すべてがDariusz Kuśnierekの320×240版とバイト一致しました。作者の制作部分はMITです。BPreplay Boldの2本はMagentaとGeorge Triantafyllakosをクレジットし、OFLを記載しています。上流のライセンス原文は実機に配置されたテーマフォルダの外にあります。 [SimUIのMIT原文](https://github.com/dkodr/SimUI/blob/13d35f79f9b6c75f034c51838496aa922b272045/LICENSE) · [フォントの原文](https://github.com/dkodr/SimUI/blob/13d35f79f9b6c75f034c51838496aa922b272045/font/backpacker_license.pdf) | 配布時にMIT原文とフォントの通知を保持します。第三者の標章には個別の条件が適用されます。 |
| SimpleMenu 0A | 初期配置の117枚のPNGが上流とデコード後のピクセルで一致しました。テーマはFGL82、RafaVico、H1BANを記載し、0A専用READMEはCC BY-NC-SA 4.0です。プロジェクト全体の画像にはCC BY-NC-SA 3.0が記載され、rxbradのロゴ配布元も3.0を掲げています。 [0A専用の原文](https://github.com/fgl82/simplemenu/blob/e70a861b1f05fd83cd1b19be53be11c0a0ecd510/simplemenu/output/OD/themes/320x240/0A/README.md) · [ロゴ配布元の原文](https://github.com/rxbrad/es-theme-gbz35/blob/05895874b2920ab6ffeeb574d053f3d9e976c000/README.md) | 0Aの作者表示と非商用・継承条件を記録しました。PixelManiaConden（`Pmc.ttf`）のメタデータにはHiBanの名前があり、許諾原文は未確認です。Acre Medium 1.000はJonathan Ball作です。作者は無料ダウンロードを提供していますが、再配布の条件は未確認です。一部の外部画像にも個別の確認が残ります。 [Acreの作者ページ](https://jonathanballdesign.com/work/acre/index.php) |
| 350tericの共通スキンフォント | `font.ttf` はEsoteric上流のファイルとバイト一致しました。SHA-256は `db5b86c44b31406e306cd3dde23ff4b44722c3ce7061a313915229d6d88a2ac6` です。フォント本体はMonotype Imaging Inc.の権利表示と独自ライセンス通知を含みます。隣の `font-license.txt` はApache 2.0の汎用原文で、このフォントに結び付く権利者の表示がありません。 [Esotericのスキン素材](https://github.com/podulator/esoteric/tree/6e0a1ca1aa523ec5dff042c4a220582edc1767e9/assets/skins) | このフォントを再配布できる根拠が未確認です。 |
| OpenDinguxテーマとCrystalMenuのフォント | OpenDinguxの320×240・640×480のPNG計88点がBuildrootのターゲット用画像と一致しました。画像のライセンスは[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)です。CrystalMenuの `umplus` BDF 2本はPyxelのサンプルとバイト一致し、IMGにCOZのM+許諾原文があります。 [OpenDinguxの作者表記](https://github.com/OpenDingux/gmenu2x-theme/blob/17682816622b31008bb9a498c78797a02aeae166/README) · [Pyxelの素材](https://github.com/kitao/pyxel/tree/ddff52645739c4a4d1575b85e87c16681a45514a/python/pyxel/examples/assets) | [第三者ライセンス表記](../../THIRD_PARTY_NOTICES.ja.md)に作者、出典、適用条件を記載しました。 |

### CrocoDSの内蔵ファームウェアと対応ソース

同梱実行ファイルには作者のCrocoDSコアで公開されているファームウェア2本が含まれます。`cpc6128.bin` は32,768バイト、CRC32 `9e827fe1`、SHA-1 `5977adbad3f7c1e0e082cd02fe76a700d9860c30` で、Caprice32の `cpc6128.rom` とバイト一致しました。`romdisc.bin` は16,384バイト、CRC32 `c3f93998`、SHA-1 `fad90dfc3eca7585ad8295917de9615aab8e1a95` で、Caprice32のAMSDOS ROMと26バイトだけ異なるAMSDOSの派生版です。作者は同梱版をOpenDingux向け単体移植として配布し、OPKはGPLv2原文を含んでいます。移植版のビルド可能な対応ソースと変更点は未確定です。別途公開された[Libretroコア](https://docs.libretro.com/library/crocods/)はコアのコードにMITを掲げています。 [単体版の作者告知](https://kyuran.be/blog/2019/11/23/crocods-for-rg350/) · [CrocoDS側の参照元](https://github.com/redbug26/crocods-core/tree/6091e690a000165fba69065f1f07c6ff3d452d20/resources) · [Caprice32側の参照元](https://github.com/ColinPitrat/caprice32/tree/a0d78f0f7c6d19a5d3205d1b231bd4da100ec6f3/rom)

Amstradの公開見解は同社が権利を持つ部分を対象としています。Locomotive BASICについて、LocoScript SoftwareのHoward Fisherは、改変なし・非営利でのCPCエミュ向け配布を受け入れ、配布者に正式な許可を申請するよう求めています。今回の同梱BASICへの許可と、この改変済みAMSDOSへの許諾はいずれも確認できていません。 [Amstradの見解](https://www.freetimeweb.nl/home/computer/alt/lawsons-amstrad-computer_site/web.ukonline.co.uk/cliff.lawson/cpchomec.htm) · [LocoScriptの見解](https://groups.google.com/g/comp.sys.amstrad.8bit/c/HtpBU2Bzv_U/m/HhNDSU3MksAJ)

#### 外部BIOSを読む検証版

作者の公開リポジトリにOpenDingux向けソースと旧OPKがあり、そこに含まれる2020年1月15日版OPKは取得済みの配布元とSHA-256が一致した。単体版の新しい候補は公開ソースの4.0 beta 3系統からビルドした。検証済みIMGのPicoArch用コアにも同じファームウェア2本が含まれていたため、上流 `f1b4b91` を基に外部BIOS版をビルドした。 [単体版ソース](https://github.com/redbug26/crocods/tree/67cf16db2b3cfd951b337b389eccbe5fd259ff6c) · [旧OPK](https://github.com/redbug26/crocods/tree/67cf16db2b3cfd951b337b389eccbe5fd259ff6c/gcw/release) · [Libretroソース](https://github.com/libretro/libretro-crocods/tree/f1b4b91291ba1e8e7c0be02269cd0d75c7fa71b9)

両版とも、plumOSのBIOS参照先の `bios/opk/crocods/` から `cpc6128.rom`（32 KiB）と `amsdos.rom`（16 KiB）を読む。CPCの字形とキーボードの文字割り当ても、指定されたROMを使う。単体版ではv3 SNAの非圧縮メモリーと追加データの読み分けを修正した。Libretro版には実行中の境界座標の保持に関する上流修正を適用した。 [Libretroの修正](https://github.com/libretro/libretro-crocods/commit/5981a91133cf7fe1706a21195ae5b8edfe39c736)

初期の外部BIOS版はRG350MのFE正規経路で007のDSKを起動できた。その後、SDL2の画面描画を使った候補の起動時にADB切断が2回発生した。画面表示をplumOSのDRMのRGB565バッファーに切り替え、ゲームパッドをevdevで読み、音声はSDL2のALSA出力を使った。最終候補での下記の試験中、ADB切断は再発しなかった。

| RG350Mでの試験 | 確認結果 |
| --- | --- |
| FE正規経路の単体版 | 007のDSKはタイトル画面まで、Abyssalのv3 SNAはプレイ画面まで到達。どちらもSELECT＋STARTでメニューを開き、Bでゲームへ復帰し、Quitで同じROM一覧に戻った。Disc PowerのBINはBASIC画面とFE復帰を確認。 |
| 同じ実行ファイルの描画・音声計測 | Abyssalで649回の描画、50.00 FPS、非ゼロPCMを確認。SDLの音声キュー登録失敗は0件。スピーカーでの聴取は未実施。 |
| PicoArch用コア | 外部BIOSからQWERTY／AZERTYを判定し、007のDSKを選ぶ際のBASICコマンド入力を修正。標準AMSDOSでタイトル画面に到達し、メニューから終了コード0で終了。 |
| BIOSがない場合 | FEの単体版経路でAMSDOSを一時的に外すと、必要なファイル名とサイズをログに出し、終了コード1でFEへ戻った。 |

試験にはRAM上の一時ファイルを使用した。終了後に解除し、既存OPK、PicoArch用コア、FEのコア設定、ROMインデックスが試験前のSHA-256と一致した。検証済みIMGもSHA-256が一致した。

最終候補の両ELFに、内蔵ファームウェア2本と従来のCPCの字形・キーボードテーブルが含まれないことを照合した。対応ソース一式、ライセンス原文、SHA-256は `output/validation/crocods-external-bios/drm-candidate/` にある。ソースアーカイブから再ビルドした両ELFはRG350Mで使ったものとバイト一致した。

### 旧版エミュレーターの実行ファイル

| 項目 | 今回の追加証拠 | 残る確認 |
| --- | --- | --- |
| FCEUX 2.2.3-interim | 同梱ELFに旧Buildroot GCC 4.9.1の識別子があります。上流の次の変更は2019-11-23の入力処理とOPK生成の改修でした。2019-11-15版OPKの一致、連射関連とBMPの一致から、引き続き `bf89b7fd` が最有力です。 [ソース候補](https://github.com/soarqin/fceux-for-retrogame/commit/bf89b7fd8b879cae6390bb1bbf41e71a88d53b03) · [次の上流変更](https://github.com/soarqin/fceux-for-retrogame/commit/a0dc6664e714a310ec2e6528c633c44d1db6b92c) | 当時のビルド入力、ローカル変更、スクリプトの確認、または公開ソースからビルドした版の実機検証。 |
| PocketSNES 2019-12-12 | 12月版ELFのGCC 4.9.1はFCEUXとは別のBuildroot識別子です。Soar Qinの公式11月版に次ぐ `1a627d8` は、Makefileへのプロファイル生成スイッチ追加のみです。ELF情報と公開履歴を照合しても、12月版のツリーとビルド手順は未確定です。 [11月版のソース](https://github.com/soarqin/PocketSNES/commit/0a13addffd8868d23e03f02a93df8e41c954cd41) · [Makefileの変更](https://github.com/soarqin/PocketSNES/commit/1a627d83288721fba1eb14d08eefa22860a05e0e) | 12月版のビルド入力と、hi-banの画像素材の条件を確認。 |
| RACE GCW-ZERO V1.2 | 同梱ELFには名前指定とファイルストリームの両方でステートを読み書きする関数があります。Alekmaulの公開OpenDinguxツリーではメニュー関数のステート入出力がコメントアウトされています。同梱ELFの復元処理は1レコードを読み、バージョン `0x10` と64バイトのROMシグネチャを照合します。この処理と関数の引数は8bitpspの2008年の実装と一致します。2020年のretrofw版は `0x11` で保存し、旧形式の `0x10` も読み込みます。 [Alekmaulの公開ツリー](https://github.com/alekmaul/race/tree/ed8deb0223c76a63dda53f34cdda9ed15c5573a1) · [2008年のステート実装](https://github.com/8bitpsp/race/blob/e3b8d8c8bf41ca2266e2f783fcbfb98422f7d1b4/state.cpp) · [retrofwの実装](https://github.com/retrofw/race-od/blob/2982e9cb74d69d8cb8761e8b3882709ac0905add/emu/state.cpp) | GCW-ZERO V1.2に組み込まれた実装の版、ビルド入力、アイコンの許諾を確認。 |
| Temper | 同梱ELFは保存済みのplumOSビルドとバイト一致しました。GCW0向け `a6c9ef2` にパッチを適用した版で、SHA-256は `aede280b2ebc3f83688b59f7855c8a2313636e1a139a129350b5ffb56b564c1b` です。上流ツリーにはExophaseのクレジットがあり、プロジェクト全体の再配布ライセンスは見つかっていません。 [GCW0ソース](https://github.com/gameblabla/temper/tree/a6c9ef2c5d1a086c22eb51980e07f3c38d0b42ae) | 改変したGCW0ビルドの再配布条件を確認。 |

## FBA44の動的ライブラリ条項

- Barry Harrisによる2011年12月のGit初回取り込みには、すでにDLL条項があります。同じツリーのWindows版はコンソールに接続する処理で `kernel32.dll` を直接読み込みます。公開履歴から、条項が最初に書かれた時期と理由までは確認できませんでした。 [当時の原文](https://github.com/barry65536/FBAlpha/blob/e4cc7bbf303177aa165c181a17efcdf422829959/src/license.txt#L1-L9) · [Windows版のコンソール処理](https://github.com/barry65536/FBAlpha/blob/e4cc7bbf303177aa165c181a17efcdf422829959/src/burner/win32/main.cpp#L344-L357)
- FB NeoのPR #26でbarbudreadmonは、文言を字面どおりに読むとDirectXも対象になると指摘しました。dinkとtmaulも当初の意図は不明と述べ、tmaulは実装にDLLが必要という理由で削除に賛成しました。dinkは2019年5月22日にFB Neoの原文からこの条項を外しました。nobk版とplumOSの採用版のFBA44原文には条項が残り、Linuxの例外は明記されていません。 [開発者の議論](https://github.com/finalburnneo/FBNeo/pull/26) · [削除コミット](https://github.com/finalburnneo/FBNeo/commit/de4cc9e9bbf0aa472231d2e4986d5498e649a241) · [nobk版の原文](https://github.com/nobk/fba-sdl/blob/9360dcc4b42f3e74e0b683fbd1abc37ee14f09e8/src/license.txt#L1-L9)
- 保存済みのFix 06 OPKは、作者の配布ファイルとSHA-256が一致しました。上流の `fbasdl.dge` はSDL 1.2、SDL_image、zlib、libpng、libaoに動的リンクしています。フォント差し替え検証版IMG内のplumOS版は同じSDL系、zlib、libpngを使い、音声出力にはlibaoの代わりにALSAを使います。同じOPK内の `fbasdl_lepus.dge` は作者版と一致し、こちらもSDLとlibaoに依存します。移植版が通常の画面・入力・音声処理に共有ライブラリを使って配布された実例です。この構成を別のOSイメージに同梱できると明示した公開資料は確認できていません。 [作者のOpenDingux配布](https://github.com/plrguez/fba-sdl/releases/tag/r19_2021-10-18-.44_od_beta-fix-06) · [ビルド設定](https://github.com/plrguez/fba-sdl/blob/9448a9c6f1040ad8ec204b5e9cb83e25574ac0c8/Makefile.dingux#L108-L115)
- フォント差し替え検証版IMGを読み戻し、FBA44のOPK内と共通ライセンスディレクトリにはFBA44原文が入っていないことを確認しました。原文はソース補足と[プロジェクト内](../../assets/frontend/licenses/FBA44-LICENSE.txt)にあります。配布時に原文全文と対応ソース・ビルド入力を提供し、依存コンポーネントの通知、営利・寄付・3年・ROMに関する条件も確認します。単体Linux版と上記の共有ライブラリがDLL条項の対象かどうかは、引き続き確認が必要です。

### RG350Mでの静的リンク試験

既存のFBA44のMIPSソフトフロート版オブジェクトを使い、SDL 1.2、SDL_image、ALSA、libdrm、libudev、libiconv、libpng、zlib、コンパイラーランタイムを静的リンクした試験用OPKを作成した。SDLの動的読み込みAPIとALSAバックエンドの共有ライブラリ読み込みを無効にし、ALSAも動的プラグインなしでビルドした。実行ファイルには動的セクション、`DT_NEEDED`、インタープリター指定がない。試験用OPKにはGCW0用ランチャーとスキン、FBA44のライセンス原文と静的リンク版の実行ファイル1本を収録した。Lepus向けの旧実行ファイルと起動定義は4機種の試験用OPKの対象外とした。

RG350MではADB経由で一時領域に置き、`opkrun` からKung-Fu Masterを起動した。FBA44本体のファイルオープンを追跡し、DRMとALSAのデバイスへのアクセスと、共有ライブラリを開かずに動作することを確認した。SELECT＋STARTでメニューを開き、Bでゲームへ復帰し、Exitで終了コード0を確認してFEへ戻した。既存のインストール済みOPKと保管済みIMGのSHA-256は一致した。

| RG350Mでの比較 | 現行 → 静的版のFPS | 確認結果 |
| --- | --- | --- |
| Kung-Fu Masterの実プレイ | 60.0 → 60.0 | ゲーム画面、メニュー、復帰画面の取得画像がピクセル単位で一致。両版とも無音以外のPCMを出力し、測定区間でALSA書き込みの負の戻り値は0件。 |
| Vigilanteの海賊版の導入画面 | 59.9 → 60.0 | 両版で導入画面、無音以外のPCM出力、メニュー表示と復帰を確認。 |
| Blade Master | 35.0 → 35.1 | 両版で映像の崩れとPCMの無音を確認。 |

FPSとPCMの取得には計測用ビルドを使った。`opkrun` の追跡試験には計測コードを入れていない試験用OPKを使った。ビルド手順、チェックサム、画面と追跡ログは `output/validation/fba44-static/` に保存した。

### 静的版の対応ソースと再リンク資料

| アーカイブ | 内容 |
| --- | --- |
| `plumOS-FBA44-v0.1.0-static-source.tar.gz` | FBA44 `9448a9c6f104` にplumOSの変更を適用したソースと差分、GCW0用OPKの素材とランチャー、ビルド手順、ライブラリのソースとパッチ、Buildroot構成、ライセンス原文 |
| `plumOS-FBA44-v0.1.0-static-relink.tar.gz` | FBA44のオブジェクト874個、静的依存ライブラリ8本、GCCとuClibc-ngのランタイムと起動オブジェクト、リンカーの引数、ライセンス原文、日英の手順 |

両アーカイブと `SHA256SUMS` は `output/validation/fba44-static/release-materials/` に収録した。展開したソースからOpenDingux SDKでクリーンビルドした結果と、展開した再リンク資料をDebianのGNU MIPS binutils 2.40でリンクした結果は、いずれもRG350Mで試験したOPKの実行ファイルとバイト単位で一致した。実行ファイルのSHA-256は `e665b52e7a5229406365c27ee319bbb3479eb841a55fdf803854a5b3263c4ede`。ALSAの診断文字列を変更してビルドした `libasound.a` に差し替えてもリンクでき、変更した文字列が実行ファイルに入ることを確認した。資料の対象は静的版の試験OPK。検証済みIMGのSHA-256は従来の値と一致した。

### ADBでのFE正規経路試験

RG350MにADBで接続し、静的版OPKと試験用ROM、FE設定とFBA44ホームの複製をRAMに置いた。バインドマウントで試験中だけ切り替え、FEのArcade一覧から `standalone:fba44` を通常の操作で起動した。既存のランチャーが静的版を読み込み、3タイトルともSELECT＋STARTでメニュー表示、Bでゲーム復帰、Exitで終了コード0を記録した。終了後は同一のFEプロセスで選択していたROMに戻った。

| タイトル | 本体のFPS表示と映像 | メニュー終了 |
| --- | --- | --- |
| Kung-Fu Master | 60 FPS、実プレイの描画を確認 | FEの同じROM一覧に復帰 |
| Vigilanteの海賊版 | 60 FPS、導入画面の描画を確認 | FEの同じROM一覧に復帰 |
| Blade Master | 約30 FPSの表示と、従来版でも発生した映像の崩れを確認 | FEの同じROM一覧に復帰 |

3タイトルともALSAの初期化ログと再生デバイスのオープンを確認した。スピーカーでの聴取は未実施。試験後は一時マウントを解除し、保存済みOPK、FEのコア設定、ROMインデックスのSHA-256が試験前と一致した。画面、終了ログ、照合結果は `output/validation/fba44-static/fe-adb-rg350m/` に保存した。

## FCEUX 2.2.3-interim の差し替え候補

Soar QinのOpenDingux版 `bf89b7fd8b879cae6390bb1bbf41e71a88d53b03` からビルドした。設定メニューに不足していた戻り値を補い、キー状態を解除する関数の戻り値型を修正した。既存のNES起動経路・ランチャーと、メニュー画像・アイコンの見た目を引き継いだ。OPKにはGPL version 2の原文を含む。 [上流ソースとライセンス原文](https://github.com/soarqin/fceux-for-retrogame/tree/bf89b7fd8b879cae6390bb1bbf41e71a88d53b03)

RG350MでOPKをRAMから一時的にマウントし、FEのNES一覧から既存のFCEUX 2.2.3経路でSuper Mario Bros.を起動した。ゲーム中の画面表示は60.1 FPS。SELECTを押しながらSTARTでメニューを開き、設定画面からメニューへの復帰、Bによるゲーム再開、Exitによる同じNES一覧への復帰と終了コード0を確認した。ALSA再生デバイスは開かれていた。スピーカーでの聴取は未実施。試験後に一時マウントを解除し、本体に保存されていたOPK・コア設定・ROMインデックスのSHA-256が試験前と一致した。

`output/validation/fceux223-source-build/` に `plumOS-FCEUX-2.2.3-bf89b7fd-source.tar.gz`、`fceux223-candidate.opk`、`SHA256SUMS`、画面とログを保存した。アーカイブには上流ソース、修正差分、OPK素材とランチャー、ビルド・梱包スクリプト、GPL原文を収録した。アーカイブを展開してクリーンビルドし、試験版の実行ファイルとOPKの両方がバイト単位で一致した。保管IMG内の旧実行ファイルに厳密に対応するソースは未確定。

## PocketSNES の差し替え候補

Soar QinのOpenDingux版 `1a627d83288721fba1eb14d08eefa22860a05e0e` からビルドした。診断ではGoldfinger追加版も試した。採用候補は旧OPKのメニュー構成に近い、Cheats追加前のリビジョンとした。plumOSの修正は映像と音声のコールバックに不足していた戻り値を補い、プロファイルを使わない通常ビルドを可能にし、コンパイラーのランタイムを静的リンクする。システムのlibpng 1.6を利用し、OPKのファイル名とFEの起動経路を引き継いだ。 [上流ソース](https://github.com/soarqin/PocketSNES/tree/1a627d83288721fba1eb14d08eefa22860a05e0e)

OPKには、非商用再配布の条件となるSnes9xの著作権表記とライセンス原文を収録した。背景とアイコンはhi-ban作の上流画像をそのまま使用し、CC BY-SA 3.0と明記した上流マニュアルを同梱した。 [上流マニュアル](https://github.com/soarqin/PocketSNES/blob/1a627d83288721fba1eb14d08eefa22860a05e0e/dist/PocketSNES.man.txt) [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/)

対応ソース `plumOS-PocketSNES-1a627d8-source.tar.gz` に上流ソース、修正差分、ビルド・梱包スクリプト、ライセンス原文とOPK素材を収録した。アーカイブを展開してクリーンビルドし、実行ファイルとOPKがいずれもバイト単位で一致した。試験成果物、SHA-256、画面と音声の計測記録は `output/validation/pocketsnes-source-build/closest-upstream/` に保存した。保管IMG内の旧実行ファイルに厳密に対応するソースは未確定。

RG350Mでは、RAMに置いた差し替え候補をFEの既存経路 `standalone:pocketsnes` から起動した。『F-Zero』の走行と『Super Mario World』のステージ内操作を確認し、安定時の描画は約60 FPSだった。2本とも44.1 kHzのPCM信号を取得し、計測区間にクリッピングはなかった。スピーカーでの聴取は未実施。SELECT＋STARTでメニューを表示し、Bでゲームへ戻り、Exitで同じFEプロセスの元のROM一覧に復帰した。一時マウントを解除した後、既存OPKとFEの状態ファイルが試験前と一致し、4機種で確認済みの整理版IMGもSHA-256照合に合格した。

## RACE の差し替え候補

retrofwのOpenDingux版 `7fe3dacba61a14da76d1cc1c6b7fb12b6f912870` を土台にし、FEの既存経路 `standalone:race` とランチャーの入口を引き継いだ。著作権表記とライセンス原文はOPKと対応ソースに収録した。 [上流ソース](https://github.com/retrofw/race-od/tree/7fe3dacba61a14da76d1cc1c6b7fb12b6f912870) [GPL version 2原文](https://github.com/retrofw/race-od/blob/7fe3dacba61a14da76d1cc1c6b7fb12b6f912870/License.txt)

旧ELFはNGP・NGPCの実機BIOSと一致する2,048バイトのフォントを含む。割り込みテーブルにも実機BIOSから一致するバイト列を確認した。差し替え候補ではCOZのM+フォント、エミュレーター側の割り込み処理、RAM初期化を使う。KoyoteのRAMダンプは外し、アイコンはplumOS用の新規画像、メニュー背景は単色にした。利用者が用意したBIOSは、plumOSの参照先にある `opk/race/npbiosb.bin` または `opk/race/npbiosc.bin` から読み込める。旧アイコンの再配布条件と旧ELFの厳密な対応ソースは未確定。

RG350MではADB経由で、『Metal Slug 1st Mission』の実プレイと『Metal Slug 2nd Mission』の導入画面を確認した。安定時の描画は約60 FPS。2本とも無音でないPCM信号を取得し、計測区間でクリッピングはなかった。スピーカーでの聴取は未実施。SD1のBIOS参照先を一時マウントし、外部NGPC BIOSを読み込めることも確認した。SELECT＋STARTでメニューを開き、Bで再開し、Exitで元のROM一覧に戻った。同梱GCW-ZERO V1.2で作った旧形式 `.sta` をスロット1から復元し、メニュー操作を再開できること、候補版で作った `.sta0` を保存・復元できることを確認した。旧版のZ80の状態は読み込み時に変換する。

`race-replacement.opk`、`plumOS-RACE-7fe3dac-source.tar.gz`、`SHA256SUMS`、試験記録は `output/validation/race-source-build/` に保存した。展開したソースから再ビルドし、実行ファイルとOPKがバイト単位で一致した。一時マウント解除後に既存ファイルのSHA-256を照合し、保管している4機種共通の整理版IMGも照合に合格した。

## Temper の再配布条件

bubble2k16のTemperPCE for 3DSは、ExophaseのTemperを移植し、作者を明記している。3DS版READMEの配布・利用手順には、別の移植版を再配布できるという記載は見つからなかった。今回確認する対象は、plumOSが同梱する改変GCW0版のOPKと対応ソース。 [3DS版のREADME](https://github.com/bubble2k16/emus3ds/blob/master/readme-temperpce.md) · [GCW0版のツリーに収録されたREADME](https://raw.githubusercontent.com/gameblabla/temper/a6c9ef2c5d1a086c22eb51980e07f3c38d0b42ae/pandora/pnd/readme.txt)

採用中のGCW0ツリーにあるPC版・Pandora版READMEには、ソースの再配布に作者の許可が必要で、移植時にコアへ加えた変更は事前確認を求めると記載されている。2015年にExophaseは、DingooとGCW-Zeroの移植者にもソースを渡したと思うと述べ、HookaによるPandora版PNDの掲載を明示的に承諾した。同じスレッドでライセンス名を付けず、特定の旧ソース2本の利用を広く呼びかけている。OpenPandoraの配布ページも当該PNDを再配布可と記載する。今回の改変GCW0版のOPKと対応ソースの公開を対象とした条件は確認できていない。 [GCW0ツリーのPandora版README](https://github.com/gameblabla/temper/blob/a6c9ef2c5d1a086c22eb51980e07f3c38d0b42ae/pandora/pnd/readme.txt) [Exophaseの投稿 #122・#124](https://www.pyra-handheld.com/boards/threads/temper-split-from-other-thread.63264/page-7) [Pandora版の配布ページ](https://repo.openpandora.org/?app=Temper&page=detail)

試験済みELFのSHA-256は `aede280b2ebc3f83688b59f7855c8a2313636e1a139a129350b5ffb56b564c1b`。監査用ソースには採用コミットに対する4ファイルの変更を収録している。プロジェクトのOpenDingux SDKで `SOURCE_DATE_EPOCH` に元のビルド日を指定してクリーンビルドし、試験済みELFとバイト単位で一致した。OPKのアイコンは上流 `SDL/icon.png` とデコード後のピクセルが一致した。上流のSystem CardファイルはOPKと監査用ソースに含まれず、そのファイル全体のバイト列はELF内にも見つからなかった。GCW0版はTremorを実行ファイルへ組み込むため、再配布時にはXiph.orgの著作権、ライセンスと免責条項も添える。 [GCW0のビルド定義](https://github.com/gameblabla/temper/blob/a6c9ef2c5d1a086c22eb51980e07f3c38d0b42ae/SDL/Makefile.gcw) [Tremorの原文](https://github.com/gameblabla/temper/blob/a6c9ef2c5d1a086c22eb51980e07f3c38d0b42ae/tremor/COPYING)

同梱を維持する場合は、改変版のバイナリと対応ソースの両方の公開、GCW0側の追加コードとアイコンに適用する条件を確認する。英語の問い合わせ文をローカルに用意した。検証済みIMGとソース確認用アーカイブは監査用に保管している。既存のGPL版Beetle PCE FastとBeetle SuperGrafxは、RG350MでHuCard・CD-ROM・SuperGrafxを確認済み。別の検証候補でTemper経路の扱いを変更する場合にも使える。 [RG350Mの試験記録](rg350m-all-emulator-routes-2026-11-19.md)

## fMSX の再配布条件とFM音源

作者の旧版ドキュメントには、ソースの再配布を認め、移植・改変時に連絡を求める記述がある。採用版のライセンス原文も連絡を求めているが、非商用のすべてのビルドについて返信や事前承認を必須とする文言はない。KodiはfMSXを著作者名・非商用表記付きで配布し、Batoceraのビルド定義はLibretroコアをOSのファイルシステムに収録する。これらの公開資料から作者との合意の範囲までは確認できない。別のRP2350移植は個別許諾を得たと明記している。 [作者の旧版ドキュメント](https://fms.komkon.org/fMSX/src/fMSX.html#LABD) [Kodiの配布ページ](https://kodi.tv/addons/omega/game.libretro.fmsx/) [Batoceraのビルド定義](https://github.com/batocera-linux/batocera.linux/blob/master/package/batocera/emulators/retroarch/libretro/libretro-fmsx/libretro-fmsx.mk) [RP2350移植のライセンス](https://github.com/rh1tech/frank-msx#license)

検証済みIMGのfMSXコアは、非商用の独自条件が付くfMSX本体と、GPL-2.0-or-laterのNuked-OPLLを静的にリンクしている。fMSX標準のFM音源が既定値でも、同梱ELFにはNuked-OPLLのコードが含まれる。両者を組み合わせて配布できる例外許諾は確認できていない。 [fMSXの原文](https://github.com/libretro/fmsx-libretro/blob/4de11755ce4f196ac1c8a7bb20bb4eccbc87a7d4/LICENSE) [Nuked-OPLLの原文](https://github.com/libretro/fmsx-libretro/blob/4de11755ce4f196ac1c8a7bb20bb4eccbc87a7d4/NukeYKT/opll.c)

同じ上流リビジョンからfMSX標準のFM音源だけを使う試験版を作成した。MIPS用の旧ステート形式にあるNuked-OPLL用の領域はサイズと位置を維持する。旧版でNuked-OPLLを選んでいた場合、その音源内部の状態は引き継げない。ソースアーカイブを展開して再ビルドし、試験版ELFとのバイト一致を確認した。試験版ELFのSHA-256は `ccee613e443bf755159ef3240cf0f4da4cee6401be7af0246508d044fb13b451`。 [試験版パッチ](../../patches/rg280v-fmsx-native-opll.patch)

RG350MでADBを使い、既存のFE → MSX → PicoArch fMSX経路から試験版でUSASを起動した。旧コアで作成したステートのスロット0を試験版で読み込み、タイトル画面とゲーム内画面を取得した。メニューのExitでFEに戻り、ALSA再生デバイスが開くことを確認した。スピーカーの音とFM音源対応タイトルでの発音は未確認。試験後に元のコアとFE設定に戻し、試験前のSHA-256と一致することを確認した。

fMSX本体の改変済みバイナリと対応ソースについて、非商用での再配布を作者へ確認する英文を用意した。作者の回答が得られるまでは、バイナリと対応ソースを内部検証用として扱う。

## SimpleMenu 0A のフォント差し替え候補

0AのPixelManiaConden（HiBan）、Acre Medium（Jonathan Ball）に加え、SimpleMenu本体の設定画面がEd MerrittのAkashi 1.00を使用している。Akashiのファイルには著作権表示があり、作者のサイトにはダウンロード案内がある。監査対象ファイルを同梱する再配布条件は確認できなかった。 [0Aの上流テーマ](https://github.com/fgl82/simplemenu/tree/e70a861b1f05fd83cd1b19be53be11c0a0ecd510/simplemenu/output/OD/themes/320x240/0A) [Akashiの作者サイト](https://www.tenbytwenty.com/#akashi)

候補ではPixelManiaCondenとAkashiの参照先を既存のNoto Sans JPに変更し、テーマ定義に参照のないAcreを候補から外した。0Aのリスト文字は16から13、見出しは40から32に調整した。テーマの作者表記とCC BY-NC-SA 4.0を維持し、フォントのOFL 1.1原文とテーマへの変更点を添える。 [フォントの原文](../../assets/frontend/licenses/NotoSansJP-OFL.txt) [候補ツリーの作成スクリプト](../../scripts/stage-jz47xx-simplemenu-fonts.py)

RG350Mで一時領域の0A候補を開き、英語と日本語の一覧表示、カーソル移動、設定への出入り、SimpleMenuの終了をADBで確認した。一覧は表示確認用のファイル名を使用した。候補IMGへ組み込む際は同じ処理を初期配置用と保存済みホームの両方の0Aに適用する。検証済みIMGは保存時のSHA-256と照合した。画像素材の個別条件は引き続きこの文書の画像監査を参照。

## SimpleMenu 0A の画像と同梱アーカイブ

整理版IMGの初期配置用と保存済みホームから、同じ120画像のSHA-256を照合した。内訳はPNGが103点、ICOが17点。ファイル名が `*.png` でも中身がICOの画像が14点ある。ロゴ画面の白い前景をGBZ35のSVGと比較すると、MSX、Game Boy、Atari STなどで形状が強く一致した。これはロゴの由来を裏付ける照合で、カード全体の一致は示さない。 [SimpleMenuの出典表示](https://github.com/fgl82/simplemenu/blob/e70a861b1f05fd83cd1b19be53be11c0a0ecd510/README.md#artwork-license) [GBZ35の原文](https://github.com/rxbrad/es-theme-gbz35/blob/05895874b2920ab6ffeeb574d053f3d9e976c000/README.md)

0Aの作者が制作した部分にはテーマのCC BY-NC-SA 4.0表記を保持する。GBZ35はCC BY-NC-SA 3.0と、Carbonなどからの素材利用を記載している。Carbonもロゴ・商標の権利者を別に記載している。0AのDoom・Daphne・Quake用アイコンにはゲームキャラクターの絵があり、今回の上流テーマ比較からはその個別の再配布条件を確認できなかった。 [Carbonのロゴ注記](https://github.com/RetroPie/es-theme-carbon) [CC BY-NC-SA 4.0原文](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.en)

両方の0Aにある未使用の `resources/general.zip` にはPixelManiaCondenとAcreが残っていた。候補作成スクリプトは照合した既知のアーカイブを除外する。両方の0Aで展開済みの120画像を保ったままZIPが無くなることを確認した。RG350Mでは一時領域の候補を使い、英語・日本語の一覧、カーソル移動、設定画面と終了後のFE復帰を再確認した。検証済みIMGは保存時のSHA-256と一致した。

### Doom・Daphne・Quakeの差し替え候補

0AのDoom・Daphne・Quakeにあるアイコンと全画面カードを、plumOSが作成した幾何学模様とNoto Sans JPの通常文字に差し替える。対象は6枚。元のファイル名と寸法を使い、0AのREADMEに変更内容とCC BY-NC-SA 4.0を記載する。初期配置用と保存済みホーム用の両方に適用し、テーマ内で他に変わるファイルがREADMEだけであることを照合した。 [候補作成スクリプト](../../scripts/stage-jz47xx-simplemenu-artwork.py) [上流の0A条件](https://github.com/fgl82/simplemenu/blob/e70a861b1f05fd83cd1b19be53be11c0a0ecd510/simplemenu/output/OD/themes/320x240/0A/README.md)

RG350Mの一時領域で3つの試験用セクションを作り、各カードと一覧ヘッダーのアイコン、一覧とカード間の行き来、SimpleMenuからFEへの復帰をADBで確認した。試験用セクションには表示用のファイル名だけを置いた。製品側の起動経路・テーマ構成への反映は、次の検証IMGで行う。検証済みIMGは保存時のSHA-256と一致した。

## SimUIの同梱ライセンスとフォント

整理版IMGのSimUI全71ファイルは、dkodrの320×240版 v1.2のファイルとSHA-256が一致した。上流リポジトリのMIT原文は、テーマのサブディレクトリだけをコピーした整理版IMGには入っていない。候補ではDariusz Kuśnierekの著作権・MIT原文を、テーマ直下の `LICENSE` として添える。画像68点はバイト単位で一致する。 [上流のMIT原文](https://github.com/dkodr/SimUI/blob/13d35f79f9b6c75f034c51838496aa922b272045/LICENSE) [同梱用原文](../../assets/frontend/licenses/SimUI-MIT.txt)

元のBPreplay Bold 2ファイルはメタデータにMagenta（2004年）とGeorge Triantafyllakos（2008年）の著作権・OFL表記を持つ。上流のPDFはbackpacker.grの一般利用案内。Fedoraのパッケージ調査では、派生元のMgOpen ModataとOFLの条件の整合性に疑義が記録されている。候補では2ファイルを除き、一覧・見出し・件数の参照先を既存のNoto Sans JPに変更してOFL 1.1原文を添えた。 [上流のPDF](https://github.com/dkodr/SimUI/blob/13d35f79f9b6c75f034c51838496aa922b272045/font/backpacker_license.pdf) [Fedoraの調査](https://fedoraproject.org/wiki/BP_Replay_fonts#Caveats) [候補作成スクリプト](../../scripts/stage-jz47xx-simui.py)

RG350Mで一時領域の候補を使い、英語・日本語の一覧、選択に追従する件数、設定の開閉と終了後のplumOS FE復帰を確認した。Noto Sans JP Regularにより英字の線は元のBoldより細く見える。整理版IMGとテーマ整理候補IMGはどちらも保存時のSHA-256と一致した。SimUI変更のIMG組み込みは未実施。

## plumOS FE共通画像の出典と表記

整理版IMGの既定テーマにある機種・メニューアイコン30点とROMギャラリー背景1点を、plumOS A30の `68d92d5` に照合した。29点はバイト一致。Game Boyアイコンと背景は整理版でメタデータが削除されているため、実機から読み取ったファイルがIMGの記録とSHA-256で一致することを確認し、A30版とデコード後の全画素を照合した。両点とも画素は一致した。V90S・MFなどの移植履歴より前に、A30の既定テーマの導入・更新にさかのぼれる。 [A30のアイコン導入](https://github.com/game-de-it/plumOS-A30/commit/9eac1864ddce2f9077436d660dac4f434fc6fcc4) [背景の更新](https://github.com/game-de-it/plumOS-A30/commit/68d92d5d950f4d2e247316cf0d7bac776e6d6861) [照合したテーマ](https://github.com/game-de-it/plumOS-A30/tree/68d92d5d950f4d2e247316cf0d7bac776e6d6861/package/frontend/plumos/themes/default) [ファイル別照合表](jz47xx-v0.1.0-frontend-artwork.tsv)

整理版IMGには、既定FEと350teric・PyMenu・EmulationStationの初期配置または保存済みホームに、同じハッシュの画像が計113ファイルある。A30の著作権表記とMIT原文を収録した同梱用通知は、plumOS制作部分に適用する。画像内の機種名・商標等は権利者に帰属する。個別の第三者素材を許諾する記録は確認できていない。既存のステージ処理は通知を `licenses/` にコピーする。検証済みIMGは保存時のSHA-256と照合した。 [A30のMIT原文](https://github.com/game-de-it/plumOS-A30/blob/5994862115d2b83a9301ae32e0c434d662226caf/LICENSE) [同梱用通知](../../assets/frontend/licenses/plumOS-frontend-artwork-NOTICE.txt)

## 350tericスキンの出典と未使用フォント

| スキン | 整理版IMGとの照合 | 再配布条件 |
| --- | --- | --- |
| Amber | 104画像がplumOSの生成済み画像とバイト一致。 | plumOS制作。 [Amberの説明](../../assets/rg280v-350teric/skins/Amber/README.md) |
| Flat | peeweekの上流と101画像・通知3点がバイト一致。 | 作者制作部分はCC0 1.0。Material Design IconsはApache 2.0。原文はスキン内の `SOURCE-LICENSE.md` と `SOURCE-3DRPARTY-LICENSE.md` に保持。 [Flatの原文](https://github.com/peeweek/gmenu2x-skin-flat/blob/e613a6b677ae4c6f74b6135b777005ede2b0a041/LICENSE.md) [第三者通知](https://github.com/peeweek/gmenu2x-skin-flat/blob/e613a6b677ae4c6f74b6135b777005ede2b0a041/3DRPARTY-LICENSE.md) |
| OldBoy・PSNextDark・Zelda | それぞれ243、124、86画像がm1024x版とバイト一致。 | 上流READMEに導入方法はあるが、画像の再配布を認める条件は確認できていない。 [上流README](https://github.com/m1024x/retrogame-skin-pack/blob/f7686404fbe137c17281c2545c22cfe311e04a4c/README.md) |
| Default・Minimal | Esoteric版と全149画像が一致。Defaultの8点はメタデータ整理後の全画素を実機から読み取って照合した。 | EsotericのプログラムはGPL-2.0。付属の個別壁紙などの出所・条件は確認が残る。 [Esotericの素材](https://github.com/podulator/esoteric/tree/6e0a1ca1aa523ec5dff042c4a220582edc1767e9/assets/skins) |

350tericはスキン固有、Default、共通の順で `font.ttf` を探す。同梱の4つの追加スキンはいずれも共通フォントを使うため、候補ではOldBoyとPSNextDarkのArimo複製、ZeldaのOldBoyフォント、FlatのPF Tempesta Seven Condensedと旧式ビットマップフォントの計5ファイルを、既知のSHA-256と照合して除いた。画像のうち除くのはFlatの旧式ビットマップフォント1点。 [候補作成スクリプト](../../scripts/stage-jz47xx-350teric-skins.py)

RG350Mの一時領域に、共通Noto Sans JPを使用する削除前後の比較ツリーを作り、4スキンそれぞれのメニュー、ROM一覧、選択移動後の計12画面を取得した。対応する画面は12組すべて画素一致した。表示用ファイルでの比較であり、エミュレーターは起動していない。試験後に一時領域を解放し、FEが復帰したことを確認した。整理版IMGは保存済みのSHA-256と一致した。

## v0.1.0の公開判断

上流の配布ライセンスと同梱通知を引き継ぎ、既知の制限や今回のバイナリに適用される具体的な義務を処理する。個別の作者名や画像の来歴の追跡は監査記録に残し、出典の未確認だけでは公開を保留しない。

4機種で起動確認した整理版IMGの後に、Simple Questの2版とArtBookの整理と、350tericの共有Monotypeフォント差し替えを含む別の候補IMGを作成した。この候補のSHA-256を再照合した。CrocoDSの単体版・PicoArch版およびRACEの内蔵ファームウェア対策は、実機試験を終えた個別成果物があり、IMGには統合されていない。FCEUX 2.2.3とPocketSNESにも、対応ソースとバイト一致で再ビルドできる試験済み候補がある。これらとFBA44静的版の保存済み成果物のSHA-256を再確認した。

公開するIMGは、確認済みの差分をまとめ、実機検証した同一ファイルを梱包する。既存の検証済みIMGとアーカイブは保管用とする。

# RG280V向けplumOS FE

V90S公開版の `plumos_controller_ui.c`、fbdevレンダラー、ROMスキャナーを移植し、JZ47xx用にクロスビルドする。ソースのMITライセンスは `src/frontend/LICENSE.V90S`、同梱フォントのライセンスは `assets/frontend/licenses/` に保持する。

## 置き場所と起動

- FE本体、設定、フォント、状態はSD1 p2の `/media/data/plumos` に置く。SD1 p3の `/media/user` はユーザー領域として保つ。
- SD2に `/roms` があれば読み取り専用の `/media/data/sd2/roms` を優先する。なければSD1 p3の `/media/user/roms` を見る。
- `S95frontend` はライブラリーキャッシュがないときだけスキャンしてFEを起動する。ADB用の `S90status` はFEがある場合には状態画面を描かない。
- RG280Vのfbdevは320×480×32bppを報告する。FEは320×240の論理画面を縦2行ずつ書き、実機で通常の縦横比になるようにする。
- ソフトウェアの背面バッファを使う。DRMが使えるときは320×480×32bppの2枚の画面バッファを60Hzで切り替える。DRMを開始できない場合はfbdevの垂直同期を待ってから転送する。矩形塗りは32bppで行単位にコピーし、不透明なギャラリー背景は初回描画後の画面データを再利用する。描画時間の調査には `PLUMOS_FBDEV_PROFILE=1` を使う。
- V90S版の機種ロゴと木目のROMギャラリー背景を同じテーマ階層に置く。機種一覧のカードとギャラリーは元の描画処理を320×240向けの寸法で使用する。
- `/dev/input/event2` のGPIOキーを読む。音量はALSA `PCM`、明るさはバックライトのsysfsへ反映する。

## メニュー範囲

STARTはUI設定、システム設定、ヘルプ、再起動、電源断。UI設定は一覧更新、表示方式、空の機種、ROM並び順、機種画面を開いた際の再スキャン。システム設定は音量、明るさ、本体情報。Wi-Fi、ネットワークサービス、未実装のAppsは表示しない。

ROM一覧はSD2の実データを検出する。ギャラリーは標準表示でXボタンから一覧表示へ切り替えられる。現在のSD2にROMサムネイルはないため、ギャラリーでは代替文字を表示する。GCW Zeroアプリは個別に互換性を検証する。

RG280Vの物理A/B/X/YはLinuxキーコード29/56/57/42で、FEでは順に決定/戻る/表示切替/お気に入りへ割り当てる。SD2のFAT32はUTF-8オプションでマウントし、日本語ファイル名を一覧へ取り込む。FEの主フォントとCJK代替フォントはSD1 p2の `/media/data/plumos/fonts` から読み込む。

## エミュレータ

FEはV90S版の `plumos-text-ui` でROMの起動計画を作り、`plumos-standalone-launch` からOPKを実行する。エミュレータのHOMEはSD1 p2の `/media/data/plumos/home` とし、設定やセーブが読み取り専用rootfsへ向かないようにする。旧OPKのSDL 1.2 KMSDRMがGPIOキーを認識できるよう、`ID_INPUT_KEY=1` のudevルールをrootfsに入れる。既存の試験用SDでは起動ラッパーがSD1 p2のルールを `/run/udev/rules.d` に読み込み、必要な場合だけイベント情報を更新する。

| 機種 | OPK | 確認状況 |
| --- | --- | --- |
| NES | FCEUX 2.6.6 | マリオで映像・入力・高品質設定での正常なBGM、SELECT＋STARTのメニュー、FEへの復帰を実機確認 |
| GB/GBC | Gambatte-DMS | GBC ROM読み込みと映像・音声デバイスを確認。GBは起動計画を確認 |
| SFC | PocketSNES | ROM指定で起動し、映像・音声デバイスを確認 |
| GBA | ReGBA 1.9.2 + 同梱GPL代替BIOS | Goodboy Galaxyを表示し、START＋SELECTでメニューを開くことを実機確認 |
| Mega Drive | Genesis Plus GX | ROM指定で起動し、映像・音声デバイスを確認 |

上記のROM指定・映像音声デバイスの確認時点では、旧OPKがGPIOキーの入力デバイスを開いていなかった。その後udevルールを適用し、ReGBAが `/dev/input/event2` を開くことを確認した。旧ReGBA 2019版では画面に緑の線が出て、メニューも開かなかった。ReGBA 1.9.2ではユーザーがGoodboy Galaxyの綺麗な表示とSTART＋SELECTで開くメニューを確認した。同梱BIOSのSHA-256 `661a9afb93624f2c5e77d07dab137bd8d23cff79e8639c62fe621b49bb064749` は[公開ソース](https://github.com/jdgleaver/ReGBA/tree/1.9.2/bios)内のバイナリと一致し、READMEにNormmatt提供のVBA-Mベースのオープンソース代替BIOSと記載されている。純正BIOSは含めない。音声とゲーム操作の物理確認は残る。旧PicoDrive OPKは `ELIBBAD` で起動できなかったため採用しない。その他の機種は既存の起動設定が残るが、エミュレータ未導入のため起動成功を確認していない。

NESは[公開FCEUX 2.6.6](https://github.com/plrguez/fceux-for-retrogame/releases/tag/2023-08-30)を採用した。旧版・新版とも低品質音声設定 `SDL.Sound.Quality = 0` では音が小さく不自然だった。新版の `1` では実機で正常なBGMを確認したため、起動前にグローバル設定と対象ROMの設定を `1` にする。物理電源ボタンはplumOS用に残し、FCEUX専用のSDL互換ライブラリでSELECT＋STARTをエミュレータのメニューキーに変換する。FE起動時に下地のfbdevを黒で埋め、エミュレータ終了時に古いADB READY画像が露出しないことを実機で確認した。

## 開発時の更新

`scripts/build-rg280v-fe.sh` でクロスビルド、`ADB_SERVER_PORT=5039 scripts/deploy-rg280v-fe.sh` で実機へ更新する。既存の設定JSONは既定で保存し、開発版の既定値で置換する時だけ `PLUMOS_FE_UPDATE_CONFIG=1` を付ける。自動起動サービスを入れる時は `PLUMOS_FE_INSTALL_SERVICE=1` を付ける。SDイメージの再生成は不要。

エミュレータ一式は `ADB_SERVER_PORT=5039 scripts/deploy-rg280v-emulators.sh` でSD1 p2へ展開する。OPK、補助ライブラリ、GPIO入力ルールをSHA-256で照合し、FE設定の6機種分の起動プロファイルだけ更新する。既存設定は `.pre-emulators` に退避する。取得元と補助ライブラリの再現手順は `scripts/fetch-rg280v-emulators.sh`、`scripts/build-rg280v-emulator-libs.sh` に固定した。ReGBA 1.9.2は[公開リリース](https://github.com/jdgleaver/ReGBA/releases/tag/1.9.2)から取得し、同じタグの[ソース](https://github.com/jdgleaver/ReGBA/tree/1.9.2)を記録する。

`scripts/capture-rg280v-fe.sh` はFEのfbdevを読み、実機相当の320×240 PNGへ変換する。エミュレータがDRMを使っている場合は `ADB_SERVER_PORT=5039 scripts/capture-rg280v-drm.sh output/rg280v-fe/drm-screenshot.png` で表示中のDRMプレーンを取得する。ReGBAの15bit `XB15` とFEの32bit `XR24` を判別してPNGに変換し、元データとDRM情報もPNGの隣に残す。開発用の出力は `output/` 以下に置き、Gitには含めない。

ReGBAの `Image scaling = Aspect, fast` はソフトウェアで隣接画素を平均するため、輪郭が柔らかくなる。`Hardware filter` はハードウェア拡大モード向けの項目で、この設定には作用しない。RG280Vの現行カーネルにはReGBAが書き込む旧OpenDinguxの `jz-lcd.0/sharpness_upscaling` が無い。起動ラッパーはSDLのアスペクト比維持と最近傍補間を指定する。`None` の銀色の枠はReGBAが起動直後にだけ描くため、SDLの3枚バッファでは未描画のバッファと交互に表示される。ReGBA専用の `libregba-doublebuf.so` が `SDL_SetVideoMode` のフラグを2枚バッファへ変更する。公式ReGBA本体と枠画像は維持し、DRM取得した連続6フレームで枠が消えないことと、物理画面でも枠が表示され点滅しないことを確認した。

最終的なSDイメージには `scripts/make-rg280v-image.sh` がFEとエミュレータ一式をSD1 p2へ同梱する。初回セットアップ完了後、同じ起動サービスでFEを起動する。エミュレータ追加後のイメージ生成と起動はまだ実機で未確認。

## 描画性能

RG280V実機の `--script` 連続スクロールで、初回のPNG読み込み後のギャラリーは平均9〜10ms/フレーム（約100fps相当）、TOPは平均約13〜16ms/フレーム（約60〜75fps相当）を計測した。物理操作中はギャラリー約62fps、TOP約59〜60fpsだった。垂直同期の `FBIO_WAITFORVSYNC` は実機で成功し、その版はユーザーによる実機操作で滑らかになったと確認された。DRM版は `drmModePageFlip` が成功し、320×480の60Hzモードで平均約16ms/フレームだった。初回の画像読み込みと稀な20ms台のフレームは残る。

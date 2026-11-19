# 作業ログ

## 2026-11-19 — RG350MのADB接続と暗転ログを確認

- 別のSD1でRG350Mを起動し、MacのUSB Ethernet経由でADBに接続。実機のDTモデルは`Anbernic RG-350M`、`/boot/model.txt`は`rg350m`。診断レポート4件を取得した。
- 液晶の`nv3052c`ドライバはSPIデバイスに接続済み。バックライトの設定値は8/12、`bl_power=4`。LCDコントローラはdeferred probeのままで、DRMにetnavivしか現れず、FEは`/dev/fb0`が存在しないため終了した。
- HDMIブリッジ`ite,it66121`はI²Cデバイスとして列挙されているがドライバ未接続。Ingenic DRMは出力ブリッジの取得がdeferすると初期化を中断する。RG300Xは同ブリッジのI²CをGPIO方式へ切り替えているため、RG350Mでも同じ切り分けを行う候補とする。まだ実機に変更を加えていない。

## 2026-11-19 — RG350Mの暗転診断を準備

- 検証用rootfsにRG350M専用の診断を追加。FE起動前、`READY`直後、その約5秒後と20秒後に、DRMコネクタ・モード・描画状態、fbdev、バックライト、FEプロセスと起動ログ、USB、カーネルログをSD1のユーザー領域へ保存する。
- 元のSquashFSと展開内容を比較し、変更が`rcS`の診断呼び出しと診断スクリプトの追加であることを確認した。
- 元カードはMacのハッシュ処理が失敗したあとに取り出し状態になり、再挿入時に内蔵SDリーダーのカード初期化が失敗した。診断rootfsは元カードへ書き込まれていない。
- 別カード用に元のイメージを複製し、起動領域のrootfsだけ診断版へ交換。カーネル・モデル指定・modules・mininit、先頭のブート領域、データ／ユーザー領域が元イメージと一致。診断用イメージとSHA-256は`output/rg350m-validation/`に生成し、Macで照合した。

## 2026-11-19 — RG350Mの暗転とSD1の照合

- 本体の画面は暗いままで、MacにはUSB機器／USB Ethernetが現れなかった。直前のRG300XのADB接続はofflineだった。
- 試験SD1の3パーティションの位置・サイズがイメージと一致。`model.txt=rg350m`、稼働用`uzImage.bin`、rootfs、modules、mininitを生成元と照合し、同梱の4機種のカーネルもSHA-256で照合した。
- 元イメージに存在しない`plumos-boot.log`に2回分の`READY`を確認。SD1のデータ・ユーザー領域とSD2のマウント、USB gadget設定の成功、adbdのPIDが記録されていた。後段のUSB状態は`operstate=down`、`carrier=0`。ログの`RG280V`は共通rootfsの固定ラベル。
- `S95frontend:0`はバックグラウンド起動を指示したシェルの結果。FEの描画成功は未確認。RG350Mのパネルドライバは組み込み済み。表示の切り分けには実機のDRM・バックライト情報とFEログが必要。照合時にSDへの書き込みは行っていない。

## 2026-11-19 — RG350Mの実機検証イメージを準備

- 既存のRG350M用カーネル・DTBと共通環境から予備SD1用イメージを生成。RG300Xで確認したFCEUXの修正と、PicoDrive・Stella・Gambatte 2020の修正版を同梱。
- 出力ファイル名を機種別にし、Linux側の作業ディレクトリも生成ごとに作り直す。既存のRG300X試験イメージを保持した。
- `model.txt=rg350m`、`ylm,rg350m`のDTB、起動ファイル、パーティション表、ext4、イメージ全体のSHA-256を照合。SHA-256は`3ef44ed5af1cf03b2ac70782a6978f09545306baf75e75ff774ecb39ea49b654`。
- 予備SD1への書き込みはユーザーが行う。実機ではまず起動、表示、USB、物理入力、音声を確認し、その後に電源操作とSD2を使ったエミュ経路を確認する。

## 2026-11-19 — RG300Xの旧エミュ表示とGambatte 2020のゲーム音を修正

- ユーザー確認に基づき、UAE4All、PC Engine CD、CrocoDS、NEO4ALL、FBA44のゲーム正常動作を検証記録へ反映した。
- 単体PicoDriveのMaster System／Game GearとStellaを320×240の論理面で描画し、640×480の機種ではSDL側で2倍にする。RG300Xへ反映し、三経路で描画範囲の縦横2倍、メニュー、約60fps、非ゼロPCMを確認した。
- Gambatte 2020はメニュー音が鳴る一方でゲームは無音。起動時の線形リサンプラー指定でGB／GBC両方のゲーム音PCMが復帰し、約60fpsだった。試験機に反映し、今後の共通SDイメージ生成でも修正版OPKを収録する。
- 修正後、ユーザーがGambatte 2020のゲーム正常動作と、単体PicoDriveのHorizontal／Vertical scalingで意図した画面サイズに調整できることを確認した。
- 詳細は `docs/validation/rg300x-all-emulator-routes-2026-11-19.md`。試験後のFE稼働、SD2読み取り専用、対象プロセスの停止を確認した。

## 2026-11-19 — RG300XのFE登録全58経路を確認

- 実機のFE設定から26機種・58経路を照合し、確認済み9経路に加えて49経路をSD2の代表ROMで起動。全49で表示を取得し、25はメニューから通常終了。24は計測後に対象プロセスを停止した。24件を別ROMや追加の入力手順で再試験した。
- Master Systemの5経路はFrontier Forceで音声データを取得。MSXのfMSXはUSASのプレイ画面に進み約60fpsで音声データを取得。FBA44はカンフーマスターの1面開始まで進み約60fpsと音声データを確認した。
- Gambatte 2020のGB/GBCでほぼ無音が再現。CrocoDS・UAE4All・PCE CDは本編確認まで届かず、blueMSXはUSASの入力待ちまで。NEO4ALLはFatal Furyの操作説明まで進み、前回の異常終了は短時間試験では再現しなかった。単体PicoDriveのMS/GGとStellaの小さい表示も記録。
- SD2の読み取り専用とFE復帰を最後に確認。個別の画面・FPS・PCM・終了方法は `docs/validation/rg300x-all-emulator-routes-2026-11-19.md` に記録した。

## 2026-11-19 — RG300XのFCEUX 2.2.3起動を修正

- 新しい/tmp HOMEでもvideo初期化の終了139を再現し、SDLの呼び出しを計測。320×240×16の`SDL_VideoModeOK`が0を返し、画面未作成のまま進むことを確認した。KMSDRMの実際の拡大表示機能と、物理解像度だけを見る公開SDL判定の食い違いが原因。設定ファイルの初期化では修正しない。
- 既存互換ライブラリに、2.2.3経路だけで有効になる表示可否の補正を追加。KMSDRM・対応する16bit NESモード・実パネルのモード一覧に限定し、他のSDL判定結果を維持。エミュ本体は既存の採用済みバイナリのまま。原ライブラリとランチャーを試験SD内へバックアップして更新し、最終SHA-256 `36e0867c3e81991fac7a8bd7f1b438d07519d30f81a8d441dec2e87ef196d57f`を照合。
- Baseballの試合画面とマリオWorld 1-1が約60fpsで動作し、32kHz音声出力のエラーを観測しなかった。ユーザーが映像・BGM・操作・メニュー・ゲーム復帰と、音量ボタン・START＋左右の輝度調整を正常と確認した。
- 最終版では通常FEのNES一覧から悪魔城伝説を既存のFCEUX 2.2.3選択のまま起動し、メニューのExitから同じFE PID 1814へ戻ることを確認。子・経路ともexit 0、残存FCEUXなし。異なるゲームへの起動遷移を追加の起動確認に使い、第三ROMの長時間プレイまでは合格扱いしない。
- 対応モード18組と無効フラグ・非KMSDRM・非対応サイズ/深度・不足するパネル・元の成功判定の維持・ネイティブ表示後のサイズ復帰を実ソースのホスト検査で確認。今後の共通試験イメージにも新ランチャー・互換ライブラリが入るよう生成処理を更新。既存イメージの再作成は行っていない。
- ユーザーがPSXのRUNABOUT-2で走行・プレイ可能と確認した結果も検証記録へ反映。走行中のfpsを新しく測定したという意味ではない。詳細は `docs/validation/rg300x-fceux223-mode-check-2026-11-19.md`。

## 2026-11-19 — RG300XのSD2ゲーム経路を試験

- RG300XとSD2の読み取り専用マウントを確認し、NESの単体2版・QuickNES、SFC/ChimeraSNES、GB/Gambatte、GBA/ReGBA、MD/PicoDrive、PCE/PCE Fast、PSX/PCSX4ALLを代表ROMで短時間試験。ROMやBIOSは変更していない。
- NES 2.6.6約58.7fps、QuickNES約59.5、SFC約59.8、GB約59.7、MD約60.0、PCE約59.7を定常窓で記録。PCM非ゼロとALSAエラーなしを確認。GBAのGoodboyは約55〜59fpsで、ユーザーが本体の映像・BGMとも正常と確認した。PSXは警告画面とメニューまでで、走行中の速度・音声を合格扱いしない。
- FCEUX 2.2.3は2つのROMで起動途中の終了139を再現。計測を外しても同じ。継承されたROM設定の修正・一時退避では直らず、その試験変更は元へ戻した。FE登録からは外さず、未解決として記録。
- Hard floatの既存OPKで計測用printfの浮動小数点引数が崩れるため、数値ログを整数引数のみで出力するよう変更。MIPS向けにビルドし、一時的に/tmpから計測した。既存の全エミュ用preloadは変更していない。
- 強制終了用watchdogのプロセスグループから抜けたFCEUXが残り、後続の初期化を妨げることを確認。対象PIDの実行ファイルを確認して終了し、影響下の結果は破棄して再試験した。通常Exitと後続プロセス確認を優先する。GB/GBAの古いシステム別ROMキャッシュも再スキャンした。
- 実際のFEから悪魔城伝説をQuickNESで起動し、SELECT＋STARTのExitから同じFE PIDへ復帰することを確認。試験用のコア選択設定をハッシュ一致で元へ戻した。最後はReGBAのメニューから終了し、残存エミュなし・FE TOPを画面取得。詳細は `docs/validation/rg300x-games-2026-11-19.md`。

## 2026-11-19 — RG300Xの実起動・入出力・Sleepを確認

- 初めのADB接続は現用RG280Vだったため機種名・画面・稼働時間で区別し、その端末へ変更せず接続切り替えを依頼。ユーザーが配線を修正後、開発用ADBサーバー5041の古い接続を作り直し、RG300X・試験用パーティション構成を確認した。
- RG300Xの640×480/60 HzのFE画面とSTARTメニューを取得。ユーザーがテスト音と物理十字キー・A/B・STARTメニューの正常動作を確認。CPUは996 MHzのまま。音量・輝度は入力注入で変更と元の値への復元を確認した。
- レンダラ内のヘッダー判定にもRG280Vだけの分岐が残っていたため、4機種共通のバッテリー処理へ変更。機種名は動的表示し、不要なWi-Fiと未初期化RTCの時計を省略。MIPSビルドと端末上のSHA-256一致、修正後画面を確認した。元のFEは試験SD内に1個バックアップした。
- ユーザーがFEのSleep→電源キーで正常復帰することを確認。FEのPIDが同じでカーネルにもsuspend exitを確認した。一方、DRM connector pollingの未初期化workが疑われる警告があるため、修正済みとはせず継続課題として記録。現時点ではカーネルを変更していない。
- 10秒以上の電源長押しでOFF→通常起動でFEへ戻ることをユーザーが確認。新しい稼働時間とFEハッシュ保持を読み取った。再起動後の古いADB transportはofflineのため、新しい開発用サーバー5042で接続した。FATユーザー領域の未正常アンマウント警告は残り、通常Shutdownとファイルシステム検査は未確認として区別する。
- 詳細・未確認項目は `docs/validation/rg300x-first-boot-2026-11-19.md`。

## 2026-11-19 — 4機種共通起動の設計とRG300X試験SDの準備

- ユーザーの指定によりRG300Xから実機検証する。現用RG280VのSD1を維持し、別の試験SDを使う。
- 上流odboot-clientの機種表と固定カーネルのDTSを確認。4機種はUBIBootのrg350版・カーネル・rootfsを共有し、起動前にDTBだけを選ぶ方式とした。4機種のDTBをビルドし、RG280Vの連結カーネルが現用SDとハッシュ一致することを確認した。
- FE、ホットキー、ゲーム中電源メニューの入力ノードをgpio-keysから取得するよう共通化。FEに機種名と縦倍率を渡し、ロゴ描画も実画面寸法へ対応。4モデルのホスト検査・不明モデル拒否・event7への追従、現用RG280Vでevent2/縦2倍の検出を確認。MIPS向けFEビルド成功。
- 確認済み環境を約606 MiBのファイル単位アーカイブとして転送。FEを一時停止して取得し、終了後にFEを再起動した。主要実行ファイルを実機と照合。SD2や巨大なカード全体イメージはコピーしない。
- 個人環境の試験イメージを1個生成。起動128 MiB、実行1536 MiB、ユーザー64 MiBで、コピー先の初回パーティション作成は無効化。生成時のext4検査に合格。SHA-256は`b2419091df92744a017efdb05ad5caface41177a49a035394ae4864bc0f57f5a`。ファイルシステムはLinuxのDockerボリューム内で構築し、macOS側の所有権・大文字小文字による差異を避ける。
- `select-jz47xx-boot-model.py`はマウント済み起動領域内のモデルファイルを検証して切り替える。4機種への切り替え、最初のバックアップ保持、破損ファイル拒否をホストで確認した。実カードへの適用は未実施。
- RG300Xの実起動は試験SD接続待ち。RG350/RG350Mも未検証。追加FE等に残るRG280V固有の描画処理は起動確認後の対象。詳細は `docs/jz47xx-multimodel.ja.md`。

## 2026-11-17 — GCW Zero系PDF ViewerをRG280Vへ移植

- OpenDinguxアプリ一覧の残るソース公開アプリからPDF Viewerを選び、配布ソースをSHA-256固定で取得。Xpdf 3.02とアプリをMIPS Soft floatで再ビルドし、320×240論理画面をRG280Vの320×480へ縦2倍表示するよう変更した。
- Appsから起動し、試験PDFの2ページを表示、Aでページ送り、SELECT＋STARTでFEへ復帰した。OPKと変更済みソースをSD1へ配置し、新規SDイメージ生成にも追加。詳細は `docs/validation/rg280v-pdfviewer-2026-11-17.md`。

## 2026-11-17 — SDL TerminalをRG280Vに移植

- GCW Zero系の `st-sdl` を固定コミットからMIPS Soft floatで再ビルド。320×240の端末画面と仮想キーボードを320×480へ縦2倍表示し、SELECT＋STARTでFEへ戻るようにした。
- OPKと変更済みソースをSD1へ配置し、今後のイメージ生成にも追加。実機のFE→Apps→起動、仮想キー入力、終了後のFE復帰を画面取得と入力注入で確認した。ユーザーも本体で文字の読みやすさとFE復帰を確認。詳細は `docs/validation/rg280v-st-sdl-2026-11-17.md`。

## 2026-11-17 — GCW Zero系Calculator・CommanderをRG280V向けに再ビルド

- SDL2、SDL2_image、SDL2_ttfをRG280V用Buildrootでビルドし、両アプリのソースを固定コミットからMIPS Soft floatで再ビルドした。OPKと必要な共有ライブラリをSD1へ配置し、今後のイメージ生成にも追加した。
- Calculatorは物理Aで入力、SELECTで終了する。ユーザーの指摘した計算結果の枠外表示を、文字幅を使った右寄せと枠内クリップで修正。実機取得画像では「777」が枠内に収まり、終了後にFEへ戻った。
- CommanderはSD2の読み取り専用領域を初期表示し、フォルダの開閉、X/Yメニュー、Quit後のFE復帰を確認した。詳細は `docs/validation/rg280v-gcw-apps-2026-11-17.md`。
- ユーザーがCalculatorの結果表示とCommanderを実機で確認し、両方正常と報告した。

## 2026-11-16 — GCW Zero系OPKアプリをFEへ統合

- STARTにAppsを追加し、SD1の `/media/data/apps` に置いたOPKを `opkinfo` の名前で自動表示するようにした。既存FEのアプリ起動・復帰経路に、RG280Vの入力準備、HOME、補助ライブラリを設定するOPK起動ラッパーを追加。6項目になったSTARTは1画面に収まるよう行間を調整した。
- 公開アプリのCalculatorとCommanderを試したが、それぞれSDL2ライブラリ不足とHard float ABI不一致で動かなかった。GPLv2以降のGCW Zero Input testerを固定コミットからSoft floatで再ビルドし、RG280VのX/Y割り当てと振動機能なしの構成でOPK化した。実機でFE→Apps→起動、十字キー・ABXYの表示、物理START＋SELECTでの終了、FE復帰を確認。OPKと変更済みソースは新規SDイメージ作成時にも収録する。詳細は `docs/validation/rg280v-opk-apps-2026-11-16.md`。

## 2026-11-16 — RG280VのFE文字サイズを統一して縮小

- FEヘッダーは機種名・時刻・充電/残量を残した1段構成のまま、既存ピクセル書体を320px幅に合わせて縮小。RG280Vの比例フォントを18pxから15pxにし、START、UI、システム、テーマ、HELP、情報、時刻設定の行間と表示件数を調整した。
- 実機の320×480画面を取得し、各画面の先頭と末尾、HELPの全6行、時刻設定の全4行が収まることを確認。FEのビルドとSD1への更新後ハッシュ照合を行い、旧バイナリをSD1に退避した。詳細は `docs/validation/rg280v-fe-typography-2026-11-16.md`。

## 2026-11-16 — RG280Vシステム設定の文字切れを修正

- V90S設定項目を戻した後、RG280VのSystem Settingsでは下部の説明欄が最終行のINFORMATIONに重なり、説明文も右端で切れていた。実機DRM画像で再現を確認した。
- RG280Vの設定画面全体をUI設定と同じ5行・34論理px間隔に統一し、下部説明欄を外した。INFOと時刻設定の子画面もスクロール末尾まで実機画像で確認した。FEバイナリは旧版をSD1へ退避してからSHA-256を照合して更新。詳細は `docs/validation/rg280v-system-settings-layout-2026-11-16.md`。

## 2026-11-16 — V90S FEソースとRG280V設定項目を再照合

- 前回はSTARTの表面だけを比較し、UI設定11項目を5項目、システム設定9項目を3項目へ削っていたRG280V専用分岐を見落とした。V90Sの実ソースとメニュー定義を照合し、UI設定11項目を復元。システム設定はRTC時刻と言語を追加して5項目とした。Wi-Fiや未導入の更新・工場出荷設定など、RG280Vで機能しない項目は表示しない。
- V90Sの正規言語ファイル6件をイメージ作成とADB配布へ追加。長い設定名と値をRG280Vの320px幅で同じサイズの比例フォントで表示するよう修正。RTC手動保存、タイムゾーンの `/etc/TZ` 永続化、端末固有の説明文を実装した。
- 実機でUI設定の先頭・末尾、テーマ画面、システム・時刻画面、日本語への切替、Favorites設定の保存と復元、手動時刻のRTC反映を確認。FEバイナリはSHA-256照合後に更新し、試験で変更した設定JSONはバックアップと一致する状態に戻した。詳細は `docs/validation/rg280v-v90s-fe-settings-audit-2026-11-16.md`。

## 2026-11-16 — RG280VのUI設定画面の下余白

- UI設定は5項目だが、使われていない説明欄を下に確保していたため、4項目だけ表示されて下が大きく空いていた。RG280VのUI設定に限り説明欄の予約を外し、行間を34論理pxにして5項目を画面内へ配置した。
- FEを再ビルドし、旧バイナリをSD1に退避してハッシュ照合後に更新。実機取得画像で最終行まで表示され、最終行へのカーソル移動とTOPへの復帰を確認した。詳細は `docs/validation/rg280v-ui-settings-spacing-2026-11-16.md`。

## 2026-11-16 — RG280VのSTARTメニューを他シリーズと照合

- Bubble、RK2020、pixel2のSTARTメニュー定義と実機のRG280V設定を比較。RG280Vは5項目で、UI Settings、System Settings、HELP、Reboot、Shutdownを表示。実機の320×240論理画面で全項目の文字切れがなく、前3項目への遷移とBでの復帰を確認した。
- Wi-Fiを前提とするNetwork Settingsは不要。一方、Performance Settingsは共通FE内に実装があるがRG280VのSTARTから開けず、Appsもカタログが空で未移植。Reboot/Shutdownの `confirm: true` は共通START処理で参照されていない。詳細は `docs/validation/rg280v-start-menu-audit-2026-11-16.md`。

## 2026-11-16 — RG280VのHELP画面とFEヘッダー

- HELPの長文を既存の18px比例フォントで描画し、USBの説明も短縮。最長行は画面内の264pxに対して247px。FEヘッダーは機種名を残した1段構成とし、右側に時刻と `CHG/BAT`、数値を既存plumOSのピクセル書体と色で表示した。
- 実機にRTCがあることを確認。バッテリードライバーには残量値がなく電圧値だけのため、数値は概算。実機取得画像で文字の重なりがないことを確認し、旧FEをSD1へ退避して更新。ユーザーがヘッダーのデザインとHELPの読みやすさを実機で確認した。詳細は `docs/validation/rg280v-help-header-2026-11-16.md`。

## 2026-11-16 — RG280Vのシステム情報画面の文字幅

- 320×480の実機画面で、INFORMATION見出しと機種名が右端で見切れることを確認。情報画面だけ既存の18px比例フォントへ切り替えた。ビルド成功、旧FEバイナリをSD1に退避し、新版へ更新。ユーザーが実機で文字が画面内に収まったことを確認した。詳細は `docs/validation/rg280v-system-information-font-2026-11-16.md`。

## 2026-11-16 — RG280Vの初回PicoArch起動待ちを解消

- 初回起動の約5〜6秒の待ちは、ゲーム起動時に行うGPIOキーのudev登録で発生していた。常駐udevを単に起動中へ移す案では、乱数初期化まで待つためFE表示直後の待ちが残った。
- RG280Vの固定GPIOキーをlibudevの実行時データベースへ起動中に登録し、検証できない場合だけ従来のudev処理へ戻るようにした。同時起動は排他ロックで直列化し、常駐udevがロックを引き継がないよう修正。カーネルの乱数初期化設定は変更していない。
- 実機ログでは入力準備が起動後3.94秒、FE準備が4.65秒で完了。udev常駐なしでGPIOキー属性を確認し、再実行は50ms。ユーザーはNES PicoArchの初回起動が速くなり、操作・メニュー・FE復帰が正常と確認。従来のSA FCEUXも同じ操作経路で正常。測定とSD1バックアップは `docs/validation/rg280v-picoarch-cold-launch-2026-11-16.md` に記録。

## 2026-11-16 — 想定エミュの実機確認完了

- ユーザーがRG280Vで想定していたエミュの動作確認完了を報告。現在のFE設定は有効15機種・候補37経路で、有効な候補にRA経路はない。FDS、32X、NGPC、FBNeoの4機種は実機結果に基づいてFEから除外済み。FEプロセスの稼働、実機設定のSHA-256 `8c4f65c763f02a10afe687b1b6e0e699cb1ce80a961a9b5b8d2d356864c938ce`、SD2読み取り専用を確認した。これは現在の想定構成の受け入れ結果であり、全ROMでの動作や全コアの60 FPS保証ではない。詳細は `docs/validation/rg280v-emulator-sweep-2026-11-16.md`。

## 2026-11-16 — MSXのRA経路をPicoArchへ変更し、起動ファイルを補完

- FEのMSX候補を `picoarch:fmsx` と `picoarch:bluemsx` に変更し、既定をfMSXにした。マージ処理にもMSXを追加。実機設定の差分はMSXのみで、SHA-256は `8c4f65c763f02a10afe687b1b6e0e699cb1ce80a961a9b5b8d2d356864c938ce`。
- fMSXコアと必須BIOS 5本・ディスク用BIOSが実機のPicoArch参照先に無かったため、固定リビジョンのコアをビルドし、手元のBIOSを公式MD5と転送後SHA-256で照合して配置した。blueMSXでは自動選択される `MSX2+` の機種設定だけがBIOS領域に欠けていた。SD2にある完全版からその設定を補い、参照先の共有ROM 8本とデータベースを確認した。BIOSはGitとSDイメージに含めない。
- `usas.rom` を両コアで短時間起動し、DRM画像でゲームのタイトル画面を確認。計測区間の表示は両方とも約60 FPS。続いてユーザーがFEからfMSXとblueMSXを実機確認し、両方とも映像・音・操作・FPS・SELECT＋STARTからのFE復帰をすべて正常と報告。blueMSXのログにも同ROMのロードとコア終了が記録され、FEが稼働している。詳細は `docs/validation/rg280v-msx-pico-fe-2026-11-16.md`。

## 2026-11-16 — FBNeoを性能不足でFEから除外

- ユーザーがPicoArch FBNeoの実機動作を約12 FPSと報告し、FEからの廃止を指定。`assets/frontend/systems.json` の `fbneo.enabled` を `false` にし、今後のプロファイル更新でも再有効化されないようマージ処理に反映した。
- 実機の設定差分はFBNeoの有効フラグのみ。SHA-256 `d5d09e9cc29bc10e2be4a171e70c56edba8bca627759391d1dc6a88c402cd79e` で照合後、FEを再起動した。ライブラリ再スキャンでFBNeoの18本が一覧から外れ、総数は702本から684本になった。FEプロセスは稼働し、SD2は読み取り専用。ROMとコアは残す。詳細は `docs/validation/rg280v-fbneo-pico-fe-2026-11-16.md`。

## 2026-11-16 — FBNeoのRA候補をFEから外す

- FEのFBNeo候補と既定を `retroarch:fbneo` から `picoarch:fbneo` に変更し、プロファイルのマージ対象にもFBNeoを加えた。実機へ反映した設定のSHA-256は `cbf2a5a8cc4be502e9029f878a2cba10fa314d48e468442a3021bbb740141934`。実機の設定差分はFBNeoのみで、SD2は読み取り専用のまま。
- 停止していたPicoArchはTERMに応答しなかったため終了し、FEを復旧した。ログには `airduelm72.zip` の必須ROM 2ファイル不足が記録されていた。現行FBNeoのDATと17本のROMをCRC照合し、`bchopper.zip` は必須23ファイルがすべて一致。実機とMac上の同ファイルのSHA-256も一致した。更新後のFBNeoでの映像・音・操作・FPSは未確認。詳細は `docs/validation/rg280v-fbneo-pico-fe-2026-11-16.md`。

## 2026-11-16 — WonderSwanのRA候補をPicoArchに置換

- ユーザーがRA経路の廃止を指定し、PicoArchは約50〜60 FPSで遊べると報告。FE候補と既定を `picoarch:mednafen_wswan` のみに変更した。マージ処理、通常配置、SDイメージ作成にも固定リビジョンのコアとソースを組み込んだ。
- 実機の既存コアと再ビルド品のSHA-256が一致。FE設定を反映して再起動し、選択画面にはPicoArchのみ表示。更新後のFEから `Puzzle Bobble.ws` を起動し、映像・音・操作・SELECT＋STARTからのFE復帰がすべて正常、約50〜60 FPSとユーザーが実機確認した。起動ログにもROMのロードとコア終了が記録されている。詳細は `docs/validation/rg280v-wonderswan-pico-fe-2026-11-16.md`。

## 2026-11-16 — NGPCを性能不足でFEから除外

- ユーザーがFE登録順のNGPCを実機で確認し、約40 FPSのため除外を指定。確認したROM名や音声・操作の個別結果は未取得。`assets/frontend/systems.json` の `ngpc.enabled` を `false` にした。
- 実機の設定もNGPCの有効フラグだけを変更してハッシュ照合し、FEを再起動。再スキャンでNGPCの27本が対象外となり、登録総数は729本から702本。FE稼働、PS1のPCSX4ALL既定、SD2読み取り専用を確認。NGPCのROMとコアは残す。次の登録順はWonderSwan。

## 2026-11-16 — PS1のPCSX ReARMedをFE候補から除外

- ユーザーの指定でPS1の候補をPCSX4ALLだけに変更し、既定も維持。マージ前後のJSON比較でPS1候補一覧以外は不変と確認した。
- 実機へハッシュ照合して反映しFEを再起動。PS1の選択メニューはPCSX4ALLだけとなり、既存バイナリのSHA-256も一致。ReARMed本体とROMは残す。次のFE登録順はNGPC。詳細は `docs/validation/rg280v-psx-investigation-2026-11-16.md`。

## 2026-11-16 — PCエンジンCDの実機確認

- ユーザーがPCエンジンCDを「OK」と報告。FEの唯一の候補であるPCE Fastを維持する。起動ログでは `ForceGear.chd` と `syscard3.pce` の読込、コア終了を確認し、FEプロセスも稼働中。個別のFPS値や音質の数値は未取得。
- FE登録順で次はPS1。既定はPCSX4ALL、もう一つの候補はPCSX ReARMed。

## 2026-11-16 — SuperGrafxのPCE Fastを非対応としてFE候補から除外

- ユーザーがSuperGrafxのPCE Fastで映像異常と無音を報告。公式コア説明でPCE FastにSuperGrafx機能が含まれないことを確認し、SuperGrafxのFE候補をBeetle SuperGrafxだけにした。PCエンジン側のPCE FastとSuperGrafx両候補は維持。
- 同じSuperGrafx ROMのBeetle SuperGrafx診断ではタイトル画面が描画され、後半は約59〜60 FPS、音声PCMも後半に出た。実機の古いPCE Fast選択履歴を削除してFEを再起動。ユーザーが1941の映像・音・操作・メニュー終了後のFE復帰をすべて正常と確認し、起動ログでも対応コアを照合した。詳細は `docs/validation/rg280v-supergrafx-pce-fast-2026-11-16.md`。

## 2026-11-16 — Sega CDのGenesis Plus GXをFE候補から除外、PCエンジン2コア合格

- ユーザーがSega CDのGenesis Plus GXに性能上の問題があると補足し、FEからの除外を指定。Sega CDはPicoDriveだけを候補と既定に変更した。実機の古いGenesis Plus GX選択履歴をクリアし、FE再起動後にPicoDriveのみ表示されることを確認。ほかの機種のGenesis Plus GX候補は維持。
- PCエンジンのPCE FastとSuperGrafxはユーザーが両方合格と報告。候補設定はそのまま。次はSuperGrafx。詳細は `docs/validation/rg280v-segacd-pcengine-cores-2026-11-16.md`。

## 2026-11-16 — Sega CD実機確認、次はPCエンジン

- ユーザーがFE登録順でSega CDを確認し、約50〜60 FPSで「ぎりぎり遊べる」と報告。この時点では候補2件（Genesis Plus GX、PicoDrive）を維持したが、後続の補足によりGenesis Plus GXを除外した。候補別のFPS内訳、映像・音声・操作・FE復帰の個別結果は未取得。
- リポジトリと実機のFE設定で、次のPCエンジンにはPCE Fast、SuperGrafxの順に2候補が登録され、既定はPCE Fastであることを確認。ユーザーが続けて実機確認する。

## 2026-11-16 — 32Xを性能不足でFEから除外

- ユーザーが32XのPicoDriveを実機で確認し、約30 FPS止まりと報告。指定に従い `sega32x.enabled=false` とし、既存設定へのマージでも無効状態を維持するよう変更した。
- 実機へハッシュ照合して反映しFEを再起動。ライブラリ再スキャンで32Xの4本が除外され、登録数は733本から729本。FE稼働、SD2読み取り専用、PS1のPCSX4ALL既定を確認した。ROMとコアは残す。次はSega CD。詳細は `docs/validation/rg280v-sega32x-rom-placement-2026-11-16.md`。

## 2026-11-16 — PS1既定をPCSX4ALLに確定し、32Xから実機確認を再開

- ユーザーの指定に従い、PS1の既定はPCSX4ALLとする。リポジトリとRG280V実機の `systems.json` の双方で `default_launch_profile` が `standalone:pcsx4all` であることを確認したため、設定変更は不要。
- 32XはFE登録順の次の未確認機種。実機には4本の試験用ROMがあり、登録コアは `picoarch:picodrive` の1件。ユーザーがFEから順番に実機確認し、問題があれば報告する。映像・色・音・FPS・入力・FE復帰の結果はまだ未取得。

## 2026-11-16 — PCSX4ALL派生版をTobal 2の対戦中ステートで比較

- ユーザーが対戦中に保存したスロット0のステートを使い、Ninoh-FOX・soarqin・gameblablaの3派生をSoft floatでビルドしてRG280Vで比較。画面取得時のFPSは現行版が41前後、Ninoh-FOX版が42〜48、ほか2版が36〜41で、いずれも60 FPSに届かなかった。gameblabla版のステート選択プレビューには色乱れがあった。
- 現行版のMIPS設定変更は連続FPSログで改善を示さず、旧GPU経路は表示寸法が崩れた。対戦中のPC採取ではGPUコマンド処理とポリゴン・スプライト描画が目立つ。比較用ビルド手順とサンプル解析を残した。
- 実機の既定PCSX4ALLのSHA-256とFE復旧を確認。試験用実行ファイルは端末から削除し、現行版を維持。結果と未確認項目は `docs/validation/rg280v-pcsx4all-variants-2026-11-16.md`。

## 2026-11-16 — RG280V PSXの重複画面切替を削減

- RUNABOUT-2の同じ走行ステートを自動ロードして比較。ReARMedの前フレーム再利用時にSDL画面切替を省くと、Unai版は約33 msから約25 ms/回、P.E.Op.S.版は約38～40 msから約33 ms/回へ短縮。Unai版で約40 FPS相当だが60 FPSには届かない。
- 連続8枚のDRM取得画像に全黒画面なし。色変換のMIPS向け2画素実装は全32,768色の値が一致し、コア処理は約1 ms短縮したがFPSは変わらず、採用しなかった。
- Unaiのホットスポットに限った `-funroll-loops` 比較でも走行中は約25 ms/回で改善せず、コアを元へ戻した。
- 画面切替の変更を `scripts/patch-rg280v-picoarch.py` に反映して通常ビルド。端末のPicoArch SHA-256 `aeacea598b60e6287c65b77f0f37fb313e6ceee699315cb13cb9ea1ee58a5be4` を確認し、通常版でPSXタイトル画面とFE復帰を確認。走行中の実機目視と音声は未確認。詳細は `docs/validation/rg280v-psx-investigation-2026-11-16.md`。

## 2026-11-16 — RUNABOUT-2走行中のReARMed処理内訳を採取

- ユーザーが保存した走行中ステートを両GPUコアで自動ロードし、Frameskip OFF・996 MHzの同一条件で計測。P.E.Op.S.は `retro_run()` 27.2～27.5 ms、画面更新10.4～12.5 ms。Unaiはそれぞれ19.0～19.5 ms、13.8～14.3 msで、合計は約33.3 ms/回だった。
- 約1 ms間隔のPCサンプリングをMacでシンボル照合した。P.E.Op.S.ではポリゴン描画とBGR555→RGB565色変換、Unaiでもポリゴン描画が主なCPU使用箇所。Unaiは改善するが、60 FPSに必要な16.7 ms/回には届かない。計測方法と割合の解釈は `docs/validation/rg280v-psx-investigation-2026-11-16.md` に記録。
- 計測用PicoArchを削除して通常版のSHA-256一致を確認し、FEプロセスを復旧。既定のPCSX4ALLとユーザーのセーブデータは変更していない。

## 2026-11-16 — RG280VのPCSX ReARMedとPCSX4ALLを同一ゲームで比較

- PCSX ReARMedはLightrec有効で起動・操作できる。RUNABOUT-2のFrameskip OFFでは約25～30 FPS。GPUをP.E.Op.S.からUnaiへ変えてもゲーム中は約30 FPSだった。
- 同じRUNABOUT-2の走行中、PCSX4ALLはDRM取得画面で59/60 FPS。PicoArch診断版でReARMedのFrameskip OFF時を計測すると、`retro_run()`約27 msと画面切替約9～14 msで、60 FPSの16.7 ms予算をコア実行だけで超えていた。詳細は`docs/validation/rg280v-psx-investigation-2026-11-16.md`。
- 計測用PicoArchは通常版へ戻した。FEのPSX既定候補はPCSX4ALLを維持する。

## 2026-11-16 — RG280VのPCSX4ALLをDigital入力で起動

- RG280Vに物理アナログスティックがないため、PCSX4ALLの起動時と設定初期化時の `Analog Mode` を `Digital`（0）に変更した。既存SD1の共通設定もデプロイ時に `Analog_Mode 0` へ更新する。
- 再ビルドしたSoft float版をSD1へ配置し、SHA-256 `6262810b9374ff451cffad750ac7afff150ae733f7b923f6f9e52c876fb1f030` が一致。共通設定とTobal 2専用設定の両方でDigital、FE稼働を確認した。Tobal 2の対戦中にDigitalモードで十字キーが効くことは前段の実機試験で確認済み。

## 2026-11-16 — Tobal 2のFPS・解像度・十字キー操作を実機調査

- DRM画面取得でPCSX4ALLの `512x480x15`、CPU 98〜100%、対戦中43〜49/60 FPSを読取。996 MHzで実行中。`512x480`はゲーム内部の映像モード。
- Software scalingで出力を320×240にし、さらに高解像度の横画素間引きを試したが、対戦中はおおむね42〜50/60 FPS、CPU 99〜100%で60 FPSに届かず。映像設定は元のhardware出力に戻した。
- Tobal 2はアナログモード3では対戦中に十字キーで移動できず、Digitalモード0で移動できることをユーザーが実機確認。Tobal 2専用設定にDigitalだけを残し、共通PSX設定は維持。詳細は`docs/validation/rg280v-pcsx4all-tobal2-2026-11-16.md`。

## 2026-11-16 — RG280VのPSX性能確認用Tobal 2をSD2へ配置

- `<local-path> 2 (Japan) (v1.1).bin` を転送。元ファイルは669,555,600バイトのMODE2/2352データで、元ディレクトリにCUEがなかったため、単一データトラックのCUEを作成した。
- ADBでSD2へ転送し、BINとCUEのSHA-256を元ファイルと照合した。BINの転送実測は1.8 MB/s、347.338秒。SD2は読み取り専用に戻した。
- FEのPSX専用スキャンで5本目として`Tobal 2 (Japan) (v1.1)`を検出。ゲーム起動と負荷場面でのFPS・音・操作は未確認。

## 2026-11-16 — PCSX4ALLをRG280VのplumOSへ移植

- 電源キーによるPCSX4ALLメニュー表示を外し、設定初期化後もSELECT＋STARTを既定にした。修正版を再ビルドし、SD1にハッシュ照合して配置した。
- RG350版ソースを固定し、現行Soft floatツールチェーンでMIPS再コンパイラ・SDL 1.2・CHD対応版をビルド。型不一致、SELECT＋START初期設定、CHDエラー処理をパッチ化した。
- SD1に配置し、FEのPSX既定候補をPCSX4ALLへ変更。従来のPCSX ReARMedは選択肢に残した。CUE/IMGを使うDRM取得の14・32・56秒時点でゲーム映像と60/60 FPS表示を確認。ユーザーは本体で映像と音声が正常と確認した。
- 入力・メニュー・FE復帰、CHD/PBP、保存内容の再起動後検証は残る。画像生成への組み込みとソース同梱を実装したが、画像自体の生成は未実施。詳細は`docs/validation/rg280v-pcsx4all-2026-11-16.md`。

## 2026-11-16 — RG280VのPSX実行方式を比較

- 現行PCSX ReARMedのLightrecは通常起動でも画面前に`signal 11`。コアダンプではPCがJIT生成コード領域にあり、カスタムマッピングを無効化しても再現した。
- `DYNAREC=0`の比較ビルドはクラッシュせず55秒でゲームロゴを描画したが、短時間計測では約14.85 FPS。公開RG350 PCSX4ALL OPKはHard float ABIで、現行rootfsのSoft float ABIと合わず起動できなかった。PCSX4ALLのMIPS再コンパイラはソース移植候補として残す。
- PSXのFE登録・現行候補は維持。映像・音・FPS・操作の実機受け入れは未了。詳細は`docs/validation/rg280v-psx-investigation-2026-11-16.md`。

## 2026-11-16 — クラッシュを理由に除外せずPSXをFE登録

- ユーザーの方針に従い、クラッシュは検証結果として扱い、PSXをFEの有効機種へ追加した。PCSX ReARMedを起動候補にし、PSXの機種ロゴ、試験用ROM4件、BIOS3種を配置した。ROM・BIOSはGitに含めない。
- 転送11件のSHA-256とFEのPSX登録4件を確認。SD2は読み取り専用へ戻し、FEの稼働を確認した。
- 別タイトルのCUE/IMGとBIOSを使った時間制限付き起動でもPCSX ReARMedは`signal 11`で異常終了。FEは復帰した。PSX登録は維持し、原因調査を残す。詳細は`docs/validation/rg280v-psx-fe-registration-2026-11-16.md`。

## 2026-11-16 — FEの不足機種アイコンを補完

- FEで新たに表示された32X、Sega CD、SuperGrafx、PC Engine CDのロゴ画像が欠けていた。既存15枚と同じplumOS-A30の既定テーマから4枚を追加した。
- 端末へ配置してFEを再起動。FE対応17機種とお気に入り・最近使った項目の計19枚についてSHA-256一致を確認した。DRM画面取得でFE稼働も確認。詳細は`docs/validation/rg280v-fe-system-logos-2026-11-16.md`。

## 2026-11-16 — FE全機種の試験用ROMを用意

- ユーザーの「対応する全てのROM」はFE対応機種ごとに約4本の試験用ROMという意味だったため、SD2の不足機種に13本を追加。32Xは前段の32本から4本へ整理した。元のROMライブラリは変更していない。
- FE再スキャンでは全17機種にROMが登録された。Sega CDのみ手元に利用可能な2本で、ほかの機種は4本以上。追加したROMとBIOSのSHA-256を照合し、CD用CHDは`chdman verify`を通過した。
- SD2の読み取り専用マウントとFEプロセスの稼働を確認。転送用にMacへ生成した約498 MBの一時ROM/CHDは削除した。ROM・BIOSはGitに含めない。実ゲームの色・音・FPS・操作は未確認。詳細は`docs/validation/rg280v-fe-rom-samples-2026-11-16.md`。

## 2026-11-16 — 32XのROM配置とFE登録

- 32XがFEに出ない原因は、SD2に該当ROMがなく空システムが非表示になる設定だった。FEの32X登録自体は有効。
- ユーザーの32X ROMライブラリの7zアーカイブ32個を検査し、対応する`.32x`をSD2へ配置。既存BC Racersはハッシュ一致で再転送せず、新規31本。全転送のサイズとSHA-256を照合し、FEライブラリにも32件が登録された。
- SD2を読み取り専用へ戻し、FEプロセスを再起動してADBシェル終了後も稼働することを確認。ROM・BIOSはGitに含めない。物理画面と実ゲームの試験は未実施。詳細は`docs/validation/rg280v-sega32x-rom-placement-2026-11-16.md`。

## 2026-11-16 — Game Gear候補とPicoArch共通表示サイズ

- ユーザーがGame GearのFE登録4候補を動作OKと実機報告。PicoArchログでGenesis Plus GX・PicoDrive・GearsystemのSD2 Columns起動・終了を確認。候補構成は維持。
- PicoArchのAspect・Fullなどが一部コアで効かないように見えるとの報告を受け、全コア共通の`scale()`経路を修正。Nativeの非整数拡大、初回の代替アスペクト比の保持、画面モード変更後の余白残りを解消し、Libretroの実行中ジオメトリ変更も反映する。
- 実スケーラーの11条件試験を通過。修正版をSHA-256照合してRG280Vへ配置し、GearsystemのGame Gear Columnsで最終窓59.99 FPS・描画・PCM信号・FE復帰を自動確認。物理メニューでの3モード切替と色・音・操作はユーザー回答待ち。詳細は`docs/validation/rg280v-picoarch-screen-size-2026-11-16.md`。
- ユーザーがGearsystemのGame GearでNative・Aspect・Fullの表示幅の変化を実機確認し、色・音・操作も正常と報告。端末のPicoArch本体ハッシュは最終版と一致。ほかのコアは共通描画経路の寸法試験で確認済みだが、ROMごとの物理表示は再試験していない。

## 2026-11-16 — マスターシステムFE候補の実機確認

- ユーザーがマスターシステムの全候補を正常と報告。PicoArchログではGenesis Plus GX、PicoDrive、GearsystemのSD2 ROM起動・コア終了を確認し、単体PicoDriveが端末のFE選択中。構成変更なし。候補別FPS数値などは未取得。詳細は`docs/validation/rg280v-mastersystem-cores-2026-11-16.md`。次はGame Gear。

## 2026-11-16 — Mega Drive Genesis Plus GXの場面依存FPS低下

- ユーザーがGenesis Plus GXの全確認ROMで、場面により約60 FPSから約30 FPSへ落ちると報告。ほかのMega Drive候補は正常との報告。
- 同一Shinobi ROMの無操作約20秒自動起動は、従来44.1 kHzと試験用32 kHzの双方で終盤59.99 FPS。ゲーム中の低下場面を含まないため、改善判定はできない。
- 32 kHz比較コアを元コアのバックアップとSHA-256照合後に端末へ配置。FE稼働を確認し、同じ場面でのFPSと音の実機比較を依頼。詳細は`docs/validation/rg280v-megadrive-genesis-plus-gx-2026-11-16.md`。
- ユーザーが32 kHz版でも約30 FPSへの低下を確認。表示中のCastlevania BloodlinesではCPU周波数996 MHz、プロセスのCPU時間差分は約52～57%相当で、DRMのVBlank待ちも観測。Mega Drive FE候補からGenesis Plus GXを外し、単体・PicoArchのPicoDriveを残す準備をした。ゲーム終了後に元コアとFE設定を端末へ反映する。
- ユーザーがFEへ戻った後、元のGenesis Plus GXコアを端末・ホスト出力・ソースへ復元。端末のコア・FE設定・選択上書きのSHA-256一致を確認し、FEを再起動した。Mega Driveの選択上書きは単体PicoDriveへ戻した。物理FE画面の確認は未取得。

## 2026-11-16 — GBA mGBAの30 FPS

- ユーザーがGBAのReGBA・gpSPは正常、mGBAだけ約30 FPSと報告。端末のPicoArchログでは同じSD2の`Densetsu no Stafy 3 (Japan).gba`をgpSPとmGBAで起動・終了している。
- mGBAのFrameskip既定値は0、個別上書きなし。同ROMの20秒診断で安定窓29.99 FPS、`SDL_Flip`待ち平均12.176 ms。1フレーム約33.34 msのうち画面待ち以外が約21.16 msで、60 Hzの16.7 msを超える。待機ループ最適化を`Detect and Remove`へ強めた比較ビルドも29.99 FPSで改善しなかったため、元コアをSHA-256照合して復元。
- mGBAをGBAのFE候補から削除し、ReGBAとgpSPを維持する。詳細は`docs/validation/rg280v-gba-mgba-2026-11-16.md`。
- FE設定を端末へ配置して読み戻し一致を確認。GBA選択を単体ReGBAへ戻してFEを再起動し、端末プロセスと旧mGBAコアのハッシュを照合。

## 2026-11-16 — GBCのFE登録候補

- ユーザーがGBCの4候補（単体Gambatte、PicoArch Gambatte、Gearboy、VBA-M）をすべて正常と実機確認。端末ログではPicoArchの3候補がSD2の`Horde DX (USA).gbc`を起動・終了。FEのrecentには単体GambatteでGBC ROMの起動履歴が残る。
- 候補構成と既定の単体Gambatteは維持。個別候補のFPS数値やセーブ永続性はこの報告では未取得。次はGBAの登録順、単体ReGBA、PicoArch gpSP、mGBA。詳細は`docs/validation/rg280v-gbc-cores-2026-11-16.md`。

## 2026-11-16 — GBのFE登録候補

- ユーザーがGBの登録候補を確認し「すべて動作OK」と報告。FE候補は単体Gambatte、PicoArch Gambatte、Gearboy、VBA-Mの順。
- 端末のGBログでPicoArchの3候補がSD2の`Zelda no Densetsu - Yume o Miru Shima (Japan).gb`を起動・終了したことを確認。FEのrecentには単体Gambatteで`Super Mario Land [V1.1].gb`の記録がある。候補別のFPS数値・音声波形・セーブ永続性は今回取得していない。次はGBC。

## 2026-11-16 — SFC Snes9x 2010の最終確認

- 登録順最後のSnes9x 2010をSD2のSuper Mario Worldで短時間・長時間の診断起動。14秒試験では終盤48.01 FPS、26秒試験では終盤30.18 FPS。18秒時点のDRM画面にはタイトルの色崩れがあり、先頭2枚の取得画像は黒かった。
- 60 FPSと正しい色を満たさないためSFCのFE候補から削除。コア本体とビルドレシピは調査用に保持。残る候補はPocketSNES、Snes9x 2005、ChimeraSNES、Snes9x 2005 Plus。詳細は`docs/validation/rg280v-sfc-snes9x2010-2026-11-16.md`。
- FE設定を端末へ配置し、SHA-256一致と読み戻した候補順を確認。FE再起動後にプロセスが稼働し、SFCの選択は正常確認済みのSnes9x 2005 Plusを保持。

## 2026-11-16 — SFC FE候補の整理

- ユーザーの指示で約30 FPS固定のMednafen SupafaustをSFCのFE候補から削除。コア本体とビルドレシピは調査・互換性試験用に保持する。
- Snes9x 2002はユーザーから速度・音は正常だが背景が黒いと報告された。タイトル画面のDRM取得では中央の黒い背景を確認。ゲーム中の描画を確認してコア固有の欠落か判定する。
- 同じSD2のSuper Mario World ROMをChimeraSNESでも起動してDRM画面を比較。ChimeraSNESには山・雲・木の背景が表示され、Snes9x 2002では同じ背景領域が黒い。Snes9x 2002のTransparency既定値は有効で、端末に個別上書きもなかった。描画欠落を確認したため、ユーザーの条件に従いSnes9x 2002もSFCのFE候補から削除。
- FE設定を端末へ配置してSHA-256一致を確認し、ChimeraSNES終了後にFEを再起動。FEプロセスは稼働し、SFC候補はPocketSNES、Snes9x 2005、ChimeraSNES、Snes9x 2005 Plus、Snes9x 2010の順。詳細は`docs/validation/rg280v-sfc-snes9x2002-background-2026-11-16.md`。
- 登録順に沿ってSFCの選択をSnes9x 2005 Plusへ進め、FEを再起動して上書き状態を照合。物理画面の背景・音・FPS・操作・復帰は確認待ち。
- ユーザーがSnes9x 2005 Plusの背景・音・操作・SELECT＋STARTメニューからFE復帰を正常、約60 FPSと実機確認。端末ログには同コアで`Dragon Quest I & II.smc`の起動と正常なコア終了が残る。次の登録順はSnes9x 2010。

## 2026-11-16 — SFC Mednafen Supafaustの起動修正と比較

- FE登録順の次の候補Mednafen Supafaustを調査。既定のエミュレーションスレッド固定先がCPU 1 (`0x2`) で、CPU 0しかないRG280Vでは起動時に`MDFN_Error`を投げていた。既定をCPU固定なし (`0x0`) に変更する再現可能なビルドパッチを追加した。
- 修正版は同じSuper Mario World ROMで12秒間の診断起動を完了し、以前のsignal 6は再現しなかった。画面更新は最後の窓で35.75 FPS。上流が単一CPU向けに推奨する単一スレッドPPUへ変更しても35.63 FPSで、速度改善はなかった。
- 単一スレッド版を端末へ配置し、FEのSFC選択をMednafen Supafaustへ進めた。実機での映像・音・操作・メニュー復帰はユーザー確認待ち。詳細は`docs/validation/rg280v-sfc-supafaust-2026-11-16.md`。
- ユーザーがSuper Mario WorldでHUD約`30 (30)`を確認。F-Zeroでも安定区間30.0 FPS、画面更新待ち平均13.0 msで、残り約20.3 msが60 Hzの16.7 ms枠を超えた。30 FPS固定は処理時間と垂直同期の組み合わせで説明でき、映像のみのFrameskipではない。FE復帰済み。
- FEのSFC選択を次の登録順であるSnes9x 2002へ変更。端末のPicoArchはFrameskip既定値をDisabledにしたSHA-256 `97e1688f...` のビルドであることを確認し、FE再起動後の選択状態を照合。物理確認待ち。

## 2026-11-16 — SFCのFE候補とChimeraSNES

- ユーザーの指示で性能不足の標準Snes9xをSFCのFE候補から削除。PocketSNES、Snes9x 2005、ChimeraSNES以降の登録順を維持した。
- ユーザーがChimeraSNESのFrameskip OFFで正常動作を確認。コア初期値がAutoだったため、再現可能なビルドパッチでDisabledへ変更。ヘッダー変更をMakefileが追跡しない点も対処し、旧バイナリと異なる修正版を生成した。
- 旧コア・FE定義を端末内へ控え、修正版のハッシュ一致を確認して配置。ライブラリ再走査とFE復帰、候補順序を確認。修正版の物理動作は確認待ち。詳細は `docs/validation/rg280v-sfc-chimerasnes-2026-11-16.md`。
- 修正版ChimeraSNESをユーザーがFEから手動設定なしで試し、約60 FPS、映像・音・操作・メニューからFE復帰まで正常と確認した。次は登録順のMednafen Supafaust。

## 2026-11-16 — SFC標準Snes9xの30 FPS調査

- ユーザーが標準Snes9xのF-Zeroで約30 FPS固定、CPU約60%、Frameskip項目なしと報告。DRM画面でも30.0 FPS・CPU約58%を確認。
- `SDL_Flip`待機は平均約12.4 ms、1フレームの残り処理は約20.9 ms。Native表示でも30 FPS。転送待ちを診断時だけ外すと約47.2 FPS相当だったため、同期待ちだけの問題ではなく、標準コアの処理が60 Hzの期限を超えている。CPU表示60%は待機を含む平均値。
- 診断用の一時設定・端末ライブラリを削除してFEを復帰。SFCの選択状態は維持。実用コアはユーザー確認済みのSnes9x 2005。詳細は `docs/validation/rg280v-sfc-standard-performance-2026-11-16.md`。

## 2026-11-16 — SFC Snes9x 2005の2 FPS表示と描画停止

- ユーザーがNESの他のコアも問題なしと報告。個別のROM・設定・計測値は未取得のため、この報告を確認範囲として記録。
- FEからSnes9x 2005で起動したDBZ対戦画面はHUDの描画数が2 FPS、内部ループ50〜60/秒、CPU約40%、音は正常。画面も実際にカクつき、時々60 FPSになるとCPU約78%。
- PicoArchのAuto Frameskip上書きが原因と特定。ユーザーがゲーム中にFrameskipをDisabledにすると60 FPSへ戻った。PicoArchのSnes9x 2005と2002の既定上書きをDisabledへ変更し、ホストで再ビルド。プレイ中なので端末への反映は終了後に行う。詳細は `docs/validation/rg280v-sfc-frameskip-2026-11-16.md`。
- ユーザーがExitでFEへ戻った後、旧PicoArchを端末内へ控え、修正版をSHA-256一致で配置した。FEプロセスは動作中。新バイナリでのDBZ再試験はユーザーへ依頼済み。
- ユーザーが修正版Snes9x 2005で複数のSFCゲームを試し、動作に問題なしと報告。recentにはDBZ、DQ I & II、DQ VI、Exhaust Heat II、F-Zeroが残り、FEへ復帰した。ゲーム別のFPS計測値とSnes9x 2002の物理試験は未取得。

## 2026-11-16 — RG280V単体FCEUXの54 FPS調査

- ユーザーの悪魔城伝説で60 FPSに届かない報告を受け、実機のFCEUXを計測。48 kHz音声では後半約54.1 FPSで、主スレッドがほぼCPU 1コアを使い切っていた。`SDL_Flip`は約0.5～0.6 ms/回。
- 音声OFFで約106.5 FPS、32 kHz音声で約59.7 FPS、48 kHzのまま描画を半分にすると内部進行約60 FPS相当。48 kHz音声を伴う主ループの処理量が主因と判断した。音声生成とバッファ書き込みの内訳は未測定。
- 試験後にROM別設定の元ハッシュとFE復帰を確認。悪魔城伝説だけ32 kHzの確認用設定へ切り替えた。計測条件・範囲は `docs/validation/rg280v-fceux-performance-2026-11-16.md`。
- ユーザーがFEから悪魔城伝説を起動し、32 kHz設定で音も動きも正常と実機確認。終了後もROM別の32 kHz設定が残り、FEが動作していることをADBで確認した。他のNES ROMの音と速度は未確認。

## 2026-11-16 — PicoArchのCPU使用率項目名

- RG280Vの「Audio and Video」で `Show CPU %` の項目名が欠けることをDRM画面で確認。共通メニュー描画が項目名を可変書式として扱い、末尾の `%` を解釈していた。固定書式で文字列を渡す修正をビルド・配置し、実機ハッシュを照合した。ユーザーがFEからQuickNESを再起動し、項目名の表示を確認。詳細は `docs/validation/rg280v-picoarch-cpu-menu-2026-11-16.md`。

## 2026-11-16 — QuickNESメニューの実機確認

- ユーザーがFEからQuickNESを起動し、物理SELECT＋STARTで開いたメニューの背景と文字を正常と確認。音声・ゲーム操作・メニューからの終了は今回の確認範囲外。検証記録を `docs/validation/rg280v-quicknes-color-2026-11-15.md` に追記した。

## 2026-11-15 — RG280V QuickNESの色修正

- V90S・TRIMUI-SのGit履歴とRG280Vの画素経路を比較。QuickNESのRGB565バイト順と既定NESパレットの差を特定した。
- FCEUXの既定64色をQuickNESビルドへ適用し、PicoArchのバイト順補正をQuickNESだけに追加。実機でMario画面が修正済みFCEUmmと全76,800画素一致し、計測上59.91 FPSでFEへ復帰した。通常の音・操作・終了はユーザー確認待ち。詳細は `docs/validation/rg280v-quicknes-color-2026-11-15.md`。
- FEからのQuickNESメニューで背景色が崩れるとユーザーが報告し、DRM画像でも再現。SDLの切り替え済みバッファから背景を読む実装を改め、ゲーム画面を表示直前に保存し、メニュー用のRGB565順に直してから暗くする方式へ変更。最初の補正案と灰色になる比較案は撤回。自動メニュー試験で背景が暗い青、文字が読める状態を取得し、通常版のMario画面はFCEUmmと画像ハッシュ一致・59.92 FPSを確認。通常の物理キー試験は確認待ち。

## 2026-11-15 — RG280V FEのSELECTコアメニュー

- V90S由来のSELECT画面はFEソース内にあり、NESの候補が単体FCEUXのみだった。FCEUmm・Nestopia・QuickNESをNESの選択肢に追加し、既定のFCEUXは維持した。
- RG280Vの320×240表示で文字とCPU行が切れていたため、画面倍率・行配置・長いコア名の描画を調整。実機DRM画面でNESと長いSFCコア名の表示を確認した。
- FEスクリプトでTOP単位の切替とROM単位の画面遷移を確認。試験用の上書きを解除し、FEを復帰させた。物理SELECTボタンの確認はユーザーへ依頼済み。詳細は `docs/validation/rg280v-fe-select-menu-2026-11-15.md`。
- ユーザーの物理試験でSELECTメニューが開かないと判明。RG280Vの機種定義ではSELECTが `KEY_ESC` だが、FEは無視していた。RG280V限定でSELECTへ割り当て、ビルド・ADB配置・ハッシュ照合・FE再起動・機種一覧のDRM取得を完了。物理ボタンの再確認を依頼した。
- 物理SELECTでメニューは開いたが、長いコア名で項目の文字倍率が変わると報告。幅超過時の縮小を廃止し、2倍文字に統一。値だけ横スクロールさせるよう変更し、長いSFCコア名のDRM画像で倍率を照合した。スクロールの実機視認は確認待ち。
- ユーザーから横スクロールは見づらいとの指摘。スクロールを撤回し、RG280VのSELECT項目を同じ18pxの文字で描く方式へ変更。CORE行の重複する語と括弧を省き、種類の `PICO:` などは残した。実機DRM画像でSFCの長いコア名が画面内に収まることを確認し、ユーザーのNES選択は保持した。ユーザーも物理画面で文字サイズが揃い、読めると確認した。

## 2026-11-15 — RG280V PicoArchの色と拡大処理

- 996 MHzのままNES低FPSを再現し、PicoArchの最近傍拡大処理を行単位で高速化した。FCEUmmは19.8から58.8 FPS、Nestopiaは19.8から59.8 FPSになった。既定の走査線効果と文字向け最適化を外した。
- FCEUmmのコア出力とPicoArch変換後の画素を実機から採取した。どちらもNESの青として正しかったが、DRM取得画像では水色に化けていた。XRGB8888由来の画面だけ、SDL反転直前に16ビット画素のバイト順を修正した。単体FCEUXとMarioの空が同じRGB値になった。
- 全コアの画素を入れ替える試験では、もともと色が正常なPICO-8が崩れたため撤回。形式別の最終ビルドではPICO-8の色を維持した。QuickNESのパレット差、PICO-8の23.7 FPS、Snes9x 2010の黒画面は残る。詳細と試験範囲は `docs/validation/rg280v-picoarch-color-and-scaler-2026-11-15.md`。
- 最終バイナリをSD1へ配置してSHA-256一致を確認。FEが復帰し、CPUは996 MHzのまま。通常のFE起動・メニュー・音の物理確認は未実施。

## 2026-11-15 — RG280VのCPU周波数比較を開始

- 低FPSコアの比較に先立ち、実機の設定可能な周波数が最大1200000 kHz、現在値が996000 kHzであることを確認した。前回1200000 kHz変更直後に停止したため、先に1092000 kHzを試した。
- 1092000 kHzへの書き込み直後にADBがofflineとなり、IP応答も消えた。Mac側USB Ethernetはactive。戻しコマンドの実行と実機周波数は確認できず、同周波数以上でのコア計測は行っていない。実機復帰後に996000 kHzとFEを確認する。詳細は `docs/validation/rg280v-picoarch-cpu-frequency-2026-11-15.md`。
- ユーザーが本体をリセットした後、IPとADBが復帰した。現在周波数・設定値は996000 kHz、FEプロセスも稼働中。指示に従い上限値も996000 kHzへ下げ、3値の一致を確認した。

## 2026-11-15 — Neo Geo CD の Fatal Fury WAV版で再試験

- ユーザーの指摘で、ROM2にMP3版と別の `Fatal Fury WAV` 一式があることを確認した。前回はMP3版だけを選んでおり、WAV版を見落としていた。
- WAV版約634 MiBをSD1のユーザ領域へ一時転送し、NeoCDコアで起動アニメーションの描画とPCM信号を確認した。最終計測窓は29.75 FPS。ゲーム本編、音質、操作、長時間安定性は未確認。
- 初回の大容量転送は180秒の制限で中断したため、ディレクトリ転送の時間上限を延長した。試験後に一時コピーを削除し、FEプロセスの復帰と容量回復を確認した。BIOSとROMの内容はGitへ含めない。

## 2026-11-15 — RG280V PicoArchの異常項目を再試験

- 起動試験用スクリプトでROM2のZIPをコア名に改名していたため、アーケードコアのゲーム識別が失敗していた。元のファイル名を保つよう修正し、FE再起動時にADBシェルを維持してプロセスの復帰を検証した。
- PicoArchホストへLibretroの単調時刻・性能計測インターフェースを実装し、Lutro Pongが実機で描画され約60 FPSで更新された。更新した実行ファイルは端末とMacでSHA-256一致を確認した。
- ユーザー所持のBIOS・機種データをSD1に試験用として配置し、Hatari、O2EM、PC-FXの起動段階が進んだ。CannonballとDinothawrはバンドルの配置修正で画面が出た。これらのBIOS/ROMはGit・イメージに含めない。
- Neo GeoはZIP名と親BIOSの配置で起動するが緑の横線と47.83 FPSを確認した。NeoCDはBIOSを見つけた後、検証用CUEのMP3トラック非対応で停止。BlueMSXは機種データ追加後も画面・速度が不十分。その他の未解決項目と判定限界を `docs/validation/rg280v-picoarch-remediation-2026-11-15.md` に記録した。
- Neo Geoを等倍・フィルターなしでも再試験したところ59.01 FPSまで改善したが緑の描画破損は残った。試験用設定は端末から削除してFEプロセスの復帰を確認。描画破損は拡大処理だけの問題ではない。
- BlueMSXの別ディスクをMSX指定で再試験したが起動直後に終了。試験用設定を削除しFE復帰を確認した。MSXの機種指定だけでは解決しない。

## 2026-11-15 — PicoArchコア拡充の途中経過と実機障害

- V90SのFE設定で明示される19コアをRG280VのMIPS/uClibc向けにビルドした。V90Sの実機検証記録にはさらに多くのPicoArchコアがあり、そのうち追加57コアのビルドを試みて49コアで`.so`を生成、8コアはビルド失敗した。ARM専用の`uae4arm`など、レシピのないものは含まない。ビルド成功は実機動作を意味しない。
- 起動ラッパー、FEの機種別設定、ビルド・ADB配置スクリプトを追加した。19コアをSD1へ配置したが、個別の実機検証はPC Engine以外未了。NES用FCEUmmとQuickNESは実機で色が異常、音が遅い。既存の単体FCEUXは同じROMで色と音が正常だった。
- PicoArchのRGB555/XRGB8888入力をRGB565へ変換する修正を試したが、NESの異常は解消しなかった。画面更新の計測ではQuickNESが通常の比率拡大時に約27fps、等倍表示で約51fpsとなり、拡大処理が大きな負荷だと分かった。音声の遅さも低フレームレートと整合するが、原因の切り分けは未完了。
- 等倍表示の一時診断版を実機に置いた状態でCPU周波数1.2GHzへの変更を試みた直後、ADB通信が切れて本体画面が黒くなった。周波数変更との因果関係は未確定。ユーザーがリセットし、ADBが復帰した。CPUは996MHzに戻っており、一時診断版と計測用ライブラリを撤去してFEを再起動。ユーザーがFEを操作できることを確認した。
- 初期セットアップ画面が再起動時に一瞬表示された原因は、完了印がある起動でも毎回画面描画と完了処理を実行していたこと。SD1の`complete`と`.plumos-ready`は残り、p3もマウントできていた。完了状態では起動スクリプトから早期に戻るよう修正した。rootfsへ組み込んだ実機再試験はまだ。
- NESの異常なPicoArchプロファイルをFEから外して単体FCEUXを維持した。FDSはFCEUmmしかないため、コア修正まで非表示にした。実機設定の差分がNESプロファイルとFDSの表示設定だけであることを確認し、ADBで照合・配置した。今回のコア群を完成版として扱わない。
- 設定更新後のFE再起動で一度黒画面となり、FEプロセスが終了していた。再度起動するとDRM初期化とプロセス維持を確認した。`S95frontend`の停止処理に、前のプロセスがDRMを解放するまで最大3秒待つ処理を追加し、ADBで照合して配置した。待機処理を使った連続再起動試験は未実施。
- 追加コアのビルド失敗8件を調査し、`np2kai`、`opera`、`lutro`、`mednafen_pcfx`、`theodore`はMIPS向けのヘッダー・アーカイバ・スタック保護設定を修正してビルド成功。`scummvm`はV90Sと同じ軽量構成とアーカイバ設定でビルド成功。追加57コア中55コアがビルド済みとなった。`easyrpg`はクロスビルド済み`liblcf`が不足し、`km_duckswanstation_xtreme_amped`はCMakeがMIPSアーキテクチャを受け付けない。これらの追加コアはすべて実機未検証。
- 追加55コアをADBでSD1へ転送し、各一時ファイルのSHA-256一致後に本配置した。既存19コアと合わせてSD1上に74個の`*_libretro.so`がある。p2の空きは約639MiB、FEプロセスは継続しCPUは996MHz。追加コアのFE選択肢はまだ実装しておらず、起動・映像・音声・入力は未検証。動作確認済みと扱えるのは従来のPCE Fastだけ。
- V90Sの検証記録にある78コアとの差は4件。`easyrpg`と`km_duckswanstation_xtreme_amped`は上記のビルド障害、`km_puae_xtreme_amped`とARM専用の`uae4arm`はRG280V用のビルドレシピがない。ARM専用コアはMIPSへそのまま移せない。

## 2026-11-15 — RG280VへGCW Zero系エミュレータを導入

- V90S版のPicoArch起動経路を参照し、RG280V用のMIPS/soft-float PicoArchとBeetle PCE Fastを固定リビジョンからビルドした。FEのPC Engine起動設定だけを `picoarch:mednafen_pce_fast` に変更し、既存設定の他項目が不変であることをJSON比較で確認。SD1へバイナリと起動スクリプトをハッシュ照合して配置し、FEからBomberman ’93を起動した。DRM取得でゲーム画面とPicoArchメニューを確認し、ユーザーが映像と音声を正常と報告。最初のメニューは640×480向けの2倍文字で横にはみ出したため、1倍文字版へ更新し、ユーザーがメニュー表示を確認した。ソースとライセンスの同梱手順も追加し、SDイメージは生成していない。
- VSyncの確認時、PicoArchの `SDL_SWSURFACE` はKMSDRM側で非同期更新経路へ進むことが判明した。`SDL_HWSURFACE | SDL_DOUBLEBUF` に変更し、PicoArchをSHA-256 `e5efda529de0bdd1a4fed5e5dd45766682f85434cdc7024617654a78a5` でSD1へ配置した。一時的な `SDL_Flip` 計測器で、実機の画面フラグにダブルバッファが含まれ、300回の画面更新すべてで8ms以上待機したことを確認した（平均10.369ms、最小8.256ms、最大16.781ms）。KMSDRMの同期コミット経路が使われている。PC EngineゲームからExitでFEへ戻ることも確認した。診断器を外し、通常の起動スクリプトをSHA-256で復旧した。
- PicoDriveがMaster SystemとGame Gearにも対応するため、FEの両機種の起動設定を `standalone:picodrive` に変更。インストール済み設定の他項目は維持し、変更が両機種だけであることをJSON差分で確認した。設定をSD1へSHA-256照合して配置し、RG280V再起動後にFEの自動起動と起動設定の保持を確認。ROMの映像・音声・操作は実機試験中。
- Master Systemの実機試験で映像・音声は正常と報告されたが、物理Xを押すと早送りになり解除できなかった。Wonder Boy 3でA/Bを入れ替える比較版を試したところAがキャンセル、Bが決定になったため、元のA/B配置へ戻した。Master System/Game Gear起動時だけXの早送りを無効にするPicoDriveパッチを追加し、OPKを再ビルドしてSD1へSHA-256 `fc59832a5522b9e49da4b606e5faf5781b527c06db6008fb8dc11b00f1acb579` で照合して配置した。ユーザーがWonder Boy 3でA/Bの正常動作とXで早送りにならないことを確認した。新しいSDイメージは生成していない。
- FEのGame Gear一覧からPuyo Puyoを起動。ユーザーが映像・音声・A/B操作・Xの早送り無効・SELECT＋STARTのメニューからFEへの復帰をすべて正常と確認した。ADBでもPicoDrive終了後にFEプロセスが残っていることを確認した。
- Mega DriveのGenesis Plus GXでBare Knuckleを試験。音が異常で、ゲーム中に停止した。音声を無効にした比較ではゲーム操作はできたが、SELECT＋STARTでメニューを開こうとすると画面が進まなくなった。旧GCW0ソースのSDL音声要求を2048フレームから512フレームに変える一時的な診断ライブラリも試したが、ゲーム中に再停止したため不採用。停止したプロセスを終了し、FEが動作することと本来の起動ラッパーのSHA-256が一致することを確認した。この時点ではMega Driveの実機動作は未達。
- [PicoDrive](https://github.com/irixxxx/picodrive) の `9f46ee4` をRG280V用ツールチェーンでビルド。最初の実機試験ではBare Knuckleが起動し、ユーザーが音声は正常と確認。SELECT＋STARTでメニューを開けたが、起動直後の画面比率は異常で、メニューを一度開くと正常になった。SDLの初回モードが320×480、メニュー後のゲームモードが320×240となることをDRM取得で確認したため、初回モードを320×240にするソース修正を追加して再試験する。PicoDriveの動作確認は継続中。
- 初回320×240修正版を直接起動し、ユーザーが比率・音・操作を正常と確認。続いてFEのMega Drive起動先をPicoDriveへ変更してBare Knuckleを起動し、ユーザーが比率・音・操作・SELECT＋STARTメニュー・終了後のFE復帰をすべて正常と確認した。ビルドスクリプトを固定リビジョン・パッチ・固定SquashFS時刻で再実行し、OPKのSHA-256が2回一致することを確認。配布用イメージにはPicoDriveのライセンスと変更済み完全ソースのアーカイブを含める。新しいSDイメージは生成していない。
- RG280Vを再起動後、ADBでFEの自動起動、Mega Driveの `standalone:picodrive` 設定、OPKのSHA-256 `e21da3adb426fadc3d041f92ecc6c31fb1e69bf9e9aff7e897bc54a5da87c72b` を確認し、DRM画面取得でもFEの機種一覧を確認。失敗したGenesis Plus GX診断ライブラリと旧OPK、旧音声ライブラリをSD1から削除した。Mac側の診断用Genesis展開・ソース複製も削除した。
- PicoDriveを浅いGit取得から再ビルドし、Mac側のソース複製を約390MBから57MBへ縮小。実機確認済みバイナリと新ビルドの差分は埋め込まれたビルド日時の文字列だけだった。`SOURCE_DATE_EPOCH=0` で日時を固定し、連続2回のOPK SHA-256 `92fe01a5e0ce70dd108b213373c627032dbfebb094ec3a57f2c7a90e0044729f` と変更済みソースアーカイブのSHA-256 `8c11fddd19f60f8ec3c38de73e8f44164650d61cc09d842a9238b441db26cb22` が一致することを確認。固定版OPKをSD1へ照合して配置した。固定版を使った再度のゲームプレイは未実施。
- GBCのAkumanor Gaiden DX v1.0をFEから起動し、ユーザーが映像・BGM・入力・SELECT＋STARTのメニューからFEへの終了をすべて正常と確認した。Gambatte-DMSのGBとGBC双方で基本動作を実機確認できた。
- 通常のFEからSuper Mario Landを起動し、SELECT＋STARTのメニューから終了した試験では、ユーザーがFEへ戻ることを確認した。ADB側でもエミュレータが終了し、FEプロセスが継続していることを確認。直接起動テスト特有の黒画面は通常経路では再発しなかった。
- 計測ライブラリを外したGambatte正式版で、ユーザーがSuper Mario LandのBGMとアスペクト比設定画面からゲームへの復帰を確認した。直接起動した正式版は終了コード0で終わったが、同じADBセッションからFEを再開するとプロセスが残らず黒画面になった。別のADBコマンドでFEを再起動し、プロセスとDRM取得画像で機種一覧を確認した。通常のFEからの起動・終了経路を確認中。
- GB/GBCのGambatte-DMSを再試験。ユーザーがDr. MarioとSuper Mario LandのBGMは無音、メニュー効果音は正常と確認した。SDL音声診断ではゲーム中の48kHz/16bit/ステレオPCMは最大振幅4、メニューの44.1kHz PCMは最大3713だった。高品質リサンプラーを線形方式（`--resampler 0`）に替えた比較版では、ゲームPCM最大振幅30720となり、Super Mario LandのBGMが正常に聞こえることをユーザーが確認した。元OPKから起動定義だけを再現可能なスクリプトで変更し、実機へ配備した。Gambatte専用のSDL入力ライブラリでSELECT＋STARTをメニュー入力に変換し、物理電源キーとR1のメニュー入力を抑制。ユーザーがSELECT＋STARTでメニューを開けることを確認した。直接起動テストから終了した際はFE再起動が抜けて黒画面になったためFEを再起動し、DRM画面取得でも機種一覧の表示を確認した。次回の直接起動テストには終了後のFE再起動を含めた。比較版でアスペクト比の設定中に終了したのは、診断ライブラリが `SDL_OpenAudio` の引数を直接変更し、メニューからゲーム音声へ戻る際に自分自身を再登録する欠陥が原因と推定。正式版には診断ライブラリを含めず、メニュー操作を再試験する。
- ユーザーのFE試験で物理A/B/X/Yがそれぞれ「戻る/お気に入り/決定/表示切替」と判明。DTの `gpio-keys` ラベルとLinuxキーコードはA=29、B=56、X=57、Y=42で、V90S由来の共通割り当てと一致していなかった。RG280Vに限りA=決定、B=戻る、X=表示切替、Y=お気に入りへ修正し、ユーザーがボタン配置の改善を確認した。
- SD2のFAT32が `iocharset=iso8859-1` でマウントされていたため、UTF-8オプションで再マウントして一覧を再生成。`find` と一覧JSONでは「忍者龍剣伝」などの日本語名が正しく読めたが、画面ではまだ「???」だった。FEがフォントをSD2側から探す一方、配布フォントはSD1 p2の `/media/data/plumos/fonts` にあることを確認し、主フォントとCJK代替フォントの探索先にSD1 p2を追加。ユーザーが画面上でも日本語名を正しく読めることを確認した。
- FCEUX 2.6.6のマリオをプレイ中に本体側のWAV録音を取り、FCEUXの再生処理を通さず `aplay` で比較した。ユーザーには同じ異常音として聞こえたため、ALSA出力だけの問題ではない。`SDL.Sound.Quality` を0から1へ変更した実機試験では、ユーザーがBGMは正常になったと確認した。設定をグローバルとROM別の両方へ適用する起動前処理を追加。比較したNestopia 2020-01-01はROM読み込み後に終了コード11で停止したため採用しない。
- FCEUXのGCW Zero向けメニュー入力は物理電源キーに割り当てられている。plumOSの電源導線と衝突しないよう、FCEUX専用 `LD_PRELOAD` ライブラリでSELECT＋STARTをメニュー入力へ変換し、物理電源キーはエミュレータへ渡さない。実機でSELECT＋STARTからメニューを開けることをユーザーが確認した。試験用直接起動から終了した際に下地のADB READY画像が露出したため、FE起動時にfbdevを黒へ消去する修正を追加。FEからマリオを起動してメニューから終了し、ADB READYが見えずFEに戻ることをユーザーが確認した。
- NESの新しいFCEUX 2.6.6候補を単体起動した後、操作不能との報告を受けてADBで該当プロセスを終了し、FEを再起動した。原因を追うと、この試験用の直接起動は通常のOPKラッパーを通っておらず、再起動後の `/dev/input/event2` に `ID_INPUT_KEY` がない状態だった。さらに入力準備スクリプトは `udevadm control --reload` が終了コード2で失敗していた。`udevd` が起動していないためで、手動起動後はスクリプトが成功し `ID_INPUT_KEY=1` を確認した。入力準備スクリプトが必要時に `udevd` を起動するよう修正。再試験ではFCEUXが `/dev/input/event2` を開き、ユーザーがマリオを十字キーで操作できた。音は小さく途切れるなどの異常が続く。FCEUXを終了してFEへ戻し、記録済みPCMの標準再生による切り分けを開始した。
- 4機種の目視試験: NES/FCEUXは悪魔城伝説の映像が出たが音が異常でメニューが開かなかった。GB/GBC/Gambatteは映像が出たが無音でメニューが開かなかった。SFC/PocketSNESはユーザーが映像・音・メニューを正常と確認。Mega Drive/Genesis Plus GXは起動画面が出たがゲーム開始後に停止し、音も異常だった。停止時 `gen_gcw0` の音声スレッドが `__snd_pcm_lib_xfer` で待ち、メインスレッドがfutex待ちだった。停止したエミュレータを終了してFEを再表示した。画面取得ツールにRGB565（`RG16`）を追加し、各エミュレータのDRM映像をPNGで確認した。NES、GB/GBC、Mega Driveの不具合は未修正。
- ReGBA 1.9.2の `Hardware` はSDLの拡大設定をラッパーからアスペクト比維持・最近傍へ指定し、比率と鮮明さが改善した。一方、`None` は銀色の枠と黒い枠が交互に出た。DRM画面を連続取得すると、公式ReGBAは枠を最初の3フレームにしか描かず、SDL/KMSDRMの3枚バッファのうち1枚に枠がないことを確認した。枠画像を一時的に外す試験は点滅を止めたが、ユーザーから枠を戻すよう指摘された。
- 公式ソースを現行BuildrootとOpenDingux 2022のツールチェーンで再ビルドしたが、前者はゲーム起動時にSIGSEGV、後者は浮動小数点ABIの相違で `ELIBBAD` となった。後者をsoft floatとして実行可能にしてもSIGSEGVだったため、再ビルド版は採用しない。公式1.9.2 OPKと銀色の枠を維持し、ReGBAだけSDLの3枚バッファを2枚へ変える `LD_PRELOAD` 互換ライブラリを作成した。RG280V実機で起動し、DRM取得した連続6枚の枠領域のハッシュが一致した。ユーザーも物理画面で枠が表示され、点滅しないことを確認した。OPK・ライブラリ・ラッパーはADB転送後のSHA-256を照合した。不要になった試験用ツールチェーンのアーカイブとDockerボリューム、失敗した試験OPKを削除した。
- ReGBA 2019版を実機で試したところ、ユーザーから緑の線とメニューを開けない問題が報告された。DRMの表示中フレームを取得する診断プログラムを一時的に作成。従来のfbdev取得はFEの古い画面しか読めなかった。ReGBA 1.9.2のDRMフレームは `XBGR1555` で、最初のPNG変換では誤ってRGB565として読んでいたため、取得画像に偽の緑色が出た。正しい15bit変換でGoodboy Galaxyの画面を確認した。
- [ReGBA 1.9.2](https://github.com/jdgleaver/ReGBA/releases/tag/1.9.2)のRG350用OPKを一時試験。Castlevaniaでユーザーが表示改善とSTART＋SELECTのメニュー表示を確認。Goodboy Galaxyも同梱BIOSで起動し、ユーザーが綺麗な表示を確認した。同梱BIOSは[ソース公開済みのGPL代替実装](https://github.com/jdgleaver/ReGBA/tree/1.9.2/bios)で、OPK内とソース内のバイナリハッシュが一致した。MIT代替BIOSを入れた1.9.2版はGoodboyが起動画面から進まなかったため採用しない。取得・展開・新規イメージ用の指定を1.9.2へ切り替え、旧版の再パック処理を外した。
- 追試で旧OPKのSDL 1.2 KMSDRMが `ID_INPUT_KEY` を持たないGPIOキーを列挙せず、ROMを起動しても入力FDがないことを発見。udevルールで `gpio-keys` に識別を付け、ReGBAが `/dev/input/event2` を開くことを `/proc` で確認した。新規イメージ用rootfsにルールを追加し、既存SDでもOPK起動前にルールを適用するラッパーを追加。ADB展開スクリプトで一式を再配置し、転送ハッシュと入力識別を確認した。再起動後の適用と物理キーの反応は確認待ち。
- V90S版の `plumos_text_ui.c` を取り込み、FEがROMを選んだ後に起動計画を作り、エミュレータ終了後にFEを描画し直す経路を追加した。NESのFCEUXで、FE→ROM→FCEUX→FEの遷移をADBのスクリプト操作とプロセスログで確認した。
- [RG350_APPREPOSITORY](https://github.com/RafaVico/RG350_APPREPOSITORY/) のコミット `2ed8306` にあるOPKをSHA-256固定で取得した。NESはFCEUX、GB/GBCはGambatte-DMS、SFCはPocketSNES、Mega DriveはGenesis Plus GX。GBAはReGBAを試した。
- Gambatteに不足するSDL_image/SDL_mixer、Genesis Plus GXに不足するlibogg/libvorbis、SFC/GBAに不足するlibpng14をJZ47xx向けにビルドし、SD1 p2の `/media/data/plumos/lib` に配置した。OPKからだけ `LD_LIBRARY_PATH` に追加し、ベースrootfsの共有ライブラリは置き換えない。
- ReGBAの元OPKには純正GBA BIOSと同じMD5のファイルが入っていた。最終イメージへは入れず、MITライセンスの[代替BIOS](https://github.com/Cult-of-GBA/BIOS)に差し替えたOPKを再生成した。再生成物のSHA-256と、実機のOPK内のBIOS SHA-256が一致した。BIOSを抜いただけの版は音声デバイスを開かなかったが、代替BIOS版は映像・音声デバイスを開いた。
- 直接起動試験ではGBC、SFC、GBA、Mega Driveの各ROMを指定してエミュレータプロセスが継続し、DRMとALSAを開いた。NESはROMロードとFE復帰も確認。GBはFEの起動計画でROMとGambatteの対応を確認した。ユーザーによる実画面・操作・音声の結果は確認待ち。
- PicoDrive旧OPKは `execve` が `ELIBBAD` で失敗したため採用しない。Mega DriveはGenesis Plus GXに変更した。現在のFE設定は既存項目を保持し、6機種の起動プロファイルだけ更新した。
- SDイメージは再生成せずADBで配置した。次回イメージ生成スクリプトにはエミュレータと補助ライブラリの同梱を追加したが、その生成物と実機起動はまだ検証していない。

## 2026-11-15 — RG280V FEの描画を60fps目標で改善

- V90S版FEの画面を実機で表示できたが、ユーザーからスクロールの点滅と引っ掛かりが報告された。320×480のfbdevは仮想画面の余白がなくページ切り替えに使えないため、メモリ上に1フレームを描いてから画面へ転送する方式を採用した。
- `PLUMOS_FBDEV_PROFILE=1` で描画と転送を分けて計測。変更前のギャラリー連続スクロールは約45ms/フレーム、うち描画約42ms、転送約3msで約22fpsだった。
- 32bpp矩形塗りを行単位のコピーに変更し、約33ms/フレームへ改善。ギャラリー背景PNGを外した対照試験では約10ms/フレームだったため、不透明な背景の描画結果をキャッシュして再利用するようにした。
- 同じ実機スクリプトで、画像読み込み後のギャラリーは平均9〜10ms/フレーム（約100fps相当）、TOPは平均約13〜16ms/フレーム（約60〜75fps相当）。初回のPNG読み込みと一部20ms超のフレームは残る。通常FEのfbdev取得画像でTOP画面の表示崩れがないことを確認した。物理キー操作での体感はユーザー確認待ち。
- 最初の体感確認では、ユーザーからまだガクつくと報告された。物理操作中のログではギャラリー約62fps、TOP約59〜60fpsで、描画時間だけでは説明できなかった。ギャラリーの移動アニメーション360msが長押しのキー繰り返し95msより長いことを調べ、試しに移動を90ms、TOPのページ遷移を180msへ短縮した。ユーザーによるとスクロール速度が上がっただけだったため、両方を元の360msと1000msへ戻した。
- fbdevの `FBIO_WAITFORVSYNC` を実機で試し、成功することを確認した。背面バッファからの転送直前に垂直同期を待つよう変更した。静止時のギャラリー更新間隔のみ33msへ延ばし、遷移中は16msのままにした。この版はユーザーの実機操作で滑らかになったと確認された。
- DRMカード1は320×480の60Hzモードで、dumb bufferとpage flipを利用できる。2枚の画面バッファを作り、描画後に `drmModePageFlip` の完了を待って切り替える実験を追加した。実機でDRM開始と切り替えが成功し、ギャラリーの温間計測は平均約16ms/フレーム。現在はこの版の体感確認中。起動できない場合はfbdev同期版へ戻る。

## 2026-11-15 — V90S版FEをRG280Vへ移植（実機表示試験中）

- V90S公開版からFE本体、fbdev描画、ROMスキャナー、機種ロゴ、ギャラリー背景、フォントを取り込んだ。ソースとフォントのライセンス文書も同梱した。
- JZ47xxのMIPS/uClibc向けにクロスビルドし、320×480のfbdevを320×240の論理画面へ合わせた。GPIOキー `/dev/input/event2`、ALSA `PCM` 音量、バックライトを利用する。Wi-Fi項目と空のAppsをSTARTから外し、RG280Vで利用できる設定項目に絞った。
- ADB経由でSD1 p2へ展開し、各ファイルのSHA-256を端末上で照合した。SD2の13機種から697本のROMを検出。機種ロゴ付きのTOP、木目背景のROMギャラリー、音量・明るさ・情報の設定画面をfbdevから取得して確認した。ROMサムネイルはSD2に存在せず、代替文字を表示する。
- 当初ロゴと背景を配置し忘れ、カードの余白もV90Sの画面寸法のままで、元のデザインを再現できていなかった。ユーザーの指摘を受け、V90Sの実機写真とテーマ資産を再確認し、同じ素材と描画処理をRG280Vの解像度に合わせた。
- 自動起動用 `S95frontend` と既存状態画面との競合防止を実装した。ソースからのイメージ生成時はFEをSD1 p2へ同梱する。これらの起動時動作、物理キー操作、ROM起動はまだ未確認。

## 2026-11-15 — RG280V初回セットアップの実機修正

- 試験用SD1で初回起動。p3の領域作成、再起動、FAT32 `PLUMOS` の初期化までは成功し、`p3 mount failed` で停止した。ADBログで確認した。
- 原因1: 読み取り専用SquashFSに `/media/user` がなく、起動時の `mkdir` は失敗していた。ビルド後処理でマウント先をrootfsに含めた。
- 原因2: 再起動後は `rcS` がp3をマウント済みなのに、初回セットアップ側が `/proc/mounts` の行頭を誤って判定し、二重マウントを試みていた。デバイス名とマウント先を列単位で照合するよう修正した。
- 修正版rootfsをADBでSD1へ転送し、端末上でSHA-256を照合して起動用FATへ配置した。旧rootfsは退避した。再起動後、p3のRWマウント、`complete` と `.plumos-ready`、ユーザーディレクトリ、起動ログの `READY` を確認。さらに再起動して同じ状態を確認した。
- seedイメージを同じファイル名で再生成し、領域表、含まれるrootfs、SHA-256を照合した。更新後の `output/plumos-rg280v-firstboot-seed.img` は `60ce9128257b7a93af52717274279fe3aae657003faff5eda1f0d81061e7f691`。以前のハッシュ `7988a97e...` の版は上記2点の不具合を含む。
- 端末の起動領域には元のrootfsを復旧用として残し、失敗した中間版と転送用の一時ファイルを削除した。

## 2026-11-15 — 試験用SDイメージの整理

- Macの容量確保のため、過去のbringup試作5本と対応するハッシュ、古いSD領域コピー4本を削除した。
- 現在書き込みに使う `plumos-rg280v-firstboot-seed.img`、起動済み構成へ戻すための `plumos-rg280v-adb-bringup.img`、SD領域の控え `rg280v-card-data-current.dmg` は保持した。
- `output` は約23GiBから12GiB、Macの空き容量は約68GiBから80GiBになった。ビルド用ファイルとログは変更していない。

## 2026-11-15 — 初回セットアップの設計見直し

- ユーザーの指摘で、RG280VにはV90S型の初回セットアップが未移植と確認した。前回の固定512MiB p3は初回セットアップではない。
- V90Sのseed生成、initramfsの領域検査・拡張・FAT新設・中断再開・完了印・ルート切替をソースから調べた。
- JZ47xx版の条件と実装順序を `docs/first-boot-design.ja.md` にまとめた。設計を先にコミットしてから実装する。
- 実装: 新しいp1/p2 seedのp2に `seed-v1` を置き、`plumos-first-boot` を追加。起動元、p1/p2の位置・ラベル、カード容量を検査してからp3を末尾まで作成する。再起動後、作成意図が記録され、p3が未フォーマットの場合にだけFAT32を作る。準備中・失敗時の大きな画面、FATとext4のログ、完了印を追加。印のない旧開発SDは変更しない。
- 検証: Buildrootを再設定して `mkfs.fat` を含め、rootfsとseedイメージを再ビルド。シェル構文、ビルド検証、p1/p2の領域表とp2の印・画面データの同梱を確認。4GiBの模擬MBRイメージに `sfdisk --append` でp1/p2を維持したままp3を作る試験が成功。
- 生成物: `output/plumos-rg280v-firstboot-seed.img`、SHA-256 `7988a97ea66527d82921dc98b080b3344823a35636949f7c1cdf799c32ec3f82`。
- 未確認: RG280Vでの初回起動、領域表変更後の自動再起動、p3のFAT初期化、p3の全容量、途中停止からの再開、画面表示。実機の確認前に完成版とは扱わない。
- 実機書き込み準備: 試験用SD1をMacの `disk5`（123729870848 bytes、内蔵SDXCリーダー、p1 `PLUMOSBOOT`、p2 Linux）として確認。イメージのSHA-256は上記と一致した。`diskutil unmountDisk` 後に管理者権限で先頭1.5GiBのバックアップを試みたが、macOSが raw SD の読み取りを `Operation not permitted` として拒否し、バックアップ・書き込みとも未実施。ユーザーが書き込み操作を引き継ぐ。書き込み先はこの試験用SD1、ファイルは上記seedイメージ。

## 2026-11-15 — RG280Vのユーザーデータ領域を分離

- 開始時点: RG280VでLinux 6.8、ADB、SD2の読み取り、状態画面の自動表示を実機確認済み。既存の試験イメージはSD1 p1 FAT + p2 ext4。
- V90S実機へSSH接続して確認した構成: 読み取り専用SquashFSルート、管理対象のext4、ROM・BIOS等のユーザー用FATを分離している。
- 今回の作業: RG280V新規イメージにSD1 p3 FATを追加し、起動時に任意マウントする。既存の2領域SDの起動を維持し、SD2は変更しない。
- 実装: p3を512MiBのFAT32 `PLUMOS` としてイメージへ同梱し、`roms`、`bios`、`apps`、`updates` を用意。`rcS` は起動元SDのp3だけを調べ、FAT種別とラベルが一致した場合に `/media/user` へマウントする。p3がなければ従来通り進む。SD2の処理は維持。
- 検証: Buildroot再ビルド成功。rootfs内に新しいマウント処理が含まれることを確認。ビルド検証スクリプト、シェル構文、`fsck.vfat -n` が成功。新規イメージのp1/p2/p3のセクタ内容照合とFAT内のディレクトリ確認が成功。
- 生成物: `output/plumos-rg280v-adb-bringup.img`、SHA-256 `d8d7b893b769c6acaa2370802a200789ad56a1ba7e82b15b74d604cb63d9f19d`。
- 未確認: 新規3領域イメージのRG280V実機起動とp3マウント。既存2領域SDでの起動実績は前回のもので、この変更後のrootfsでは再試験していない。

## 2026-11-15 — RG280V PicoArchコアのROM起動試験

- SD1の74コアすべてをlibretro APIとして読み込み、SD2と `rom2` のROMを拡張子・機種に照らして選定。VMU用VeMUlatorだけ対応データがなく、残り73コアで短時間のROM起動試験を実施した。
- DRM画面を2時点で取得し、SDL画面更新のFPSとPCM音声のゼロ標本率を記録。実ROM画像はGitに入れず、コア別のROM名・測定値・画面ハッシュ・判定を `docs/validation/rg280v-picoarch-smoke-2026-11-15.md` とCSVへ残した。
- NES 3コアは同一BaseballでFCEUX参照画像と枠色が異なり、19.8〜29.6 FPS。PCE Fastは60.0 FPSで非ゼロ音声。SFCは2002/2005系が概ね60 FPSだが、標準版と2010は低FPS。複数のコアで全黒・起動直後終了・シグナル終了を記録した。BIOS不足やROM構成の問題とは未分離。
- GBAの6コアは小さな言語選択画面が出ていたため、画像の非黒面積だけを使った「全黒」判定を訂正。音声値とFPSだけでは実プレイ時の色・音の正常性を証明できないことを報告書に明記した。問題のあるコアは今回は変更していない。
- 制限時間後にFEを手動で再起動し、DRM取得画像でFE画面が復帰したことを確認。自動復帰は3回失敗したので、次回用に復帰待機を延長したが実機再検証は未了。SD1の試験用コピーは削除し、空き約638 MiBを確認。

## 2026-11-17 — RG280V GCW Zeroアプリ Bard

- Calculatorの結果枠とCommanderの表示・操作はユーザーが実機で正常と確認。次のソース公開アプリとしてBard Storytellerを移植した。
- 上流コミットを固定し、BuildrootのFlite、libzip、SDL_ttf、SDL_gfxを使ってMIPS Soft float版をビルド。変更パッチ、再ビルドスクリプト、OPKと変更済みソースのSDイメージ同梱処理を追加した。
- 文字の縦潰れを受け、320×240で描画してRG280Vの320×480表示へ縦2倍に拡大。ユーザーが縦横比を自然と確認した。メニュー全項目を収め、FEのAppsから起動してQuitからFEへ復帰する経路を実機で確認。読み上げ音も実機で正常と確認された。外部文書の読書は継続確認項目。

## 2026-11-17 — RG280V GCW Zeroアプリ FFPlay

- FFmpeg-GCW0 のソースを固定し、MIPS Soft float で FFPlay と必要な共有ライブラリをビルド。RG280V の表示比率、SDL 動画表示、ボタン割り当てを修正した。
- SD1/SD2 のメディア選択画面を追加し、OPK と変更済みソースをイメージ生成に組み込んだ。実機へ転送しハッシュ一致を確認した。
- 単独試験で動画表示後に FE プロセスがない黒画面が発生したため、FE を復旧。通常の FE → Apps 経路で30秒の合成動画を再生し、再生中の映像と終了後の FE 復帰を画面取得で確認した。音と操作の実機評価は継続する。詳細は `docs/validation/rg280v-ffplay-2026-11-17.md`。
- その後の試験でPCM音声付きAVIが開始直後に終端へ進む事象を確認。音声なしAVIは実時間再生、AAC音声付きMP4は再生中の画面取得とユーザーによる映像・音の正常確認ができた。SELECT終了後のFE復帰も確認。FFPlayのファイル選択後に画面解放待ちを追加し、実行ログを保存するようにした。合成試験ファイルはSD1から削除した。PCM AVIの互換性は未解決として記録。

## 2026-11-17 — RG280V GCW Zeroアプリ Gmu

- GCW Zero版のGmuソースを固定し、MIPS Soft floatでSDL画面とMP3・Ogg Vorbis・FLACプラグインを再ビルド。RG280Vの画面比率とABXY入力を修正し、OPKと変更済みソースをイメージへ組み込んだ。
- FEのAppsから起動し、STARTの画面切替、SELECT＋STARTの終了とFE復帰を確認。3形式の合成音声でファイルとALSA PCMデバイスを開くことを確認。聴感はユーザー確認待ち。
- 上流GCW Zero設定の長いプレイリスト項目が保存時に切れて開始フォルダーの項目を壊す問題を発見。短い一覧に置換し、保存・再起動後の開始フォルダー保持を確認した。詳細は`docs/validation/rg280v-gmu-2026-11-17.md`。
- ユーザーの実機試験で無音と音量キーによる暗転が判明。Gmuの音量有効範囲0〜15に対して初期値40を指定していたため、保存値が0となっていた。初期値を15へ直し、ユーザーが音を確認した。
- 未登録の`Lock`がキー番号0と解釈され音量キーで画面を消していた。未登録キーを無効値へ変え、ロック設定を外した。音量＋／−を注入した後もDRM画像で画面が残ることを確認。AでFLAC再生・フォルダー移動、Bで親フォルダーへの移動に変更し、A入力によるFLAC再生を確認した。物理ボタンでの最終目視は確認待ち。
- ユーザーが物理ボタンで正常と確認。その後、Gmu起動直前にApps一覧から名前が消える現象を報告。FEのDRM描画終了時、古いApps一覧を含むfb0へ戻っていた。現行の表示バッファをfb0へ写してからDRMを解放する修正を入れ、3秒の診断待機中もGmu行が残ることを取得画像で確認。診断待機は撤去し、Gmu起動とFE復帰を確認した。合成試験音3本はハッシュ照合後にSD1から削除。

## 2026-11-17 — RG350単体エミュ候補の調査

- RG350 APPREPOSITORYのEmulators一覧から32X、Neo Geo Pocket、WonderSwan、ArcadeのOPKを取得してELF ABIと共有ライブラリ依存を確認。既存Soft float環境へ直接追加できるかを切り分けた。
- 既存の単体PicoDriveで32X ROMの起動とSH2 DRC初期化を確認。実プレイFPSは未測定。32XをFEに再表示せず、単体PicoDrive経路を無効機種の候補として追加した。配布版32X OPKはSDLマウス初期化に失敗し、試験後に端末から削除。FE復旧を確認した。詳細は`docs/validation/rg280v-rg350-standalone-audit-2026-11-17.md`。
- 追試で計測用SDLフックからSTARTを複数回送り、After Burnerの本編へ進めた。画面の異なる2時点をDRMで取得し、後半のFPS窓は25.64〜56.81で不安定。44.1 kHzステレオPCMの非ゼロ信号と実時間のコールバック、クリップ率0%を記録した。音の聴感と物理入力・通常メニュー終了は未確認。32Xは性能条件を満たさないためFE表示を無効のままとした。
- ユーザーの指定に従い、Emulatorsの配布OPK全62本を登録順に静的監査・実機起動した。26本にはSD2のROMを指定し、8秒ずつDRM画面、SDL画面提示、PCMコールバックを記録。16本で画面提示、13本で音声コールバックを取得したが、非ゼロPCMは2本のみ。25本は旧共有ライブラリ不足を報告。タイトル・メニュー値をゲーム中の性能値とは扱わない。
- Neo Geo PocketのRace ExplorerはROMを読み込みチーム・メンバー選択まで進み、後半は約60 FPSと非ゼロPCM。NES FCEUXはBaseballのチーム選択まで約60 FPSだがPCM無音、Mega Drive Genesis Plus GXはBare Knuckleのオープニングで約60 FPS・非ゼロPCM、GB Gambatte原版はSuper Mario Landのゲーム画面で約60 FPSだがPCMほぼ無音。配布原版と既存FE改修版は別判定とした。全62件の個別理由と測定範囲は`docs/validation/rg280v-rg350-standalone-audit-2026-11-17.md`。
- 試験用OPKは各回で削除、FEを最終復旧して実行プロセスを確認。ROM、OPK、スクリーンショットはGitに入れていない。実機での音質・操作・ゲーム終了経路は、候補別の追加確認が必要。

## 2026-11-19 — PyMenuの追加

- 推奨順の最初として、元のPyMenuソースをPython 3.11/Pygame 1.9.6の専用環境で移植。元のUIとテーマを維持し、Python 2依存の座標変換・辞書比較・scandirを修正した。
- 26機種・58の正規SA/PICO経路を取り込み、STARTのコア選択、NES起動、SELECT＋STARTメニュー終了、PyMenuのROM一覧への復帰を実機で確認。plumOS FEのAppsからの起動とFEへの復帰も確認した。
- 電源・音量・輝度・CPU管理はOS側を使い、既存の起動FEやSDL/ALSAは変更していない。再現用ビルド・導入スクリプト、パッチ、試験範囲をGitに保存。詳細は`docs/validation/rg280v-pymenu-2026-11-19.md`。

## 2026-11-19 — EmulationStationの追加

- 推奨順の2番目として、JZ4770向けのEmulationStationをソースからSoft floatでビルド。配布OPKのHard float実行ファイルは使わず、元のsimplegcwテーマを導入した。
- 26機種のFE既定経路を生成し、Apps起動、機種/ROM一覧、NES Baseballの起動、通常メニュー終了からES一覧への復帰、STARTのRETURN TO PLUMOSから元のFEへの復帰を実機で確認。
- UTF-8文字列の符号付きchar変換による起動時abort、現行GCCとのround衝突、320×480パネルの描画/クリップ座標を修正。専用SDL2_imageにJPEG対応を追加し、元テーマの背景を表示した。
- 全機種ROM画面の先読みをやめ、背景画像を表示高に合わせて縮小。読み込み画面の提示直後に消去しないようクリア順を修正した。診断コードは最終版から撤去。
- OS、カーネル、通常FE、既存フロントエンド、グローバルSDL/ALSAは変更なし。パッケージ用に一時変更したBuildroot設定も復元した。詳細は`docs/validation/rg280v-emulationstation-2026-11-19.md`。

## 2026-11-19 — EmulationStationカテゴリー移動時の異常終了

- ユーザー報告の「カテゴリーを開く／ROM一覧から戻る」で異常終了を実機再現。最初はCPCを開く操作、次はSEGA CD一覧から戻る操作で発生し、特定カテゴリーに限定されないことを確認した。
- 実機と一致するMesaのビルド情報から、etnavivのタイル画像コピー処理を特定。コピー幅の単位を修正し、部分タイルは汎用処理へ戻す修正を追加した。
- 修正版MesaをEmulationStation専用ディレクトリに配置。OSの共有ドライバは変更せず、ゲーム起動時は専用ドライバの検索設定を外す。
- 通常版バイナリで26カテゴリーを3周。各カテゴリーの「開く・下・上・戻る・次へ」計390操作を、同一プロセスで異常終了なしに完了。実機の読み込み先も専用ドライバであることを確認した。
- コピー処理の回帰試験は元のMesa関数と修正版を直接比較。元の関数は境界検査で失敗し、修正版はR8/RGBAのコピー一致と部分タイルのフォールバックを通過した。
- 導入時に共有ライブラリのシンボリックリンクを維持するよう修正し、重複コピーを削減。終了コードを通常ログに保存するようにした。診断用コードは通常版に残していない。

## 2026-11-19 — EmulationStationの機種表示取り違え

- PokeMiniにGame Boyのテーマを使っていた設定ミスを修正。PC Engine CDもPC Engineテーマを共用していたため、両機種に専用の表示名・既存plumOSアイコンを設定した。元テーマのレイアウトと共通素材を使い、TOPの機種名は文字で描画する。
- 全26機種の実機設定を、FE定義・ROMフォルダー・拡張子・起動スクリプト・既定コア・表示画像と照合。実在ROMの起動計画も実行なしで確認し、ほかの誤配線はなかった。専用の読み取り専用監査スクリプトを追加した。
- 今後の生成時に、複数機種へ同一のテーマIDを割り当てないチェックを追加。元のESで未対応のplatform IDはignoreとし、別機種扱いにならないようにした。
- GB、PokeMini、PC Engine CDの表示とROM一覧を実機の画面取得で確認。全機種の一覧は`docs/validation/rg280v-emulationstation-bindings-2026-11-19.md`。

## 2026-11-19 — PyMenuのNeo Geo画像欠落と一覧復帰

- PixelテーマのNeo Geo画像参照が、存在しない`images/pixel/`を指していた。実在する元の`images/pixel97/`へ修正。標準・Pixel・TFTの全26機種（計78組）のアイコン・フォルダー画像・背景の参照を点検した。
- 背景が読めない場合、メイン画面が共有描画面を消さず、ROM一覧と半透明帯が残る不具合を修正。毎回背景をクリアし、アイコン欠落時は機種名、背景欠落時は通常の既定背景を表示する。
- 元のNeo Geo画像で一覧へ入って戻った前後の画面一致を確認。さらに画像3点を一時退避し、代替表示で5回往復しても残像・表示崩れがないことを確認した。画像はハッシュ照合して復元し、plumOS FEへ戻した。
- Python本体を転送し直さずUIだけ更新する`--ui-only`を導入。ユーザーのテーマ設定・履歴・お気に入りは維持した。

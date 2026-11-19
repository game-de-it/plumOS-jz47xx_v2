# RG350 OPK 実機目視比較の準備（2026-11-17）

前回の機械監査で合格にできなかった Atari800、FBA44、Temper について、各3 ROMをRG280Vの `START → Apps` から選べるようにした。通常のFEエミュ登録は変更していない。項目名は `TEST Atari ...`、`TEST FBA ...`、`TEST Temper ...`。

| 候補 | ROM | 前回の問題 |
| --- | --- | --- |
| Atari800 | Caverns of Mars / Miner 2049er / Food Fight | Caverns of Marsは白帯、無音。残り2本は未判定 |
| FBA44 | Kung-Fu Master / Battle Chopper / Ninja Spirit | Kung-Fu Masterは色化け・音声ゼロ。残り2本は未判定 |
| Temper | Air Zonk / Blazing Lazers / Bonk's Revenge | Air Zonkは黒画面。残り2本は未判定 |

AtariとFBAのROMは 検証用ROMセットから試験用ディレクトリへコピーし、Temperは既存SD2のROMを参照する。旧readline/ncurses/OpenSSL/libaoは `/media/data/local/rg350-visual-tests/lib` だけに隔離し、製品の共通ライブラリには追加しない。FBA44は監査で使った、ROM引数を受ける試験用OPKを使用する。ROM、OPK、旧ライブラリはGitへ含めない。

配置コマンドは `python3 scripts/setup-rg350-visual-tests.py`。各転送後にホストと端末のSHA-256を照合し、Apps設定の9件を読み戻して確認した。FEプロセスが起動中であることも確認した。作業前のApps設定はGit管理外の `output/rg280v-apps/rg350-visual-tests/apps-before.json` に保管する。試験後は `python3 scripts/setup-rg350-visual-tests.py --remove` でこの9項目と試験用ファイルだけを撤去できる。

各項目はFEのAppsから単独起動し、終了時はFEへ戻る。操作不能になった場合はADBから該当プロセスを停止してFEを復旧する。実機目視ではタイトル画面だけでなくゲーム開始後の映像色、音、入力、速度、終了後のFE復帰を記録する。配置時点では9候補の実機目視結果は未取得であり、合格判定はしない。

## Atari800の目視結果

ユーザーが3項目を選んだところ、ボタン操作でいずれも終了した。端末の `runs.tsv` ではCavernsが3秒、Minerが3秒、Food Fightが1秒で終了し、全て終了コード10。各 `atari_*.log` は0バイトで、標準出力・標準エラーに説明はない。直後のカーネルログにAtari800のページフォルトやOOMは見当たらなかった。OPKのdesktopは `Exec=atari800 %f` であり、ROM引数の指定はある。OPK付属の説明書ではSELECTがメニュー、Aが発射、十字キーが移動となっているが、このRG280V試験ではその動作まで進めていない。3 ROMで同じ終了コードのため、ROM個別の合否を判断せず、起動・入力経路を調べる。

## FBA44の目視結果と後続ビルド

ユーザーはKung-Fu Masterで音声は正常だが、入力が効かず画面が二重に崩れると報告。DRM画像でも320×240の全面に走査線・色化け・重複表示を確認した。試験用ROMはOPKに読み込まれていた。旧FBA44の問題なので他の2 ROMだけで合格判定しない。TERMに応答しなかったため該当 `fbasdl.dge` にKILLを送り、FEのApps画面へ正常復帰した。キャプチャはGit管理外の `output/rg280v-apps/rg350-visual-tests/fba-kungfum-user-view.png`。

配布元 `plrguez/fba-sdl` の `r19_2021-10-18-.44_od_beta-fix-06` はRG280Vを対象にし、先行修正にKung-Fu Masterの256×246解像度と表示面の扱いが含まれる。ただし配布バイナリのELF属性はMIPS hard floatで、このplumOS環境のsoft float ABIに一致しない。13.5 MBのOPKは比較用に隔離して保存し、通常のFEには登録しない。ソースは取得済みで、soft float再ビルドと入力割当の確認が必要。

旧FBA44の `FBA_HWSCALING` を0から1にした短時間試験でもKung-Fu Masterの崩れは残った。設定は元に戻した。`scripts/probe-rg280v-fba-frame.c` でSDL_Flipの直前に320×240、RGB565、pitch 640の画素を保存したところ、既に画面が崩れていた。したがってこの画面の崩れはDRM転送後ではなく旧FBA44側の描画経路で発生する。

残り2本を同じ旧FBA44で8秒ずつ機械試験した。Battle Chopperの画面は目視で正常なランキング画面を表示したが、計測時は約30 FPS。Ninja Spiritのタイトル画面も目視では色・配置とも正常で、計測時は約19 FPS。どちらもゲームプレイ中の速度、音、操作は未確認。Battle Chopper試験後にFE自動復帰が一度失敗したため `S95frontend restart` で復旧し、FE稼働を確認した。両スクリーンショットはGit管理外の `output/rg280v-apps/rg350-device-audit-fba-{bchopper,nspirit}-visual/34.png` に保存した。

## ソースからの修正試験

試験用Appsだけをソース版へ切り替えた。通常のFEエミュ経路は変更していない。ROM、OPK、スクリーンショット、ビルドツリーは引き続きGit管理外。各OPKはMac側とRG280V側のSHA-256一致を確認した。

| 候補 | ソース・コミット | RG280V向け処理 | 実機で確認できたこと | 残る確認 |
| --- | --- | --- | --- | --- |
| FBA .44 | [plrguez/fba-sdl](https://github.com/plrguez/fba-sdl) `9448a9c6f1040ad8ec204b5e9cb83e25574ac0c8` | MIPS soft floatで再ビルド。配布OPKの`fbasdl.dge`のみ交換 | Kung-Fu Masterのタイトルとゲーム中の画面が正常。旧版でSDL画素の時点から出ていた重複・色化けが消失。ゲーム中画面まで進み、プロセスは45秒の計測時間内で動作 | 実機で音声・操作・終了、他2 ROM、FPS |
| Atari800 4.1.0 | [atari800/atari800](https://github.com/atari800/atari800) `d9d9ad1b47169d30b41e90b709dfc437844c9b9c` | `patches/rg280v-atari800-input-video.patch` で十字キー・A・START・メニュー入力をRG280Vに割当。生16 KB ROMを標準16 KB型のCART形式へ変換 | Caverns of Marsがタイトルからゲーム中へ進み、START・A・右入力後も終了せず動作。旧OPKはボタン押下後に終了コード10だった | 実機で音声・メニュー・終了、他2 ROM |
| Temper | [gameblabla/temper](https://github.com/gameblabla/temper) `a6c9ef2c5d1a086c22eb51980e07f3c38d0b42ae` | soft floatで再ビルドし、GCW専用IPU経路を外した比較版を作成 | Blazing Lazersのタイトル、Air Zonkの約25秒後のタイトルが表示。Air Zonkの初期黒画面は同じROMのPicoArchでも再現し、導入演出の途中だった | ゲーム中の映像・音声・操作・終了、IPUあり版との比較 |

FBAの配布バイナリはhard float ABIだったため、そのまま使用しない。ビルドスクリプトは `scripts/build-rg280v-fba-softfloat.sh`。ソースと依存ヘッダーは `output/rg280v-apps/rg350-visual-tests` 内に隔離し、ソースタグに含まれるKung-Fu Masterの256×246描画処理を取り込んだ。ビルド時のpng++は0.2.9、AVIRは2.5、JSONは3.9.1、BoostヘッダーはDebian bookwormの1.74を利用した。`Tag_GNU_MIPS_ABI_FP: Soft float`をELFで確認した。

Atari800の生ROMはカートリッジ種別が不明なため選択画面を出す。Caverns of MarsとMiner 2049erの16 KB試験ROMは、標準16 KB型を示す16バイトのCARTヘッダーを付けた。元ROMは変更していない。Food Fightの32 KB ROMには型を推測で指定していない。変換と試験用OPKの転送は `scripts/setup-rg350-visual-tests.py` で再現できる。

Temperの比較ビルドは `patches/rg280v-temper-noipu.patch` を使用した。Air Zonkの黒い導入場面はPicoArchとTemperの両方で数秒続き、約25秒後にタイトルが表示された。黒画面の単一キャプチャだけで不具合判定しない。IPU設定を外すこと自体の有効性は、この時点では未判定。

Atari800とTemperのパッチは上流ソースとの差分をゼロ行コンテキストで保存した。適用時は各ソースツリーで `git apply --unidiff-zero` を使う。元のソースツリーへ実際に戻せることを `git apply --unidiff-zero --reverse --check` で確認した。

試験OPKのSHA-256はFBA `f4222aad3205054eb777fa3a4a932a3a4eeba45808faa0a5e30f521377f65a49b3d`、Atari800 `2eeb984c95cb4c57fc0096f4d571a95a9e8ceb26a2d199a167a9a930793020bc`、Temper `ca599af6011ef011ea1b41a17c4d7f8941f93007d9e7ab222bdc01ecf851d7b9`。試験用Appsの9件を再照合し、FEプロセス稼働を確認した。

## SELECT＋STARTメニュー修正

FBA Kung-Fu Masterの映像・操作・音声はユーザーの目視で正常だったが、SELECT＋STARTではメニューを開けず終了できなかった。実行中のFBAはTERMに応答しなかったため、そのプロセスだけをKILLし、FEへ戻した。FBAの上流実装はSELECT＋STARTを2人同時スタートに使い、メニューは別のキーへ割り当てていた。`patches/rg280v-fba-input-audio.patch` でSELECT＋STARTを優先してGUIへ送るよう変更した。

同じ操作で他の試験用エミュもメニューを開けるよう、Atari800はSELECT単独をコンソールSELECT、START単独をコンソールSTARTとして残し、同時押しだけをGUIに送るよう `patches/rg280v-atari800-input-video.patch` を更新した。TemperはSDLのSELECT・STARTキー状態を追跡し、同時押しを1回だけメニュー操作として送るよう `patches/rg280v-temper-noipu.patch` を更新した。電源ボタンはエミュメニューには使用しない。

3本をsoft float ABIで再ビルドし、試験用Appsへ転送後、ホスト・端末のSHA-256を照合した。ADBから入力イベントのSELECT＋STARTを送って画面を取得し、FBA・Atari800・Temperの全てでメニューが表示された。画像はGit管理外の `output/rg280v-apps/rg350-visual-tests/{fba,atari,temper}-menu-chord.png` にある。自動試験では各プロセスを終了してFE起動を確認した。メニュー項目からの通常終了とゲーム復帰は、実機操作による確認が残る。

更新後のOPK SHA-256はFBA `8b935db05bb4bf9b1dc9ae4058627a5381ca804d7cfd52af3f1998fdc20e5652`、Atari800 `921793d7873f687f911a251d974448319f8409ba444cfa20c6880c7a0e49e4bc`、Temper `34cabae61b5c44f61e31eb4c05e8474fef3ed41e7e5cda5f42f55ac4987e3c73`。差分はいずれもゼロ行コンテキストで、適用時は `git apply --unidiff-zero` を使う。
TemperのSDLソースはCRLFなので、対応するパッチもCRLFを保持している。差分の空白検査には `git -c core.whitespace=cr-at-eol diff --check` を使った。

## Atari800の表示比率修正

ユーザーはAtari800のゲームとメニューが横につぶれ、メニュー文字を読めないと報告。DRM取得画像は320×480だが、有効なゲーム・メニュー画素は中央の y=120〜359 の320×240だけで、残りは上下の黒帯だった。FBAとTemperは320×240のDRMモードだった。Atari800へ `-fullscreen -fs-width 320 -fs-height 240` を渡す比較でも320×480のままで、SDLが列挙した解像度から選ぶ処理に原因が残った。

`patches/rg280v-atari800-input-video.patch` に `PLUMOS_RG280V` ビルド時の320×240解像度固定とフルスクリーン指定を追加した。メニュー・ゲーム共通のSDL表示設定だけを修正し、入力・ROM・他の試験用エミュは変更していない。`scripts/build-rg280v-atari800-test.sh` は設定済みのAtari800 4.1.0ソースと展開済み試験OPKを入力として、パッチ適用、soft floatビルド、OPK再作成を実行する。

修正版のCaverns of Marsは、ゲーム・SELECT＋STARTメニューともDRM画像が320×240になり、ゲーム絵とメニュー文字が画面の高さを使うようになった。取得画像はGit管理外の `output/rg280v-apps/rg350-visual-tests/atari-240-{game,menu}.png`。OPKのホスト・端末SHA-256は `12b3d15309e984bfc9744ec30ecb11e0aed8d8413db1c49a3f5517d606eb4b43` で一致し、試験後にFE起動を確認した。その後、ユーザーがAtariの全試験ゲームについて実機動作を正常と確認した。

## FBA Ninja Spiritの音声停止とメニュー復帰

ユーザーはNinja Spiritのゲーム中に停止し、その後の更新版ではメニューをBで閉じてゲームへ戻る際にFEへ落ちたと報告した。停止時の `fbasdl.dge` は `futex_wait_queue` で待機し、ログには `ALSA write failed (unrecoverable): Input/output error` が残った。上流のSDL音声リングは空きがなくなると無期限に待つため、コールバック停止後もゲームが進めなくなる。最初の修正では30 msの待機上限と音声破棄を追加した。メニュー前後と設定保存後の診断ログも出した。

比較版ではBでメニューを閉じる操作を3回繰り返しても15秒後までゲームプロセスが生存した。別の比較版でSDLの音声デバイスをメニュー中に停止しない方式も試したが、ALSAエラーは残ったので採用していない。現在の版ではBからの復帰後に `FBA menu: returned to game` まで記録され、15秒後もプロセスが生存し、ALSAエラーが出ない試行もあった。一方、メニューを開いた試行ではALSAエラーがなお再現している。メニューを開かず13秒動かした試行では出なかった。FEへ突然戻る現象の原因はまだ特定できていない。ログ末尾で復帰処理のどこまで進んだかを判別できる状態にした。

この診断用FBA OPKはホストと端末でSHA-256 `ebcb78dcf88cb575ea47712144bb6b0e578eeef44a6a04f7a578115c9acffc24` が一致した。ユーザーの実機試験では映像は続いたが、音は無音または異音となった。

音声停止後にSDLデバイスを自動で閉じて開き直す試験版は、ログ上 `FBA audio: SDL device reopened` まで進んだ直後にOS全体の応答が止まり、RESETが必要になった。この試験版は撤回し、FE起動を確認した。SDLデバイスの再開処理を実機へ戻さない。

次に `patches/rg280v-fba-input-audio.patch` でFBAの音声方式2をSDLコールバック式からALSA PCMの直接書き込みに変更した。PCMは非ブロックモードで開き、メニュー前後は `drop` / `prepare` でリセットする。書き込みエラーには `snd_pcm_recover` を試み、復旧できなければ次の音声フレーム以降に開き直す。旧SDL待機上限パッチはこの経路では使わないため除いた。ビルドはsoft float ABIで、`-lasound` を追加した。

ALSA比較OPKのSHA-256は `685ce81a4f9388093c17375fac04315d54636cd38ac8ff75fb689296ee02e446`。端末の試験用FBAへ適用する前に旧版を `fba-sdl-previous.opk` に保存した。Ninja SpiritでSELECT＋STARTからB復帰を3回繰り返し、各回10秒後もFBAプロセスが生存し、ALSAエラーは記録されなかった。試験後にFEの再起動を確認した。ソースを整理した再ビルドOPKは旧SDL修正コードを含まない。SHA-256 `d9c31ee651bf002d3902bfa0995eeb594377385f26d5e722b8e053e40f6fca77` がホストと端末で一致し、試験用FBAへ反映した。ユーザーによる音質と操作の実機確認を待つ。

## FBA Ninja Spiritの4 FPS調査

ユーザーの実機ではNinja Spiritが約4 FPSで、音質の判定が難しかった。音声なしでも画面表示は約5 FPS、ALSA音声ありでは約4 FPSだったため、音声方式だけが原因ではない。旧メインループは実時間から遅れると最大10フレームを連続でエミュレートし、最後の1フレームだけ描画していた。計測では3秒間に約130〜139フレームをエミュレートしても、描画は13〜14フレームだった。

追いつき処理を外して毎フレーム描画すると約16 FPSになり、M72の描画処理が重いことが分かった。描画処理をさらに分けると、512色パレットの32ビット参照と384×256画素への転送に約39 ms/画面を費やしていた。M72の16ビット出力時に16ビットのパレット表を使う修正で約2 ms/画面まで短縮した。診断版のゲーム中計測では、3秒間に108〜112フレームを描画して約36〜37 FPS。残るFBAコア処理は約25 ms/フレームで、目標の60 FPSには届いていない。CPUは従来指定の996 MHzで固定し、周波数は上げていない。

計測コードを外したOPKを作成し、ゲーム中の画面をDRMから取得して色と配置を確認した。取得画像はGit管理外の `output/rg280v-apps/rg350-visual-tests/nspirit-clean-bench.png`。さらに汎用転送処理と同じパレット参照ポインタの設定を保持した最終版を作成し、ホストと端末の試験用FBA OPKのSHA-256 `357215645ba9f9a4ed8874acfa2afd83d96cf68e59ccec65060b184b5ba50e55` が一致した。試験後はNinja Spiritの設定を元に戻し、FBAプロセスの終了とFEの起動を確認した。実機の音質・メニュー復帰と他のM72タイトルへの影響は、更新版での確認が必要。

ユーザーの最終版実機確認では約38 FPSで音飛びが発生した。したがってNinja Spiritは合格にせず、試験用Appsの候補として残す。画素変換の改善だけでは60 FPSに届かず、残るエミュレーション処理の高速化が必要。現在の計測では処理に約25 ms/フレームかかり、60 FPSに必要な約16.7 msを超える。音質とメニュー復帰も合格判定を保留する。

## FBA Kung-Fu MasterとTemperの実機確認

ユーザーはFBAのKung-Fu Masterが60 FPSで正常に動作すると確認した。これを試験Apps内の同タイトルの合格結果とする。FBAの他タイトルへは一般化しない。

Temperもゲームは60 FPSで正常だが、SELECT＋STARTでメニューを一度開くと、その後SELECTまたはSTARTを単独で押しただけでメニューが再表示される不具合があった。原因はゲーム入力側の同時押し判定が押下状態を保持する一方、メニュー側がキーを離すイベントを消費するため、ゲーム側の状態が古くなることだった。メニューから戻る際に同時押し判定を初期化し、PC Engine側のRUN・SELECTも離した状態へ戻す修正を `patches/rg280v-temper-noipu.patch` に追加した。再ビルド手順は `scripts/build-rg280v-temper-test.sh`。soft float ABIを確認し、OPKのホスト・端末SHA-256 `82f5404834e161c8fb4fd0c3d2006447bd8ed28ee18248a719038cfdcebc5ee8` が一致した。自動試験ではSELECT＋STARTでメニュー表示を確認し、試験終了後にFEへ復帰した。さらにユーザーが実機で、メニューから戻った後のSELECT・START単独押しと、再度のSELECT＋START同時押しを試し、動作正常と確認した。

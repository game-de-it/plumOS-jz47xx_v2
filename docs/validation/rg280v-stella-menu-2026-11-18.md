# StellaのRG280Vメニュー入力・終了修正

ユーザーから、Appsに追加したStellaでメニュー操作ができないとの報告。配布原版の画面は開いていたが、GCW Zeroのアナログスティックでマウスを動かす設計で、十字キーではボタンのフォーカスを移せず、Aもマウス位置のクリックになっていた。

## 修正

参照元は [DavidKnight247/Stella-3.9.3](https://github.com/DavidKnight247/Stella-3.9.3/tree/4c309195f666909e7c0a185bcc46da836fc234dd)、リビジョン `4c309195f666909e7c0a185bcc46da836fc234dd`。ソースを修正してsoft-float ABIで再ビルドした。

- メニューの十字キーはリスト・スライダー等の操作に渡し、その項目が方向入力を使わない場合は前後の項目へフォーカスを移す。
- メニューのAは決定、Bは戻る。物理A/BがSDLのCtrl/Altキーであっても、デスクトップ用ショートカットやマウスクリックとして扱わない。
- L/Rで前後の項目へフォーカスを移せる。X/Yはタブ切替。リストやスライダーから別の項目へ移る場合もL/Rを使える。
- START＋SELECTでメニューを開閉する。押下中のラッチと両キーの解放を処理し、単体キーの入力をメニュー復帰後に残さない。
- SELECT単押しは従来のAtari Resetを解放時に1フレーム送る。START単押しはResetしないため、plumOSのSTART＋左右による輝度調整と競合しない。
- 既存のキー設定を読み込んだ場合も、固定ハードウェアのメニュー移動・A/Bが有効になるようにする。ゲーム中のAによるFire、BによるConsole Select等は維持する。

旧版のlibpng警告も確認したため、新ビルドではSDKのSDL_imageとpng16をOPK内の専用ライブラリとして組み合わせた。共有の互換ライブラリは置換していない。

## 終了時クラッシュ

最初の入力修正版ではExit Gameを選ぶとFEには戻るが、終了コードが11だった。短時間のstraceで実際のSIGSEGVを確認し、MIPS PC `0x004dd170` をMac側のSDKで逆引きした結果、`OptionsDialog::~OptionsDialog()` に特定できた。

GCW0ビルドではRomAuditDialogを作成しない一方、`myRomAuditDialog` がコンストラクタで初期化されず、デストラクタで不定なポインタをdeleteしていた。`myRomAuditDialog(NULL)` を初期化リストへ追加した。終了を強制成功扱いにする処理は加えていない。

## 実機上の機械確認

- Asteroidsでゲームの描画と音声を取得。ゲーム中約60 FPS、PCMに信号がありクリップ0%。
- START＋SELECTでメニューを開き、下でVideo SettingsからAudio Settingsへフォーカスが移ることを画像で確認。
- AでAudio Settingsへ入り、Bでメインメニューへ戻り、さらにBでゲームへ戻ることを確認。
- メニュー開閉を3回繰り返した後も、ゲーム画面と得点の継続を確認。メニューを開く操作でResetされていない。
- 初期化不備の修正後、Asteroids、Centipede、Breakoutの3本すべてで、十字キーでExit Gameを選び、Aで終了すると終了コード0でFEへ戻ることを確認。
- START単押しをResetにしない最終版でも、3本のゲーム開始・約60 FPS・音声信号・START＋SELECTメニュー・Exit Gameの終了コード0・FE復帰を再確認した。

この記録は実機で取得した画像・入力注入・PCM・終了コードの確認。修正後の本体での目視・聴取はユーザー確認待ち。

## 配置と再現

Appsの `TEST 28 Stella 1: Asteroids`、`2: Centipede`、`3: Breakout` はすべて同じ修正版OPKへ更新した。以前の設定は端末の `.stella/stellarc.before-rg280v-menu` にバックアップした。

- パッチ: `patches/rg280v-stella-menu-input.patch`
- ビルド: `bash scripts/build-rg280v-stella-menu.sh`
- 配置: `python3 scripts/setup-rg350-stella-rom-tests.py`
- OPK: `output/rg280v-apps/stella-rg280v-menu.opk`
- 最終OPK SHA-256: `a343df29e2af4e94d8ce72a948f39933f3bc8cd10fab0a2b667ab9fca1b1cbb6`
- 初回の入力確認: `output/rg280v-apps/rg350-device-audit-stella-menu-fix-20261118-28-1/`
- 終了修正後: `output/rg280v-apps/rg350-device-audit-stella-menu-final-20261118-28-{1,2,3}/`
- 最終版: `output/rg280v-apps/rg350-device-audit-stella-menu-final2-20261118-28-{1,2,3}/`
- 手動操作中の取得画像: `output/rg280v-apps/stella-fixed-*.png`

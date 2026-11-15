# RG280V FE SELECTメニュー（2026-11-15）

V90S由来のFEにはSELECTで開くコア選択画面、TOP単位とROM単位の上書き、Bで戻る操作が既に含まれていた。RG280VのNESにはFCEUXしか登録されておらず、比較するコアを選べなかった。NESにPicoArchのFCEUmm・Nestopia・QuickNESを追加し、既定は単体FCEUXのままにした。3コアのバイナリは実機のSD1で存在を確認した。

RG280Vの320×240論理画面ではV90Sの3倍文字が横にはみ出し、CPU行が下部パネルに隠れていた。SELECT画面の文字倍率と行配置をRG280V用に調整し、長いコア名だけ1倍文字で収めた。V90S向けの大画面配置は変更していない。

実機検証では、ADBのFEスクリプトからTOPのNES SELECT画面を描画し、DRM画像を取得。4つの候補が `plumos-text-ui core system nes` に現れることを確認した。左右操作でNESのNestopia、SFCの長い `mednafen_supafaust` を一時選択し、画面内に収まることと設定反映を確認した後、両方の上書きを解除した。NESのROM一覧からSELECTでROM単位の画面が開くこともテキスト描画で確認した。試験後、通常FEのプロセスが動作し、NESはFCEUXの既定に戻っている。

実機配置したFEバイナリのSHA-256: `924c72639d77081e42a2da370bd9ce5c7425bbf8c95f1ba2293b1de3dca5e224`。`systems.json` のSHA-256: `0fda439f91e2152d95a76156078dba926ecf67e58b03698de42c255cfd31703a`。物理SELECTボタンからの表示とユーザーによる視認は確認待ち。QuickNESの色差は別件として残る。

## 物理SELECTの修正

ユーザーの実機確認では、上記版で物理SELECTを押してもメニューが開かなかった。`--script select` は画面遷移だけを試しており、物理キー入力を通っていなかった。RG280VのOpenDingux機種定義 `rg280v.dts` が取り込む `gcw0-base.dtsi` では、Select button は `KEY_ESC` と定義されていた。一方、FEは `KEY_ESC` を無視し、`KEY_RIGHTCTRL` 等だけをSELECTに割り当てていた。

RG280Vに限り `KEY_ESC` を `ACTION_SELECT` に割り当てて再ビルドした。修正版FEのSHA-256は `9b207474c5ead0c81065e63f413b8cc2c340cc46ebd1f43135d3a7d95139e8bb`。ADB復帰後にSD1へ配置し、端末側のハッシュ一致、FEプロセスの再起動、機種一覧のDRM取得を確認した。物理SELECTからメニューが開くかはユーザーに再確認を依頼した。

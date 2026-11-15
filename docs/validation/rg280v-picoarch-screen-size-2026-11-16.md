# RG280V PicoArchの共通Screen size（2026-11-16）

## 実機報告と対象

ユーザーはGame GearのFE登録4候補をすべて動作OKと報告。ただしPicoArchの「Screen size」にあるAspectやFullが効いていないように見えるコアがあり、既に確認したコアにも同じ問題があり得ると報告した。Game GearのPicoArchログにはGenesis Plus GX、PicoDrive、Gearsystemで同じSD2の`Columns [V1.0].gg`を起動・終了した履歴がある。候補構成は変更しない。

## 共通描画処理の修正

PicoArchの全Libretroコアは`plat_video_process()`から同じ`scale()`へRGB565画面を渡す。従来の`scale_select_scaler()`はNativeでも160×144を非整数倍率の約267×240へ拡大し、Aspectとの差が見えにくかった。またコアのアスペクト比が0の場合、最初のフレーム寸法から得た代替値をグローバルへ保存していた。画面サイズを変更しても、ダブルバッファの余白に古い画像が残る可能性があった。

`scripts/patch-rg280v-picoarch.py`で共通スケーラーを更新した。

- Nativeは画素比を維持する整数倍率で中央に描画。元画像が画面より大きいときだけ縮小して収める。
- Aspectはコアが報告した画面比率に収め、報告値0の場合はそのフレームの幅と高さから計算する。代替値は保持しない。
- Fullは320×240全域に描画する。
- ゲーム中にLibretroコアが`SET_GEOMETRY`または`SET_SYSTEM_AV_INFO`を送った場合、表示比率を更新する。後者ではFPS・音声周波数も更新する。
- 両面バッファで古い画素が残らないよう、各フレームで余白だけを消す。文字最適化とNativeの画面効果は維持する。

4:3の画像を4:3のRG280V画面へ表示すると、AspectとFullが同じ320×240になる。これは両モードが適用された正常な結果であり、視覚的な差を確認するにはGame Gearのような4:3以外の画像を使う。

## 確認

実際の`scale.c`をホストでコンパイルした`scripts/test-rg280v-picoarch-scaling.c`で11条件を検証し、全件通過。160×144はNative 160×144、Aspect 267×240、Full 320×240。256×192の4:3ではAspectとFullがともに320×240。240×160、320×224、640×480、コア比率0と4:3、未消去の描画先からの余白処理も検証した。

最終PicoArch本体SHA-256は`3fdad0d306ccc8d88eaa69618f9e5048860b5957bdc6fe160a5fb2db72581147`で、端末配置後のハッシュと一致。SD2のGame Gear ColumnsをGearsystemで11秒自動起動し、最終画面更新窓59.99 FPS、取得画像320×240で描画あり、PCM非ゼロ、FE復帰後PID 5021を確認した。

ユーザーが同じGearsystemで物理SELECT＋STARTのメニューからNative→Aspect→Fullへ切り替え、3モードとも表示幅が変化し、色・音・操作に異常がないことを確認した。端末ログにはGame Gear Columnsの起動とコア終了が記録され、PicoArch本体のハッシュは最終版と一致。ほかの全コアのROM別FPS・表示結果は個別には再試験していないが、3モードの寸法計算は全コア共通の描画経路に適用される。

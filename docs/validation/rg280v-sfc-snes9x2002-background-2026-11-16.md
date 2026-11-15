# RG280V Snes9x 2002の背景欠落（2026-11-16）

ユーザーはFEのSnes9x 2002でSD2の`Super Mario World - Super Mario Bros. 4.sfc`を起動し、速度・音は正常だが背景が真っ黒と報告。同じROMのChimeraSNES画面をDRMから取得して比較した。ROMのSHA-256は`c6808e082ab343be554d07f2b3eb157c3c5134b364a2ffb3806a67f17e0992d0`。

Snes9x 2002のタイトル画面はロゴ・選択肢・枠は描かれるが、中央の山・雲・木にあたる背景領域が黒い。ChimeraSNESでは同じ部分が描かれる。Snes9x 2002の`Transparency Effects`は上流コアで既定`enabled`、端末の当該コア設定ディレクトリに個別設定ファイルはなかった。性能・音声と独立した描画互換性の問題と判断し、SFCのFE候補から外す。コア本体とビルドレシピは調査用に保持する。

比較画像はGit管理外の`output/rg280v-emulators/snes9x2002-current.png`と`output/rg280v-emulators/chimerasnes-compare-title.png`に保存。SupafaustとSnes9x 2002を除いたFE設定のSHA-256は`e080035b496fd567699b98564652fd4db5691e0d267489aaaf465bef6ce2a67f`。端末へ配置して一致を確認し、ユーザーがChimeraSNESを終了した後にFEを再起動した。残るSFC候補はPocketSNES、Snes9x 2005、ChimeraSNES、Snes9x 2005 Plus、Snes9x 2010の順。

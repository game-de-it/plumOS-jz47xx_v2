# RG280V PicoArch「Show CPU %」表示修正（2026-11-16）

## 再現と原因

- RG280Vの「Audio and Video」画面をDRMから取得。`Show FPS` の次の行は右側の `ON` だけが見え、左側の `Show CPU %` が表示されなかった。
- PicoArchのメニュー定義には `Show CPU %` がある。共通メニュー描画で項目名を `text_out16(x, y, name)` と渡していたが、この関数は `vsnprintf` に渡す書式文字列を受け取る。末尾の `%` が書式として解釈されるため、文字列として渡す必要がある。

## 修正と確認

- `scripts/patch-rg280v-picoarch.py` で共通メニューの項目名を `text_out16(x, y, "%s", name)` へ変更した。エラー文も同様に固定書式で渡す。
- PicoArchを再ビルドして実機へ配置。ローカルと実機のSHA-256は `66d4a2154cbc7db786a3880947155f6e19344df3fb4a06dcf13e6b968aad4899` で一致した。実行中の旧版は維持し、新しい起動から修正版を使うようファイルを切り替えた。
- ユーザーが実行中のPicoArchを終了し、FEからQuickNESを再起動して「Audio and Video」に `Show CPU %` の項目名が表示されたと確認した。

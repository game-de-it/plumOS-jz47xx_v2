# RG280V PDF Viewer移植（2026-11-17）

OpenDinguxアプリ一覧の [PdfViewer](https://github.com/retrogamehandheld/OpenDingux/blob/master/Readme.md#applications) の配布ソース `pdfviewer.sourcecode.Hardyx.tar.gz` を使用した。取得元は一覧に記載されたGoogle Drive、原本SHA-256は `d42918c4fe1378384b296a9cce38cd34a534698e29bc70ae1ca5725e36220e83`。ビルド時もこの値を照合する。変更は `scripts/patches/pdfviewer-rg280v.patch` に保存し、`scripts/build-rg280v-pdfviewer.sh` でMIPS Soft floatのOPKと変更済みソースアーカイブを生成する。

元のGCW Zero設定は320×240の画面を使う。RG280Vでは320×240の論理面を320×480の実画面へ縦2倍に表示した。アプリが描画を更新する箇所を共通の `VideoFlip()` へまとめ、物理SELECT＋STARTで終了できるようにした。Aは決定・次ページ、Bはキャンセル・前ページとして元のGCW Zeroの画面内表示と一致する。ファイル選択は `/media/user/Documents/` から開始し、そのディレクトリがなければ `/media/user/` を使う。

| 確認 | 結果 |
| --- | --- |
| ビルド | Xpdf 3.02を含む77ソースをクロスビルド。`readelf -A` でSoft float ABIを確認 |
| FE登録 | Appsに `PDF Viewer` と表示。`opkinfo` でメタデータ確認 |
| 起動と描画 | DRMで320×480のフレームバッファと自然な縦横比を確認 |
| PDF表示 | 2ページの試験用PDFをファイル選択から開き、1/2・2/2の画面を取得 |
| 操作 | Aで次ページへ進むこと、SELECT＋STARTでFEのApps一覧に戻ることを確認 |
| 配置 | OPKと変更済みソースをSD1へ配置し、Macと本体のSHA-256一致を確認 |

OPK SHA-256: `1994cf7f8553743a28bf55e82f507868a8cd39347c0734d1a07aeb71c130a624`  
ソースアーカイブ SHA-256: `7f6e15843bbec1e0d4bfa25b77c4b9ef0cc1b0147f77225143e8f17752881bcc`

試験用PDFはSD1の `/media/user/Documents/plumos-pdf-test.pdf` に配置した。今回SDイメージ全体は再生成していない。ユーザーの本体目視確認と、一般的なPDFの互換性・大きな文書の性能は別の確認事項とする。

# RG280V WonderSwanのFE候補をPicoArchへ変更（2026-11-16）

ユーザーはWonderSwanのRA経路の廃止を指定し、PicoArchでは約50〜60 FPSで動作して遊べると報告した。従来のFE `systems.json` は `retroarch:mednafen_wswan` だけを候補にしていたが、実機には `mednafen_wswan_libretro.so` があり、PicoArchログには `GUNPEY.ws` と `Puzzle Bobble.ws` のロード・終了が記録されている。候補別のROMごとのFPS数値、音・入力の個別結果はこの時点では未取得。

FEのWonderSwan候補と既定を `picoarch:mednafen_wswan` のみに変更した。プロファイルのマージ処理にもWonderSwanを追加し、今後の更新でRAへ戻らないようにした。通常のPicoArchコア配置とSDイメージ作成に、固定リビジョン `16d96f64a32cbe1fa89c40b142298dbd007f2f4d` のWonderSwanコア、COPYING、ソースアーカイブを含めた。ROMとRA実行ファイルは削除しない。

同リビジョンから再ビルドしたMIPSコアのSHA-256 `5d7f9b340cb042be2b24cf17e0c82b24ef8640ae1471e5e3264a64015c952418` は実機の既存コアと一致。ソースアーカイブのSHA-256は `9cfa000048c01bfa5d39945a4034cde1b2fc032e589f66adcda66c610143815d`。実機に設定とライセンス・ソースをハッシュ照合して配置し、FEを再起動した。設定のSHA-256は `c8931be45b8760100ee8aead5ae048bca8b3225dc8dc2a2aa7b779795c3b66b7`。マージ前後の比較でWonderSwan以外の機種は不変。実機のFE選択画面はPicoArchの1候補だけを表示し、FEが稼働、SD2が読み取り専用であることを確認した。

シェル構文と対象コアの再ビルドは検証済み。SDイメージ全体は生成していない。更新後、ユーザーがFEから `Puzzle Bobble.ws` を起動し、映像・音・操作・SELECT＋STARTメニューからの終了とFE復帰をすべて正常、約50〜60 FPSと実機確認した。PicoArchログにも `mednafen_wswan_libretro.so` で同ROMをロードし、コアを終了した記録がある。確認後もFEプロセスは稼働している。

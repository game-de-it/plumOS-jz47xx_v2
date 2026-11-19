# JZ4770の4機種で共通SDを使う構成

対象はRG300X、RG350、RG280V、RG350M。RG300Xに続き、RG350Mを予備SD1で検証する。
現在のRG280VのSD1には試験用起動ファイルを書き込まない。

## 起動方式

OpenDinguxのLinux 6.8とUBIBootを維持する。4機種とも同じ
`ubiboot-rg350.bin`を使用することは、上流の
[odboot-client.cの機種表](https://github.com/OpenDingux/odbootd/blob/master/odboot-client.c)
と一致する。これはLinuxに渡る`hwvariant=rg350`の意味でもある。
RG280VをRG350と誤認識しているという意味ではない。

カーネル本体・rootfs・modules・ユーザー環境は共通にし、カーネル末尾に
連結するDTBを機種別にする。現行UBIBootに機種自動判別は追加しない。
**最初にMac上で起動対象を選ぶ**方式で、ユーザー環境を作り直さずSDを再利用する。
Linux起動後の設定は、実際に読み込まれたDTの`compatible`から選ぶ。
初回セットアップ画面からDTBを選ぶ方式では、画面初期化より遅いため解決できない。

試験SDの起動領域をMacへ接続した場合の切り替え例：

```sh
python3 scripts/select-jz47xx-boot-model.py --boot-volume <local-path> --model rg300x
```

このツールは起動領域内に同梱したモデル別ファイルのハッシュを照合し、
`uzImage.bin`を置き換える。初回の旧ファイルは`uzImage.previous.bin`に保存する。
切り替え後はカードを安全に取り出して、指定した機種に挿す。

| 機種 | DTB | カーネルのパネルモード | FEの縦方向倍率 |
| --- | --- | --- | --- |
| RG300X | rg300x | 640×480 | 1 |
| RG350 | rg350 | 320×240 | 1 |
| RG280V | rg280v | 320×480 | 2 |
| RG350M | rg350m | 640×480 | 1 |

モードは固定した上流カーネル`3181c26b25ab`のDTSとパネルドライバから確認。
RG300Xの`focaltech,gpt3`、RG350Mの`leadtek,ltk035c5444t`、
RG350の`frida,frd350h54004`に必要なパネルドライバは現行カーネルで有効。
RG300XとRG350MはDTSでHDMIブリッジのI²CをGPIO方式に切り替える。
RG350MではハードウェアI²CのままだとHDMIブリッジが認識されず、内蔵液晶の
DRM初期化も保留された。GPIO方式ではブリッジと内蔵液晶が初期化された。

## ユーザー環境の変更

- `plumos-jz47xx-device-env`は4機種のDTを識別し、機種名・縦倍率を設定する。
- FE・常駐ホットキー・ゲーム中の電源メニューは、固定の`event2`ではなく
  `gpio-keys`の入力ノードを使用する。
- FEのIngenic用設定・ABXY対応・OPK一覧は4機種で共有する。
- ロゴ描画は実フレームバッファの寸法に合わせる。
- RG280Vで確認したスリープ修正はカーネルに含まれるが、他機種の復帰動作は未確認。
  長押し電源OFF用DTプロパティも継承されるが、実機確認前に合格とはしない。

追加フロントエンドやエミュレータには、RG280Vの表示寸法を前提にした箇所が残る。
特にEmulationStationのScissor倍率は縦2倍が固定で、他機種用の調整が必要。
これらの動作保証は、FEが起動したという結果とは区別する。

## 試験用SD

`scripts/build-jz47xx-boot-in-container.sh`は4機種のDTBと連結カーネルを生成する。
`output/jz47xx-multimodel/boot/SHA256SUMS`にハッシュを記録する。
rootfsとmodulesは、ビルド後のSDK内にある別状態のファイルを混ぜず、
実機から取り出して照合した組を使う。

`scripts/make-jz47xx-test-image-in-container.sh rg350m`は
`output/jz47xx-multimodel/plumos-jz47xx-rg350m-test.img`とSHA-256ファイルを生成する。
ファイル名には引数の機種名を使う。SDカードへの書き込みは手動で行う。
構成はFAT32の起動領域128 MiB、ext4の
実行領域1536 MiB、FAT32のユーザー領域64 MiBと先頭予約領域。
カードの残り容量へはこの試験では拡張しない。
実機の完了済み環境を引き継ぐため、コピー先のseedマーカーを外し、
初回パーティション作成処理を再実行しない。ROMのSD2はコピー対象外。

このイメージは個人環境の検証用であり、配布用のクリーンビルドではない。
設定・保存データ・BIOS等を含み得るため、リリース成果物には使用しない。

## 検証状況（2026-11-19）

- 4機種のDTBビルドと`compatible`の検査に成功。
- 同じカーネルにRG280VのDTBを連結したものは、現用SD1の
  `uzImage.bin`とSHA-256が一致：
  `fd5359971c7e63399feaaddab3329fd74f35f2d1979f42292158b5a6e54190e8`。
- プロファイルのホスト試験で4機種の機種名・倍率を確認。入力番号を
  `event7`に変えた試験でも追従。不明なDTはエラーにする。
- FE・電源メニューの共通化コードはMIPS向けビルドに成功。
- RG300X選択の試験イメージ生成とext4検査に成功。
  SHA-256：`b2419091df92744a017efdb05ad5caface41177a49a035394ae4864bc0f57f5a`。
- 現用RG280Vで新しい検出ヘルパーが`rg280v`、`event2`、縦2倍を取得。
  ヘルパーは`/tmp`で実行し、現用SDの設定・起動ファイルは変更していない。
- RG300Xは実起動、640×480/60 Hz、FE表示、物理入力、テスト音を確認。
  音量・輝度ホットキーは入力注入で変更と復元を確認し、ユーザーが
  FEのSleepから電源キーで復帰できることを確認した。
  10秒以上の電源長押しによるOFFと通常起動、修正版FEの保持も確認した。
- RG300XのヘッダーにもIngenic用バッテリー処理を適用。機種名は動的に表示し、
  Wi-Fiは省略、RTC時刻が未設定の場合は時計を省略する。
- 復帰時のDRM polling警告、ゲーム経路、残る電源試験は継続対象。
  詳細は `validation/rg300x-first-boot-2026-11-19.md`。
- RG350の実機起動は未確認。RG350MでLinux起動、USB接続、640×480の内蔵液晶、
  FEの実機表示とDRMキャプチャを確認。音声・入力・電源操作・HDMI実出力は未確認。
- RG350Mの試験イメージを生成。イメージ内の`model.txt`、連結カーネル、
  rootfs・modules・mininitを生成元と照合し、パーティション表、ext4、SHA-256を検査した。

RG300Xでは、起動→DT/パネル/入力の取得→FE表示とABXY→音声とエミュ起動/復帰→
音量/輝度→電源メニュー→Reboot/Shutdown→Sleep/復帰の順に確認する。

# v0.1.0候補とアップデートの検証

## 4機種で起動確認した候補

| 成果物 | SHA-256 |
| --- | --- |
| `plumOS-JZ47xx-0.1.0.img` | `be91e3b6631ca515bdb3dfc0bf6c2eb69958432a7aaaff32833ce67209d79f4d` |
| 同じIMGを梱包した `plumOS-JZ47xx-v0.1.0-sd-image.7z` | `426d56e480768269a300b0a275a6d882332afcd0872dc25ce0cc6bb5e9e0238b` |

同じSD1でRG280V・RG300X・RG350・RG350Mを起動し、FEの表示とADB接続を確認した。初回セットアップはRG280Vで一度実行され、同じ拡張済みp3を残り3機種で使用した。7z展開後のIMGは元ファイルと同じSHA-256だった。

単体エミュレーターOPK 38本を展開し、既知のファームウェア234件と照合した。CrocoDSの単体版とPicoArch版は外部BIOS参照版に差し替えた。差し替え後、照合した範囲でメーカー製ファームウェアは検出されなかった。旧候補での結果は[候補の履歴](jz47xx-release-candidate-2026-11-20.md)に記録している。

## 更新機能入りの試験候補

`plumOS-JZ47xx-0.1.0-update-test.img` のSHA-256は `7651715b3e41cb1ef42bc8132c9898412b90d76abfc620a0270e928de588a731`。

ブートローダー、パーティション表、p1の起動ファイル、p3は4機種確認済み候補とバイト単位で一致した。p2には更新プログラム、公開鍵、表示修正を含むFE実行ファイルを追加・反映した。**カーネル起動後のFE起動手順には変更がある。** `S95frontend` に更新の適用と異常時の復旧を追加した。

RG350MにADBで試験用の実行ファイルと鍵を一時導入し、FEからの更新、再起動、更新後のFE描画、自動復旧を確認した。改ざんパッケージは拒否された。試験ファイルと既存設定のSHA-256は適用・復旧の前後で一致し、終了後に試験機を元の構成へ戻した。この試験は更新機能の動作確認で、以下のIMG起動確認とは別に実施した。

### RG350MでのIMG起動

更新機能入りIMGを試験用SD1に書き込み、RG350Mを←で起動した。FEの表示を実機で目視確認し、ADBで機種、機種選択の保存、初回セットアップの完了、p3のマウントとカード末尾までの拡張を確認した。

`S95frontend` は正常終了し、起動したFEのPIDと描画完了マーカーが一致した。FE、更新プログラム、署名検証プログラム、更新公開鍵、FE設定を含む11ファイルは、起動前にIMGから読み出したSHA-256と一致した。更新待ちの状態は空だった。このIMGの起動確認はRG350Mで実施した。

### 配布用アーカイブ

確認したIMGを同一バイト列のまま `plumOS-JZ47xx-v0.1.0-sd-image.7z` に梱包した。7zのSHA-256は `40c6158a97a7347683cb3706ba70ec86b8f4689885beae1f231162a8f2f6bf38`。展開後のIMGのSHA-256は上記の確認済みIMGと一致した。

## Temperを除外した候補

`plumOS-JZ47xx-0.1.0-no-temper-test.img` のSHA-256は `a93b84b53389bac4300d966e6a81f14f943a8cb922475a6b3192a9d559033821`。

更新機能入りの検証済みIMGを保管し、別のIMGからTemperのOPK、初期設定、FEとSimpleMenuの起動経路を除外した。PC Engineの既定はBeetle PCE Fastで、候補に残っていたTemperの選択設定をBeetle PCE Fastへ変更した。標準FEの登録は26システム・57起動経路。ブート領域、パーティション表、p3、更新処理の実行ファイルとFE起動スクリプトは旧候補と一致した。

RG350Mに新候補と一致する設定を一時適用し、標準FEからBeetle PCE FastでPC Engineのゲームを起動した。ステージ画面、音声デバイスのオープン、メニューのExitから同じFEプロセスへの復帰をADBで確認した。候補IMGと実機の対応ファイル9点のSHA-256が一致した。試験後、一時データを除去して元の設定に戻した。この試験ではSD1の再書き込みは行っていない。

### Temper除外版のRG350M起動確認

この候補IMGを試験用SD1に書き込み、RG350MでFEの表示を目視確認した。ADBでFEの描画完了、初回セットアップの完了、p3の拡張、TemperのOPKが存在しないこと、PC EngineがBeetle PCE Fastを参照することを確認した。更新プログラム、公開鍵、FE起動スクリプトを含む13ファイルは、元IMGから取得したSHA-256と一致した。FEの `System Update` メニューが表示され、署名なしの試験ファイルは検証プログラムに拒否された。正常な更新の適用と復旧は、同じ更新プログラムを使った前候補で確認している。

## Temper・fMSXを除外した候補

`plumOS-JZ47xx-0.1.0-no-fmsx-test.img` のSHA-256は `caf310d9a69b435c261d37be5f71892bd11904229bc7abcd893042996464a289`。

起動確認済みのTemper除外版から、fMSX本体、設定、ライセンス、標準FEとSimpleMenuの経路を外した。標準FEは26システム・56経路で、MSXはPicoArchのblueMSXを使用する。EmulationStationのMSX表示もblueMSXに合わせた。ブート領域、パーティション表、p3は元IMGとバイト単位で一致した。p2はファイルシステムの検査と、書き込み後の内容照合を行った。

RG350Mに候補と一致する設定を一時適用し、標準FEからblueMSXでMSX2のカートリッジゲームを起動した。同梱C-BIOSでゲーム画面まで進み、PicoArchのメニューからExitで同じFEプロセスに戻った。候補IMGと実機で、設定、コア、FE、更新プログラムなど9ファイルのSHA-256が一致した。終了後に試験データを除去し、元の設定とFE起動を確認した。この段階ではSD1に書き込まず、既存の起動環境で検証した。

Linux・Buildroot・UBIBoot・システムパッケージと、エミュレーター・アプリのソースを別々のアーカイブにまとめた。前者には候補のブートファイルおよびシステムバイナリの照合記録を、後者には候補内のバイナリのハッシュと対応ソースの確認状況を収録した。

PicoArchのソースは同梱バイナリとの対応を保つため、fMSX向けの入力割り当てだけを含む。fMSX本体とコア向けのパッチは含めていない。


### RG350Mでの候補IMG起動とblueMSX

候補IMGを書き込んだSD1でRG350Mを起動した。ADBで機種とv0.1.0、初回セットアップ完了、p3の拡張、FEの描画完了を確認した。FE、起動スクリプト、blueMSX、設定、更新プログラムなどの9ファイルと、対象OPK 6本はIMGの読み出し値とSHA-256が一致した。

本体のRAMに試験用ROMを一時配置し、IMGの標準FEのMSXからPicoArchのblueMSXを起動した。同梱C-BIOSで『ウシャス』の本編が表示され、音声出力デバイスが開いた。SELECT＋STARTのメニューからExitし、同じFEプロセスに戻った。スピーカーの聴感は未確認。試験ROMと一時マウントは終了後に除去した。

### 7件の対応ビルド照合

| 項目 | IMG内で照合したファイル | 固定リビジョン | 照合結果 |
| --- | --- | --- | --- |
| Handy | `handy.opk` 内の `plumos-emulator` | `6fc52aebdb65` | 保存済みビルドと一致 |
| Oswan | `oswan.opk` 内の `plumos-emulator` | `efea1326dc4f` | 保存済みビルドと一致 |
| SMS Plus GG | `smsplusgg.opk` 内の `plumos-emulator` | `5554715689a4` | 保存済みビルドと一致 |
| SMS Plus MS | `smsplusms.opk` 内の `plumos-emulator` | `5554715689a4` | 保存済みビルドと一致。GGと同じELF |
| UAE4All | `uae4all.opk` 内の `plumos-emulator` | `9988f9924a5d` | 保存済みビルドと一致 |
| GnGeo | `gngeo.opk` 内の `plumos-emulator` | `6fa682e06b60` | 保存済みビルドと一致 |
| 旧PCSX-ReARMed | `pcsx_rearmed_before_mmap_fix_libretro.so` | `d26eaee5c8fb` | 記録された時刻と同じ条件でパッチ適用前のソースを再ビルドし、SHA-256が一致 |

OPK 6本はいずれも標準FEから `plumos-emulator` を実行する。修正版のビルドを元のパッケージに追加した際に別名の旧実行ファイルも残っていた。旧ファイルは[移植元のOPKカタログ](https://github.com/RafaVico/RG350_APPREPOSITORY/blob/master/repository.nfo)の保存済みOPKから抽出したELFと全件一致した。GG/MSの旧ファイルは同一なので、対応ソースの版が未特定なのは旧ELF 5種類。現行の対応ソースをこれらの旧ELFに割り当てていない。候補IMGはSHA-256を再照合し、変更がないことを確認した。

## 未使用のOPKとlibretroコアを整理した候補

`plumOS-JZ47xx-0.1.0-route-cleanup-test.img` を、RG350Mで起動確認済みのfMSX除外版から別ファイルとして生成した。標準FEの26システム・56経路、SimpleMenu、350teric、EmulationStation、PyMenu、Appsの登録とランチャーを照合した。

未使用のOPK 14本とlibretroコア59本を除外した。旧PCSX-ReARMed試験用コアも対象に含む。無効化されたFBNeoの設定と、保存されたコア設定に参照があるMednafen NGPは保持した。Handy、Oswan、SMS Plus GG/MS、UAE4All、GnGeoのOPKは、対応ソースが未特定だった旧実行ファイルのみを外した。起動用の `plumos-emulator`、共有ライブラリ、デスクトップエントリー、その他のメンバーは再展開して照合し、内容・権限・所有情報が一致した。

ブート領域、パーティション表、p3は元IMGとバイト単位で一致した。p2はファイルシステムの検査と読み戻しを完了した。整理済みIMGの実機確認は次節に記録した。

### 整理版のRG350M実機確認

整理版を書き込んだSD1でRG350Mを起動し、ADBで機種、初回セットアップ完了、p3のカード末尾までの拡張、FE描画を確認した。FE本体、テキストUI、設定、起動スクリプト、対象OPK 6本の計10ファイルは、候補IMGの読み出し値とSHA-256が一致した。

| OPK | 起動確認に使った画面 |
| --- | --- |
| Handy | Basketbrawl のタイトル |
| Oswan | Puzzle Bobble のタイトル |
| SMS Plus GG | Puzlow Kids のタイトル |
| SMS Plus MS | Frontier Force の導入 |
| UAE4All | Baby Jo の言語選択 |
| GnGeo | Art of Fighting 2 起動時のNEO-GEO画面 |

各OPKは標準FEのROM一覧から起動し、SELECT＋STARTでエミュレーターのメニューを開き、ExitまたはQuitから終了した。6本とも終了コード0で、同じFEプロセスのROM一覧へ戻った。ROM・BIOS・試験設定はRAMに一時配置し、終了後に解除した。この試験の範囲は起動とメニューからの終了。FPSの計測やスピーカーの聴感確認は実施していない。

候補に含まれるエミュレーターOPK 23本を再展開して既知のファームウェア234件と照合し、一致はなかった。ReGBAにはライセンス原文を伴うオープンBIOSが入っている。

確認したIMGを `plumOS-JZ47xx-v0.1.0-sd-image.7z` に梱包した。7zの整合性検査に合格し、展開した `plumOS-JZ47xx-0.1.0.img` と元の候補IMGのSHA-256はともに `6d26505c8226c4e3cf6d81d03b173c8e4887db57bb4baace9a912d2a7a8b299b` だった。7zのSHA-256は `8ec7c9e018a37e8cefa5c301ddc0193aa77583add95c8c0011683f7dbaad8988`。

# 作業ログ

## 2026-11-15 — 試験用SDイメージの整理

- Macの容量確保のため、過去のbringup試作5本と対応するハッシュ、古いSD領域コピー4本を削除した。
- 現在書き込みに使う `plumos-rg280v-firstboot-seed.img`、起動済み構成へ戻すための `plumos-rg280v-adb-bringup.img`、SD領域の控え `rg280v-card-data-current.dmg` は保持した。
- `output` は約23GiBから12GiB、Macの空き容量は約68GiBから80GiBになった。ビルド用ファイルとログは変更していない。

## 2026-11-15 — 初回セットアップの設計見直し

- ユーザーの指摘で、RG280VにはV90S型の初回セットアップが未移植と確認した。前回の固定512MiB p3は初回セットアップではない。
- V90Sのseed生成、initramfsの領域検査・拡張・FAT新設・中断再開・完了印・ルート切替をソースから調べた。
- JZ47xx版の条件と実装順序を `docs/first-boot-design.ja.md` にまとめた。設計を先にコミットしてから実装する。
- 実装: 新しいp1/p2 seedのp2に `seed-v1` を置き、`plumos-first-boot` を追加。起動元、p1/p2の位置・ラベル、カード容量を検査してからp3を末尾まで作成する。再起動後、作成意図が記録され、p3が未フォーマットの場合にだけFAT32を作る。準備中・失敗時の大きな画面、FATとext4のログ、完了印を追加。印のない旧開発SDは変更しない。
- 検証: Buildrootを再設定して `mkfs.fat` を含め、rootfsとseedイメージを再ビルド。シェル構文、ビルド検証、p1/p2の領域表とp2の印・画面データの同梱を確認。4GiBの模擬MBRイメージに `sfdisk --append` でp1/p2を維持したままp3を作る試験が成功。
- 生成物: `output/plumos-rg280v-firstboot-seed.img`、SHA-256 `7988a97ea66527d82921dc98b080b3344823a35636949f7c1cdf799c32ec3f82`。
- 未確認: RG280Vでの初回起動、領域表変更後の自動再起動、p3のFAT初期化、p3の全容量、途中停止からの再開、画面表示。実機の確認前に完成版とは扱わない。
- 実機書き込み準備: 試験用SD1をMacの `disk5`（123729870848 bytes、内蔵SDXCリーダー、p1 `PLUMOSBOOT`、p2 Linux）として確認。イメージのSHA-256は上記と一致した。`diskutil unmountDisk` 後に管理者権限で先頭1.5GiBのバックアップを試みたが、macOSが raw SD の読み取りを `Operation not permitted` として拒否し、バックアップ・書き込みとも未実施。ユーザーが書き込み操作を引き継ぐ。書き込み先はこの試験用SD1、ファイルは上記seedイメージ。

## 2026-11-15 — RG280Vのユーザーデータ領域を分離

- 開始時点: RG280VでLinux 6.8、ADB、SD2の読み取り、状態画面の自動表示を実機確認済み。既存の試験イメージはSD1 p1 FAT + p2 ext4。
- V90S実機へSSH接続して確認した構成: 読み取り専用SquashFSルート、管理対象のext4、ROM・BIOS等のユーザー用FATを分離している。
- 今回の作業: RG280V新規イメージにSD1 p3 FATを追加し、起動時に任意マウントする。既存の2領域SDの起動を維持し、SD2は変更しない。
- 実装: p3を512MiBのFAT32 `PLUMOS` としてイメージへ同梱し、`roms`、`bios`、`apps`、`updates` を用意。`rcS` は起動元SDのp3だけを調べ、FAT種別とラベルが一致した場合に `/media/user` へマウントする。p3がなければ従来通り進む。SD2の処理は維持。
- 検証: Buildroot再ビルド成功。rootfs内に新しいマウント処理が含まれることを確認。ビルド検証スクリプト、シェル構文、`fsck.vfat -n` が成功。新規イメージのp1/p2/p3のセクタ内容照合とFAT内のディレクトリ確認が成功。
- 生成物: `output/plumos-rg280v-adb-bringup.img`、SHA-256 `d8d7b893b769c6acaa2370802a200789ad56a1ba7e82b15b74d604cb63d9f19d`。
- 未確認: 新規3領域イメージのRG280V実機起動とp3マウント。既存2領域SDでの起動実績は前回のもので、この変更後のrootfsでは再試験していない。

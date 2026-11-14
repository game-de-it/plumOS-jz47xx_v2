# JZ47xx版 plumOS の構成

## 起動とユーザー環境

UBIBoot、OpenDingux Linux 6.8、RG280V DTB、mininit の起動引き渡しを
ハードウェア基盤として使う。mininit が開く `rootfs.squashfs` 内では、
plumOS所有の `inittab`、`rcS`、`plumos-usb-ecm` がマウント、USB CDC、ADB、ログを管理する。
現段階は診断シェルを起動する。ADB接続はRG280Vで確認済みで、
次にフロントエンドを加える。
旧P2版とLinux 5.19は使わない。

現在の2パーティション版はRG280Vの起動・ADB検証専用で、最終SD構成ではない。
SD1 p2の `/media/data/local/init.d/S*` をADBで更新できる起動フックとして使う。
開発中のUSB ECMはMacのネットワーク設定との突き合わせのためMACを固定している。
他機種対応時には機種固有IDから安定したMACを生成する。
OpenDinguxのrootfs skeletonとアプリ実行ライブラリは暫定的なビルド素材として
残すが、OpenDinguxのinitスクリプトは実行しない。起動成立後にplumOSの
最小skeletonへ置き換える。

## V90Sから引き継ぐ領域の役割

| 領域 | JZ47xxでの役割 |
| --- | --- |
| 生セクタ | UBIBoot。通常のアプリ更新では変更しない。 |
| SD1 p1 FAT32 `PLUMBOOT` | カーネル・機種別DTB・起動引き渡し・将来のSystem A/B。UBIBootがFATから読むため、V90Sの独立したraw boot領域はここに統合する。 |
| SD1 p2 ext4 `PLUMOS_SYS` | 管理対象ランタイム、設定、ログ、更新状態。 |
| SD1 p3 FAT32 `PLUMOS` | Mac/Windowsから配置するROM、BIOS、アプリ、更新ファイル。初回起動時に未使用領域へ作成する。 |
| SD2 | 任意のROM・BIOS・メディア。存在しなくても起動し、自動フォーマットしない。 |

System A/Bの切替、p2拡張、p3作成は、RG280Vの基本起動とADB接続を実機確認してから
実装する。初回起動の処理には中断再開可能な状態記録を持たせ、既存パーティションを
勝手に初期化しない。4機種共通イメージは、起動前の機種別DTB選択が成立した後に作る。

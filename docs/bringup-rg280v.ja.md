# RG280V bring-up

## 実機で確認した現在地

Linux 6.8、mininit、plumOS `rcS` はRG280Vで起動し、SD1 p2のext4、
モジュール領域、診断シェルまで進む。2026-11-15に、データ通信できる
USBケーブルでMacからping、ADB connect、shell、pushを実機確認した。
Mac側は `en106` に `10.1.1.1/30`、端末側は `usb0` に `10.1.1.2/30`。
ADBが起動しなかった原因はloopback未設定で、`127.0.0.1/8` を設定して解決した。
SD2の16GB FATカードは読み取り専用でマウントし、`bios` と `roms` を確認した。
FBDEVへ描く開発用の大きな状態画面は再起動後の自動表示まで実機確認した。
状態画面の描画は起動ログの最後より後に行う。フロントエンドとUSB-DACは未検証。
生成するSDイメージにも状態画面の描画ツール、画面データ、起動サービスを
SD1 p2へ同梱する。新規イメージの書き込み後の実機起動は別途確認する。
新規イメージにはSD1 p3のFAT領域（`PLUMOS`、512MiB）も設ける。
正常にマウントされると `/media/user` に `roms`、`bios`、`apps`、`updates` が見える。
既存の2領域SDにはp3を追加せず、引き続き起動できる設計とする。

## 固定した基盤

- OpenDingux buildroot `98ce2f08d1ca54d8916b47f37ee866d1d0a0d4e0`。
- 上記の `od_gcw0_defconfig` が指定する OpenDingux Linux
  `3181c26b25abd135dc2d44ed71b72664ff89c0c8` (6.8)。
- OpenDingux の kernel defconfig と RG280V DTBを使う。USB AudioとUSB診断の
  ドライバのみfragmentで追加し、host役割を強制する設定は加えない。
- 起動用FAT領域に `/dev` と `/root` を作る。LinuxがFATをrootとして
  マウントした直後、devtmpfsとmininitがこれらのマウント先を使う。
- `configs/plumos_rg280v_defconfig` は不要なゲーム・メディア・Wi-Fiパッケージを
  除いた初期構成。現在はOpenDingux skeletonをビルド素材にしつつ、
  plumOSの `inittab` と `rcS` だけを起動する。ADB確立後にskeletonも置き換える。

## USBと開発ループ

Macとの接続はplumOSの初期化処理からCDC Ethernetを先に使う。RG280VのUSB
ポートがperipheralとして認識されれば、`usb0` を `10.1.1.2/30` にし、
`adbd` をTCP 5555で起動する。ホスト側は `10.1.1.1/30` に設定して
`adb connect 10.1.1.2:5555` を試す。ADBが失敗した場合は起動用FAT領域の
`plumos-boot.log` を読む。開発用構成のため、無線ネットワークは含めない。
MacではUSB Ethernetとして現れたインターフェースに `10.1.1.1/30` を設定する。
ADB接続後は `scripts/capture-rg280v.sh` で基本ログを保存できる。
`scripts/deploy-rg280v-status.sh` は大きな開発用状態画面をADBで配布する。
RG280VのFBDEVは320×480行として見え、物理画面では縦が半分に縮むため、
320×240のデザインを縦に2倍して描く。

アプリの反復は `/media/data/apps` または `/media/data/local` への転送、
対象プロセスの再起動で行う。カーネルとDTBはSDイメージの再生成が必要。
OPKは `scripts/deploy-rg280v-opk.sh path/to/app.opk` で転送できる。

## 実機での確認順序

1. UARTログが取得可能なら接続し、起動停止位置を記録する。
2. LCD、ボタン、バッテリー、内蔵音声、SD2、電源断を確認する。
3. USB CDC接続、Macからのping、ADB shell/pushを確認する。
4. 10回の冷間起動、長時間待機、アプリ起動・終了を確認する。
5. host側の配線・役割・VBUSを調べる。外部給電ハブでDACの列挙を試し、
   列挙が成立してから `snd-usb-audio` とALSAの経路を検証する。

RG280VのUSB host経路と給電能力は未確認。共通DTSのID GPIOは
信頼性上の理由で無効化されているため、試験なしに有効化しない。

## 共通イメージへの移行

RG280V単体の起動が安定した後、4機種のカーネル+DTBを同じFAT起動領域に
置き、起動前の機種選択を追加する。初回のみの機種選択を許容する。
同じ物理SDを差し替える際の自動判別は、起動前に使える識別信号を
実機で確かめられた場合に追加する。

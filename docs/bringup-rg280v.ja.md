# RG280V bring-up

> 開発初期の設計・検証記録です。現在の共通イメージは[開発者ガイド](developer/README.ja.md)を参照してください。

## 起動画面と起動時間（2026-11-16）

初回セットアップ画面が毎回表示された原因は、SD1上の `rootfs.squashfs` が
完了判定を入れる前の版のままだったこと。現在の `plumos-first-boot` は
`provision/complete`、`/media/user/.plumos-ready`、p3のマウントを確認し、
完了済みなら画面を描く前に終了する。実機でrootfsを更新した後、再起動しても
`first-boot.log` は70行のまま増えなかった。新規SDの初回セットアップ経路は
この変更後の実機では未確認。

起動直後のLinuxマスコットとコンソール文字は、カーネルの `CONFIG_LOGO` と
`CONFIG_FRAMEBUFFER_CONSOLE` を無効化して消した。シリアルコンソールは残す。
データ領域のマウント直後に、V90S/A30/MF共通の正規原画
`board/rg280v/assets/bootlogo.bmp` をFBDEVの320×480へ表示する。
初回セットアップ中は専用画面がこのロゴを置き換え、FE起動時に消す。
ADB READY画面とその自動起動サービスは廃止した。

起動ログの実測では、SD2の `blkid` が乱数初期化を待って約8.6秒停止していた。
ファイル形式を指定して直接マウントし、FATとext4を順に試す方式に変更した。
また、FE起動サービスは、正常なUTF-8マウントでも表示される
`iocharset=iso8859-1` を誤判定し、毎回約2.6秒のROM全件走査を実施していた。
マウントし直す処理を除き、TOPのキャッシュがない初回だけ全件走査する。
以降、ROM一覧は既定の「入ったときに走査」で更新でき、TOP全体は設定の
「Refresh TOP」で再走査できる。

| 起動ログの位置 | 変更前 | SD2修正後 | FE走査修正後 |
| --- | ---: | ---: | ---: |
| SD2マウント完了 | 12.30秒 | 3.81秒 | 3.80秒 |
| FE起動サービス完了 | 16.12秒 | 7.14秒 | 4.45秒 |
| rcS完了 | 16.30秒 | 7.35秒 | 4.78秒 |

これはカーネル起動からの `dmesg` 時刻。FEの物理画面の表示完了時刻ではない。
SD2のFAT読み取り専用マウントとFEプロセスの起動は再起動後に確認した。
共通ロゴとコンソール無効化を反映した実機では `rcS` 完了が4.08秒で、
`vtcon1` は作られず、フレームバッファコンソールへの切替ログも消えた。
その状態ではFBDEVのメモリにロゴを書くだけでは表示モードが有効にならず、
ロゴが見えなかった。`rg280v-fbshow` が現在のモードを強制的に有効化してから
描くようにし、正規ロゴの表示を実機で確認した。最終版の `rcS` 完了は4.40秒。

## 実機で確認した現在地

Linux 6.8、mininit、plumOS `rcS` はRG280Vで起動し、SD1 p2のext4、
モジュール領域、診断シェルまで進む。2026-11-15に、データ通信できる
USBケーブルでMacからping、ADB connect、shell、pushを実機確認した。
ホスト側のUSB Ethernetと端末側の `usb0` に対向するアドレスを設定した。
ADBが起動しなかった原因はloopback未設定で、`127.0.0.1/8` を設定して解決した。
SD2の16GB FATカードは読み取り専用でマウントし、`bios` と `roms` を確認した。
FBDEVへ描く開発用の大きな状態画面は再起動後の自動表示まで実機確認した。
状態画面の描画は起動ログの最後より後に行う。フロントエンドとUSB-DACは未検証。
生成するSDイメージにも状態画面の描画ツール、画面データ、起動サービスを
SD1 p2へ同梱する。2026-11-15に初回セットアップ用seedを実機で起動した。
固定512MiBのp3を持つ旧3領域試験イメージは初回セットアップに非対応。
新しいseedイメージはp1/p2だけを持ち、p2の `seed-v1` 印で初回セットアップを
開始する。p3をカードの残りに作成し、再起動後にFAT32 `PLUMOS` として
初期化する。実機では約113.7GiBのp3が `/media/user` にRWマウントされ、
`roms`、`bios`、`apps`、`updates` と完了印を確認した。再起動後も維持される。
印のない既存の2領域SDは変更しない。

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
ポートがperipheralとして認識されれば、端末側の `usb0` にアドレスを設定し、
`adbd` をTCP 5555で起動する。ホスト側のUSB Ethernetに対向アドレスを設定して
`adb connect "$DEVICE_USB_IP:5555"` を試す。ADBが失敗した場合は起動用FAT領域の
`plumos-boot.log` を読む。開発用構成ではUSB Ethernetを使用する。
ADB接続後は `scripts/capture-rg280v.sh` で基本ログを保存できる。
`scripts/deploy-rg280v-status.sh` は起動ロゴと描画ツールをADBで配布する。
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

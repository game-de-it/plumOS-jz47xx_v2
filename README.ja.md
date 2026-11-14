# plumOS jz47xx v2

RG280Vから着手する、OpenDinguxベースのplumOSです。現在は実機検証前の
bring-up構成です。SDカードに書き込める成果物を作るまではリリースしません。

## 現在の目標

1. RG280VでOpenDinguxのカーネル・DTB・最小ユーザー環境を起動する。
2. USB CDC Ethernet経由のADBとSSHで、イメージを作り直さずに試験する。
3. 画面、入力、内蔵音声、電源操作、SDの安定性を確認する。
4. USB hostとUSB-DACの成立条件を実機で調べる。

旧P2版およびLinux 5.19はベースにしません。出発点は
[OpenDingux buildroot](https://github.com/OpenDingux/buildroot) の
`opendingux` ブランチを固定したコミットです。カーネルもそのコミットが指定する
OpenDingux Linux 6.8を使い、実機で評価します。

設計と検証手順は [docs/bringup-rg280v.ja.md](docs/bringup-rg280v.ja.md) を参照。

## ビルド

Dockerが起動しているMacで `./scripts/build-rg280v.sh` を実行します。
ビルド成果物が揃ったら `./scripts/make-rg280v-image.sh` でRG280V用の
bring-up SDイメージを作ります。イメージとSHA256は `output/` に出力されます。
Buildrootの作業ディレクトリは、大文字と小文字を区別するDocker volume
`plumos-jz47xx-rg280v-build` に置きます。`work/` と `output/` は生成物です。
defconfigを変更した場合は、ビルド前に `./scripts/configure-rg280v.sh` を実行します。

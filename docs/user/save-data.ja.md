# セーブ・ステートの保存先

[English](save-data.md) · [ユーザーガイド](README.ja.md) · [SDカード構成](storage.ja.md)

標準フロントエンドから起動したエミュレーターのセーブとステートは、通常、SD1の **p2 `PLUMOSDATA`** にあります。ROMをSD2から起動した場合も、以下の保存先はSD1です。表のパスは本体上のパスです。SD1をカードリーダーでLinuxのPCに接続してp2を開く場合は、パーティション内の `plumos/` からたどります。

## PicoArch

| 種類 | 保存先 |
| --- | --- |
| ゲーム内で保存したデータ（セーブRAM） | `/media/data/plumos/Saves/<システムID>/<ゲーム名>.sav` |
| セーブステート | `/media/data/plumos/home/picoarch/<システムID>/.picoarch-<コア名>-<システムID>/<ゲーム名>.st0` など。末尾の数字はスロット番号。 |

たとえばGBのPicoArch Gambatteでは、セーブRAMは `Saves/gb/`、ステートは `home/picoarch/gb/.picoarch-gambatte-gb/` に保存されます。[システムIDとコア名](supported-systems.ja.md)

## 単体エミュレーター

FCEUX、Gambatte、PocketSNES、ReGBA、PicoDrive、PCSX4ALLは `/media/data/plumos/home/` を使います。独立したOPK経路のホームは `/media/data/plumos/home/opk/<エミュレーターID>/` です。たとえばFCEUX 2.2.3のIDは `fceux223` です。セーブを探すときは、FEの **SELECT** メニューで使用した起動経路を確認してください。

| 起動経路 | 主な保存先（`/media/data/plumos/` からの相対パス） |
| --- | --- |
| PCSX4ALL | メモリーカードは `home/.pcsx4all/memcards/`、ステートは `home/.pcsx4all/sstates/`。 |
| FCEUX | `home/.fceux/` の下の `sav/` に通常セーブ、`fcs/` にステート。 |
| FCEUX 2.2.3 | `home/opk/fceux223/.fceux/` の下の `sav/` に通常セーブ、`fcs/` にステート。 |
| Gambatte | `home/.gambatte/saves/`。Gambatte 2020は `home/opk/gambatte2020/.gambatte/saves/`。 |
| PocketSNES | `home/.pocketsnes/`。 |
| ReGBA | `home/.gpsp/`。 |
| PicoDrive | `home/.picodrive/`。たとえばSRAMはその下の `srm/`。 |
| PokeMini | `home/opk/pokemini/saves/`。EEPROMは `.eep`、ステートは `.sta`。 |
| その他の単体OPK | `home/opk/<エミュレーターID>/` の配下。フォルダー名と形式はエミュレーターごとに異なります。 |

## 設定と履歴の保存先

`/media/data/plumos/` 配下の `config/frontend/settings.json` にFE設定、`config/system/settings.json` にシステム設定があります。エミュレーターごとの設定や代替FEの設定は `home/`、標準FEのお気に入りや履歴は `state/frontend/` にあります。関連データをまとめて残す場合はSD1全体をバックアップしてください。

## バックアップと復元

1. エミュレーターをメニューの **Exit** または **Quit** で終了し、FEの電源メニューで **Shutdown** を選びます。
2. SD1全体をイメージとして読み出すと、セーブ・ステート・設定をまとめて保管できます。個別に保存する場合は、LinuxでSD1のext4パーティション `PLUMOSDATA` を開き、上記のフォルダーから必要なファイルをコピーします。
3. 個別のファイルを復元するときは、同じシステムと起動経路を使い、ファイル名と階層を保って対応する保存先へ戻します。ステートは同じエミュレーターまたはコアの同じ版での復元を推奨します。

ゲームやサムネイルをSD2に置いている場合は、そのカードも別途バックアップします。

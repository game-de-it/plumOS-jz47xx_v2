# RG280V FE全機種の試験用ROM配置（2026-11-16）

ユーザーの意図は、全ROMの移動ではなく、FEに登録された各機種を実機で検証できるよう機種ごとに約4本のROMを用意することだった。SD2のFEライブラリ件数を調べ、不足していた32X、Sega CD、SuperGrafx、PC Engine CD、WonderSwanを補った。前段で32Xに置いた32本は、元の転送記録とSD2上のSHA-256を照合してから4本へ整理した。ユーザーの元ライブラリは変更していない。

| FE機種 | 再スキャン後のROM件数 |
| --- | ---: |
| NES | 120 |
| SFC | 115 |
| GB | 52 |
| GBC | 11 |
| GBA | 20 |
| Mega Drive | 163 |
| Master System | 6 |
| Game Gear | 20 |
| 32X | 4 |
| Sega CD | 2 |
| PC Engine | 50 |
| SuperGrafx | 4 |
| PC Engine CD | 4 |
| Neo Geo Pocket Color | 27 |
| WonderSwan | 4 |
| FBNeo | 18 |
| MSX | 108 |

Sega CDは提供されたライブラリで利用できる2本を配置した。1本はFatal Fury Specialのデモ版、もう1本はNight Striker。PC Engine CDは4本をCHD化した。両CD機種に必要なBIOSも端末の`plumos/bios`へ配置した。CHDは作成後に`chdman verify`を通過。転送した13本のROMと4本のBIOSはSD2または端末上でSHA-256を照合し、ROMはFE再スキャンの登録名とも照合した。個別ハッシュはGit管理外の`output/rg280v-emulators/fe-rom-samples-20261116.json`に保存した。ROMとBIOSはGitに含めない。

作業後のSD2は読み取り専用マウントで、FEプロセス`plumos-controller-ui --render`の稼働を確認した。全17機種がROMを持つことまで検証済み。追加ROMの映像・色・音・FPS・入力・終了後のFE復帰は、これから実機で確認する。

追記：PSXは当時のFE登録に含まれていなかった。後続作業でPSXを登録し、試験用ROM4件とアイコンを追加した。起動試験のクラッシュは登録除外の理由にしない。詳細は`rg280v-psx-fe-registration-2026-11-16.md`を参照。

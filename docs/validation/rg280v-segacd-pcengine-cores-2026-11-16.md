# RG280V Sega CD・PCエンジンの実機確認（2026-11-16）

ユーザーがFE登録順で実機確認した。Sega CD全体の感触は約50〜60 FPSで「ぎりぎり遊べる」。その後、Sega CDのGenesis Plus GXには性能上の問題があるためFE候補から外すよう指定された。候補別の正確なFPS値やROM名は未取得のため、50〜60 FPSを特定のコアの測定値とは扱わない。PicoDriveはSega CDの唯一のFE候補として残す。

PCエンジンは登録されたPCE FastとSuperGrafxの両コアをユーザーが合格と報告した。候補別のFPS値やROM名、映像・音・入力・FE復帰の内訳は未取得。FE設定は変更せず、既定のPCE Fastも維持する。

RG280VのSega CD設定では `launch_profiles` を `picoarch:picodrive` のみにし、既定も同じ値へ変更した。実機に残っていた `picoarch:genesis_plus_gx` のSega CD機種別選択履歴をクリアし、実機の `plumos-text-ui core system segacd` でPicoDriveのみ表示されることを確認。設定ファイルのSHA-256は `787cfb56f864433e35e5077317e7ba141adcc367f599286761774ab26d47db7f`。FE再起動後は `plumos-controller-ui` が稼働し、SD2は読み取り専用。Mega Drive・Master System・Game Gear側のGenesis Plus GX候補は変更していない。次の登録順はSuperGrafx。

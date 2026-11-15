# RG280V ChimeraSNESのFrameskip既定値（2026-11-16）

FEのSFC候補を登録順に確認中。標準Snes9xはF-Zeroで約30 FPS、同期待ちを除いても約47 FPS相当だったため、ユーザーの指示でFE候補から削除した。残る候補の順序はPocketSNES、Snes9x 2005、ChimeraSNES、Mednafen Supafaust、Snes9x 2002、Snes9x 2005 Plus、Snes9x 2010。SFCの既定PocketSNESは変えていない。

ChimeraSNESはユーザーがFrameskipをOFFにすると正常に動くと報告。コアの `libretro_core_options.h` ではFrameskipの既定が`auto`で、音声バッファの通知に応じて映像を省く。`scripts/patch-rg280v-chimerasnes.py` で既定を`disabled`に変更し、`scripts/build-rg280v-picoarch-cores.sh`から再現できるようにした。上流のMakefileはヘッダー変更を依存関係として追跡しないため、パッチ適用時に`libretro.o`を削除して再コンパイルさせる。最初のビルドは旧バイナリと同じSHA-256になったため採用せず、再コンパイル後の異なるバイナリを配置した。

- 旧コアSHA-256: `3f5fb6dfa743770723be5d2a7e9471d01266c7ea280157d6a8289418269051fa`
- 修正版コアSHA-256: `49f429cc329177e88592a580d475e25dc459c4738196b830310d40c4ab8eab9b`
- 更新後のFE定義SHA-256: `ce9671e5ed4763d742dff78ef5a21853706ae1cdb8792b3b07f57f68925b85fe`

旧コアと旧FE定義は端末内`/media/data/plumos/backups/`へ保存。修正版を一時ファイルへ転送してハッシュ照合後に置換し、ライブラリを再走査してFEを起動した。端末から読み戻したFE定義で、標準Snes9xが候補からなくなり順序が上記の通りであることを確認した。ユーザーが修正版をFEから手動設定なしで起動し、約60 FPS、映像・音・操作・SELECT＋STARTメニューからFE復帰まで正常と確認した。

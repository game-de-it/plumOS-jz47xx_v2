# RG280V Mednafen Supafaust確認（2026-11-16）

SFCのFE登録順でChimeraSNESの次。対象ROMはSD2の`Super Mario World - Super Mario Bros. 4.sfc`。CPUは従来の996 MHz設定。診断起動ではFEを停止し、12秒のwatchdogでPicoArchを終了してからFEを復帰した。

既存コアは起動直後にsignal 6で終了し、ログに`Mednafen::MDFN_Error`が残った。上流`libretro.cpp`のエミュレーションスレッド固定先は既定で`0x2`（CPU 1）だが、RG280Vの`/proc/cpuinfo`にあるCPUは0だけ。`scripts/patch-rg280v-supafaust.py`で既定を`0x0`（固定なし）へ変更し、ビルドスクリプトから毎回適用するようにした。修正版はwatchdog終了まで動き、signal 6は出なかった。したがって固定先がクラッシュの原因である可能性が高い。

同じROMで、PPU描画方式を比較した。上流の設定説明は単一CPUなら単一スレッド描画を推奨する。CPU固定なしの複数スレッド版は最後の診断窓で35.75 FPS、単一スレッド版は35.63 FPS。変更による改善はなく、60 FPS未達。取得した画面はNintendo Presentsの初期表示で、ゲーム中の映像・音・入力品質はこの自動試験では判定できない。音声の非ゼロ信号はあるが、無音率は初期画面のため品質判定に使わない。

- 旧コアSHA-256: `cf82a26c853a9e7c42939ea887f338ed7f4808b0aad234f30046b9ab7adaa723`
- CPU固定なし版SHA-256: `3e148f91bdd0d125039f8b0541b802c2284340dd2a301f4cdf84a5c4d52210da`
- 単一スレッド版SHA-256: `752b770c202d2568f359e83a86e146d1a62a9019a3f2a350764365675b1ad985`

端末内に旧コアと比較版、旧FE選択状態のバックアップを保存。単一スレッド版を照合して配置し、FEのSFC選択をMednafen Supafaustに変更してFE再起動を確認した。実機操作での確認は保留中。

## 物理画面と30 FPSの内訳

ユーザーがFEからSuper Mario Worldを起動して、HUDが約`30 (30)`で固定されると報告。括弧内はPicoArchの主ループ回数なので、映像のみを間引くFrameskipではない。ゲーム中に読み取ったプロセスのCPU時間は3.07秒で187 ticks（この環境の100 ticks/秒では約61%）、周波数は996 MHz。

ユーザーがメニューからFEへ戻った後、同じ単一スレッド版でSD2の`F-Zero.sfc`を20秒診断起動した。最後の窓は30.0 FPS、`SDL_Flip`待ちの平均は13.025 ms/回。1フレーム33.3 msのうち画面待ち以外に約20.3 ms掛かる。60 Hzの16.7 ms以内に処理できず、次の垂直同期まで待つため30 FPSに揃う。自動試験はwatchdogで終了し、FEプロセスを復帰した。CPU固定なしと単一スレッド化ではこの不足を解消できなかった。

初期画面を含む自動試験とユーザーのプレイ中の観察は別条件。F-Zeroの音声信号は非ゼロだったが、音質・操作感の実機判定は未取得。Supafaustは現状60 FPSを満たさない候補として扱い、次のFE登録順はSnes9x 2002。

FEのSFC選択をSnes9x 2002へ進め、端末側PicoArchがFrameskip既定値Disabled版（SHA-256 `97e1688f539829a3f449bdb760b3f6fb5b3319ee66f142e45dbba8055bd670c4`）であることを確認した。FEは再起動済み。Snes9x 2002の物理確認結果は別途記録する。

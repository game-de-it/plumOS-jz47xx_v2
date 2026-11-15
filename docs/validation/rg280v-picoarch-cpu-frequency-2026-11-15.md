# RG280V PicoArch CPU周波数比較（2026-11-15）

低FPSコアについて同じROMと試験条件でCPU周波数を比較する予定だった。実機の`scaling_available_frequencies`は444000、492000、600000、696000、792000、900000、996000、1092000、1200000 kHz、governorは`userspace`、切替前の`scaling_cur_freq`は996000 kHzだった。[LinuxカーネルのCPUFreq文書](https://www.kernel.org/doc/html/latest/admin-guide/pm/cpufreq.html)によると、`userspace` governorでは`scaling_setspeed`へ希望周波数を書いて切り替える。

まず1092000 kHzを短時間試し、8秒後に996000 kHzへ戻すコマンドをADBで実行した。しかし周波数変更直後にADBがofflineとなり、10.1.1.2へのpingも応答しなかった。MacのUSB Ethernetインターフェース自体はactiveのままだった。コマンド後の周波数は読み取れず、戻し処理が実行されたかどうかも確認できなかった。前回も1200000 kHzへの変更直後に画面とADBが停止し、ユーザーが本体をリセットしていた。

そのため今回、低FPSコアの1092000/1200000 kHz計測は実施できていない。996000 kHzを超える設定を安定周波数と扱わない。実機復帰後に現在周波数とFE起動を確認する。基準の996000 kHz結果は[同日の起動試験](rg280v-picoarch-smoke-2026-11-15.md)を参照。なお、その計測FPSは画面更新回数であり、ゲーム速度や音程を直接示さない。

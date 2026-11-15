#!/usr/bin/env python3
"""Create a compact, Git-trackable summary of the RG280V core smoke run."""

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "output/validation/rg280v-picoarch-20261115"
DEST = ROOT / "docs/validation"
DEST.mkdir(parents=True, exist_ok=True)

plan = {item["core"]: item for item in json.loads((DATA / "plan.json").read_text())}
results = {}
for line in (DATA / "smoke/results.jsonl").read_text().splitlines():
    result = json.loads(line)
    if result["core"] in results:
        raise ValueError(f"duplicate result: {result['core']}")
    results[result["core"]] = result


def fmt(value):
    return "—" if value is None else f"{value:.1f}"


def outcome(result):
    if result is None:
        return "ROMなし"
    output = result["runner_output"]
    if "signal=" in output:
        return "異常終了"
    if "exit=" in output:
        return "起動直後終了"
    captures = result["captures"]
    if not captures:
        return "画像なし"
    if all(c["unique_colors"] == 1 for c in captures):
        return "全黒"
    return "描画あり"


def pcm(result):
    if result is None or result["last_audio_zero_fraction"] is None:
        return "未取得"
    zero = result["last_audio_zero_fraction"]
    if zero >= 0.995:
        return "PCM無音"
    if zero >= 0.9:
        return "PCMほぼ無音"
    return "PCM信号あり"


def notes(core, result):
    values = []
    if core in ("fceumm", "quicknes", "nestopia"):
        values.append("FCEUX参照画像とNES枠色が不一致")
    if core == "mednafen_pce":
        values.append("同じROMのPCE Fastは描画あり")
    if core == "chimerasnes":
        values.append("同じROMのSnes9x 2002/2005は描画あり")
    if core == "fake08":
        values.append("同じCelesteのRetro8は60 FPS")
    if core in ("gpsp", "mgba", "mednafen_gba", "meteor", "vba_next", "vbam"):
        values.append("言語選択で待機、プレイ未確認")
    if result is not None and result["last_fps_window"] is not None:
        if result["last_fps_window"] < 45:
            values.append("45 FPS未満（公称fpsとは未照合）")
    if core == "vemulator":
        values.append("対応するVMUファイルなし")
    return "; ".join(values)


rows = []
for core in sorted(plan):
    result = results.get(core)
    item = plan[core]
    if result is None and item["status"] == "planned":
        raise ValueError(f"missing run: {core}")
    captures = [] if result is None else result["captures"]
    hashes = []
    for capture in captures:
        image = ROOT / capture["file"]
        hashes.append(hashlib.sha256(image.read_bytes()).hexdigest()[:16]
                      if image.exists() else "missing")
    rows.append({
        "core": core,
        "system": result["system"] if result else ",".join(item["systems"]),
        "source": ("rom2-bundle" if result and result["source"] == "staged"
                   else result["source"] if result else "—"),
        "rom": result["rom_name"] if result else "—",
        "result": outcome(result),
        "fps_window": fmt(result["last_fps_window"]) if result else "—",
        "audio": pcm(result),
        "audio_zero_fraction": (fmt(result["last_audio_zero_fraction"] * 100)
                                if result and result["last_audio_zero_fraction"] is not None
                                else "—"),
        "colors_2nd_capture": str(captures[-1]["unique_colors"]) if captures else "—",
        "capture_sha256_prefixes": ",".join(hashes),
        "process": (result["runner_output"].splitlines()[0] if result else "—"),
        "note": notes(core, result),
    })

csv_path = DEST / "rg280v-picoarch-smoke-2026-11-15.csv"
with csv_path.open("w", newline="") as output:
    writer = csv.DictWriter(output, fieldnames=rows[0].keys(), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)

from collections import Counter

counts = Counter(row["result"] for row in rows)
report = [
    "# RG280V PicoArch コア起動試験（2026-11-15）",
    "",
    "## 条件と判定の限界",
    "",
    "- RG280V実機、996 MHz、SD1の74コアを使用。SD2とROM2からシステム・拡張子を照合したROMを選定。ROM2のディスク・ZIPは一時的にSD1へ転送し、試験後に削除した。",
    "- 基本は各11秒、追加バンドルは12秒起動。約3.5秒と7秒でDRM画面を取得し、SDL_Flipの時間と48 kHz PCMコールバックのゼロ標本率を記録した。制限時間での `watchdog: timeout` は正常な試験終了。",
    "- `FPS` は最後の計測窓の画面更新回数で、ゲーム固有の目標FPSとは照合していない。起動画面だけのコアや静止画でも更新される。",
    "- `PCM信号あり` は波形の非ゼロ標本を示すだけで、BGMの音程・速度・音量・歪みの正常性は証明しない。`PCM無音` もロゴやタイトル画面の無音区間を含み得る。",
    "- `描画あり` は色数1を超える画像が取得できた意味で、正しい色とは限らない。参照画像と直接比較できたのはNESのBaseballだけ。ゲーム開始、入力、メニュー、長時間安定性はこの試験の対象外。",
    "- BIOSは一括転送していない。BIOS、親ROM、ディスク付属ファイルが要るコアの失敗は、コア本体の欠陥と断定できない。",
    "",
    "## 集計",
    "",
    f"- コアAPI読込: 74/74。ROM起動試験: {len(results)}/74。対応データなし: {74-len(results)}。",
    "- 起動試験の画面結果: " + ", ".join(f"{name} {count}" for name, count in counts.items()) + "。",
    "- NES（FCEUmm、QuickNES、Nestopia）は同一のBaseballで19.8、29.6、19.8 FPS。3者とも枠色が既存FCEUX参照画像と異なる。過去の実機試験でもPicoArch NESの色と音の遅れが報告済み。",
    "- PCE Fast / Blazing Lazers は60.0 FPS、PCM非ゼロ。SFCはSnes9x 2002/2005系が概ね60 FPS、標準Snes9xは31.1 FPS、2010は19.5 FPS。",
    "- 同じBlazing LazersでPCE Fastは描画あり、通常のPCEは全黒。CelesteではRetro8が60.0 FPS、Fake-08が23.4 FPS。これらは同じROMで比較可能な差。",
    "- GBAの6コアは少なくとも1枚の画面中央に小さな言語選択表示が出た。自動画像判定の初期値では全黒と誤判定していたため、報告では描画ありに修正した。ここで音声が無いことは不具合確定ではない。",
    "- FEは試験後に手動で再起動し、プロセス稼働を確認。試験後のSD1空き容量は約638 MiB。",
    "",
    "## コア別結果",
    "",
    "| コア | 機種 | ROM | 画面 | FPS | 音声 | 終了 | 注記 |",
    "| --- | --- | --- | --- | ---: | --- | --- | --- |",
]
for row in rows:
    rom = row["rom"].replace("|", "\\|")
    if len(rom) > 35:
        rom = rom[:32] + "..."
    process = row["process"].removeprefix("watchdog: ")
    report.append("| " + " | ".join([
        row["core"], row["system"] or "—", rom, row["result"],
        row["fps_window"], row["audio"], process, row["note"],
    ]) + " |")
report.extend([
    "",
    "数値、ROM名、PCMゼロ率、画面ハッシュは同名のCSVに記録。実画像と詳細ログはローカルの `output/validation/rg280v-picoarch-20261115/smoke/` に保存している（GitにはROM画像を含めない）。",
    "",
    "## 次回の切り分け対象",
    "",
    "1. NESの色と約20〜30 FPS、および実機で報告済みの音の遅さ。FCEUX参照画像とのパレット比較から開始。",
    "2. `異常終了` と `起動直後終了` をBIOS・ROM構成不足と実装問題に分離。特にCrocods、Dinothawr、NP2kai、TyrQuake、PCSX-ReARMed。",
    "3. 全黒または低FPSのコアは、対応BIOSを揃えた後に実プレイまで進めて再計測。",
    "4. FE復帰の自動処理が3回失敗した。試験ランナーの遅延再試行を追加したので、次の実機試験で検証する。",
])
md_path = DEST / "rg280v-picoarch-smoke-2026-11-15.md"
md_path.write_text("\n".join(report) + "\n")
print("wrote", csv_path, md_path)

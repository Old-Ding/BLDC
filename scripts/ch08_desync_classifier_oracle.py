"""离线检查第 08 章同步/失步判据。"""

from __future__ import annotations

import csv
from pathlib import Path


LOCKED_REFERENCE = {
    "scenario": "signal_locked_reference",
    "source": "signal_fixture",
    "role": "sync_positive",
    "speed_ratio": 0.98,
    "phase_slip_cycles": 0.04,
    "negative_torque_fraction": 0.06,
}


def classify(speed_ratio: float, slip_cycles: float, negative_torque_fraction: float) -> str:
    # 同步/失步由速度跟随和累计滑移决定；负转矩占比只描述转矩脉动，不单独否决同步。
    del negative_torque_fraction
    if speed_ratio >= 0.85 and slip_cycles <= 0.25:
        return "SYNC_FOLLOW_CONFIRMED"
    if speed_ratio <= 0.20 and slip_cycles >= 2.0:
        return "DESYNC_CONFIRMED"
    return "INDETERMINATE"


def expected_classification(row: dict[str, object]) -> str:
    role = str(row.get("role", ""))
    scenario = str(row.get("scenario", ""))
    if role == "sync_positive" or scenario in {"sync_follow", "signal_locked_reference"}:
        return "SYNC_FOLLOW_CONFIRMED"
    if role.endswith("_desync") or scenario in {"gentle_ramp", "overfast_ramp", "load_step"}:
        return "DESYNC_CONFIRMED"
    return "INDETERMINATE"


def annotate_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    for row in rows:
        classification = classify(
            float(row["speed_ratio"]),
            float(row["phase_slip_cycles"]),
            float(row["negative_torque_fraction"]),
        )
        expected = expected_classification(row)
        row["expected_classification"] = expected
        row["classification"] = classification
        row["result"] = "PASS" if classification == expected else "FAIL"
    return rows


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    wave = root / "waveforms" / "08-open-loop-desync"
    summary = wave / "plecs_desync_summary.csv"
    rows: list[dict[str, object]] = []

    with summary.open("r", encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            speed_ratio = float(row["speed_ratio"])
            slip_cycles = float(row["phase_slip_cycles"])
            negative = float(row["negative_torque_fraction"])
            rows.append({
                "scenario": row["scenario"],
                "source": "plecs_csv",
                "role": row.get("role", ""),
                "speed_ratio": speed_ratio,
                "phase_slip_cycles": slip_cycles,
                "negative_torque_fraction": negative,
            })

    rows.insert(0, LOCKED_REFERENCE)
    rows = annotate_rows(rows)

    oracle_csv = wave / "desync_classifier_oracle.csv"
    with oracle_csv.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys(), lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# 第 08 章同步/失步分类离线检查",
        "",
        "本检查不生成新的 PLECS 波形。它复用同一个同步/失步分类函数，重读信号级参考和 C08 PLECS summary，确认同步正例与失步场景的判据一致。",
        "",
        "| 场景 | 来源 | 速度比 | 累计滑移/圈 | 负转矩占比 | 期望分类 | 实际分类 | 结果 |",
        "|---|---|---:|---:|---:|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {scenario} | {source} | {speed_ratio:.4f} | {phase_slip_cycles:.3f} | "
            "{negative_torque_fraction:.3f} | {expected_classification} | {classification} | {result} |".format(**row)
        )
    lines.extend([
        "",
        "## 证据边界",
        "",
        "- `signal_locked_reference` 只证明阈值能识别一个有界滑移的同步信号夹具，不是 PLECS 电机仿真。",
        "- `sync_follow` 来自 PLECS CSV，和三个失步场景使用同一分类函数。",
        "- 速度比和累计滑移是同步/失步主判据；负转矩占比只辅助观察转矩脉动，不单独否决同步。",
    ])
    report = root / "reports" / "08-open-loop-desync-classifier.md"
    report.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8", newline="")

    passed = all(row["result"] == "PASS" for row in rows)
    print(f"Generated C08 desync classifier oracle. rows={len(rows)} pass={passed}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

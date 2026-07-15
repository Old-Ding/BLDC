"""复核第 14 章 PLECS 原生诊断字段，并运行失败样本谓词。"""

from __future__ import annotations

import csv
import statistics
from copy import deepcopy
from pathlib import Path


TAIL = 5000
SCENARIOS = ("zero_speed_start", "target_step", "load_step", "invalid_hall", "overload")
REQUIRED_NATIVE_COLUMNS = (
    "hall_a", "hall_b", "hall_c", "hall_code", "hall_decoded_sector",
    "hall_transition_class", "hall_legal_event", "hall_direction",
    "hall_speed_feedback_rad_s", "hall_timeout", "hall_enable", "hall_fault",
    "hall_edge_count", "gate_ah", "gate_al", "gate_bh", "gate_bl", "gate_ch", "gate_cl",
)


def read_csv(path: Path) -> list[dict[str, float]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return [{key: float(value) for key, value in row.items()} for row in csv.DictReader(stream)]


def add_diagnostics(rows: list[dict[str, float]]) -> list[dict[str, object]]:
    missing = [column for column in REQUIRED_NATIVE_COLUMNS if column not in rows[0]]
    if missing:
        raise RuntimeError(f"missing native C14 diagnostics: {missing}")
    out: list[dict[str, object]] = []
    for row in rows:
        gate_all_off = int(all(row[name] < 0.5 for name in ("gate_ah", "gate_al", "gate_bh", "gate_bl", "gate_ch", "gate_cl")))
        out.append({**row, "gate_all_off": gate_all_off})
    return out


def rise_after(rows: list[dict[str, object]], trigger_s: float, threshold_rad_s: float) -> float:
    for row in rows:
        if float(row["time_s"]) >= trigger_s and float(row["speed_rad_s"]) >= threshold_rad_s:
            return float(row["time_s"]) - trigger_s
    return -1.0


def scenario_metrics(name: str, rows: list[dict[str, object]]) -> dict[str, object]:
    tail_rows = rows[-TAIL:]
    hall_valid = [row for row in tail_rows if abs(float(row["hall_speed_feedback_rad_s"])) > 1e-9]
    post_load = [row for row in rows if float(row["load_torque_Nm"]) > 0.0]
    fault_rows = [row for row in rows if float(row["hall_fault"]) >= 0.5]
    target_step_s = next(
        (float(rows[i]["time_s"]) for i in range(1, len(rows))
         if float(rows[i - 1]["speed_target_rad_s"]) != float(rows[i]["speed_target_rad_s"])),
        0.0,
    )
    return {
        "scenario": name,
        "final_speed_rad_s": float(rows[-1]["speed_rad_s"]),
        "tail_abs_error_rad_s": statistics.fmean(
            abs(float(row["speed_target_rad_s"]) - float(row["speed_rad_s"])) for row in tail_rows
        ),
        "hall_tail_bias_rad_s": (
            abs(
                statistics.fmean(float(row["speed_rad_s"]) for row in hall_valid)
                - statistics.fmean(float(row["hall_speed_feedback_rad_s"]) for row in hall_valid)
            ) if hall_valid else float("inf")
        ),
        "rise_to_50_from_start_s": rise_after(rows, 0.0, 50.0),
        "rise_to_55_after_target_step_s": rise_after(rows, target_step_s, 55.0) if target_step_s > 0 else -1.0,
        "post_load_high_saturation_fraction": (
            sum(float(row["effective_duty"]) > 0.85 for row in post_load) / len(post_load) if post_load else 0.0
        ),
        "fault_all_off_fraction": (
            sum(int(row["gate_all_off"]) == 1 for row in fault_rows) / len(fault_rows) if fault_rows else 0.0
        ),
        "hall_fault_fraction": sum(float(row["hall_fault"]) >= 0.5 for row in rows) / len(rows),
        "hall_enable_tail_fraction": sum(float(row["hall_enable"]) >= 0.5 for row in tail_rows) / len(tail_rows),
        "hall_edge_count": int(max(float(row["hall_edge_count"]) for row in rows)),
        "peak_phase_current_A": max(
            max(abs(float(row["ia_A"])), abs(float(row["ib_A"])), abs(float(row["ic_A"]))) for row in rows
        ),
    }


def accepts(metrics: dict[str, object]) -> bool:
    scenario = str(metrics["scenario"])
    err = float(metrics["tail_abs_error_rad_s"])
    hall = float(metrics["hall_tail_bias_rad_s"])
    rise_start = float(metrics["rise_to_50_from_start_s"])
    rise_step = float(metrics["rise_to_55_after_target_step_s"])
    high_sat = float(metrics["post_load_high_saturation_fraction"])
    fault_off = float(metrics["fault_all_off_fraction"])
    peak = float(metrics["peak_phase_current_A"])
    final_speed = float(metrics["final_speed_rad_s"])

    if scenario == "zero_speed_start":
        return err <= 5 and hall <= 2 and 0 <= rise_start <= 0.03 and fault_off == 0 and peak <= 35
    if scenario == "target_step":
        return err <= 5 and hall <= 2 and 0 <= rise_step <= 0.12 and fault_off == 0 and high_sat <= 0.05
    if scenario == "load_step":
        return err <= 8 and hall <= 2 and high_sat >= 0.5 and fault_off == 0
    if scenario == "invalid_hall":
        return err <= 5 and hall <= 2 and fault_off >= 0.99
    if scenario == "overload":
        return final_speed < 55 and err >= 15 and hall <= 2 and high_sat >= 0.8 and fault_off == 0 and peak <= 35
    raise ValueError(f"unknown scenario: {scenario}")


def mutated_metrics(summary: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    mutations: list[dict[str, object]] = []
    startup = deepcopy(summary["zero_speed_start"])
    startup["scenario"] = "zero_speed_start"
    startup["tail_abs_error_rad_s"] = 18.0
    startup["rise_to_50_from_start_s"] = -1.0
    mutations.append({"mutation": "startup_failure", **startup})

    steady = deepcopy(summary["target_step"])
    steady["scenario"] = "target_step"
    steady["tail_abs_error_rad_s"] = 8.0
    mutations.append({"mutation": "steady_error_over_limit", **steady})

    load = deepcopy(summary["load_step"])
    load["scenario"] = "load_step"
    load["tail_abs_error_rad_s"] = 12.0
    load["post_load_high_saturation_fraction"] = 0.30
    mutations.append({"mutation": "load_recovery_timeout", **load})

    invalid = deepcopy(summary["invalid_hall"])
    invalid["scenario"] = "invalid_hall"
    invalid["fault_all_off_fraction"] = 0.0
    mutations.append({"mutation": "invalid_hall_not_all_off", **invalid})

    overload = deepcopy(summary["load_step"])
    overload["scenario"] = "overload"
    mutations.append({"mutation": "overload_misclassified", **overload})
    return mutations


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    wave = root / "waveforms" / "14-complete-hall-closed-loop"
    summary_rows: list[dict[str, object]] = []

    for scenario in SCENARIOS:
        rows = add_diagnostics(read_csv(wave / f"plecs_{scenario}.csv"))
        diag_path = wave / f"plecs_{scenario}_diagnostics.csv"
        with diag_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=rows[0].keys(), lineterminator="\r\n")
            writer.writeheader()
            writer.writerows(rows)
        metrics = scenario_metrics(scenario, rows)
        metrics["result"] = "PASS" if accepts(metrics) else "FAIL"
        summary_rows.append(metrics)

    acceptance_csv = wave / "plecs_acceptance_summary_v2.csv"
    with acceptance_csv.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=summary_rows[0].keys(), lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(summary_rows)

    by_scenario = {str(row["scenario"]): row for row in summary_rows}
    mutation_rows = []
    for row in mutated_metrics(by_scenario):
        row["result"] = "FAIL_DETECTED" if not accepts(row) else "MISSED"
        mutation_rows.append(row)

    mutation_csv = wave / "acceptance_mutations.csv"
    with mutation_csv.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=mutation_rows[0].keys(), lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(mutation_rows)

    lines = [
        "# 第 14 章完整闭环验收检查",
        "",
        "本检查只读取 C14 PLECS CSV 中已经原生导出的 Hall/control/gate 字段；若缺少这些列，检查直接失败。",
        "",
        "| 场景 | 尾段误差/rad/s | Hall 偏差/rad/s | 起动到 50/s | 阶跃后到 55/s | 高限幅占比 | 全关占比 | Hall fault 占比 | Hall enable 尾段占比 | Hall 边沿数 | 峰值电流/A | 结果 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in summary_rows:
        lines.append(
            "| {scenario} | {tail_abs_error_rad_s:.3f} | {hall_tail_bias_rad_s:.3f} | "
            "{rise_to_50_from_start_s:.5f} | {rise_to_55_after_target_step_s:.5f} | "
            "{post_load_high_saturation_fraction:.3f} | {fault_all_off_fraction:.3f} | "
            "{hall_fault_fraction:.3f} | {hall_enable_tail_fraction:.3f} | {hall_edge_count} | "
            "{peak_phase_current_A:.3f} | {result} |".format(**row)
        )
    lines.extend([
        "",
        "## 失败样本谓词",
        "",
        "| 失败样本 | 对应场景 | 结果 |",
        "|---|---|---|",
    ])
    for row in mutation_rows:
        lines.append(f"| {row['mutation']} | {row['scenario']} | {row['result']} |")
    lines.extend([
        "",
        "## 证据边界",
        "",
        "- Hall A/B/C、Hall code、decoded sector、fault、enable 和六路 gate 均来自 C14 PLECS CSV 原生列。",
        "- 本脚本只复核字段完整性、验收谓词和失败样本，不从机械角重建被测 Hall 结果。",
    ])
    report = root / "reports" / "14-complete-hall-acceptance-check.md"
    report.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8", newline="")

    formal_pass = all(row["result"] == "PASS" for row in summary_rows)
    mutation_pass = all(row["result"] == "FAIL_DETECTED" for row in mutation_rows)
    print(f"Generated C14 acceptance check. formal_pass={formal_pass} mutation_pass={mutation_pass}")
    return 0 if formal_pass and mutation_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())

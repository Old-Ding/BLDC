"""运行第 12 章 Hall 边沿测速、滤波和超时场景。"""

from __future__ import annotations

import csv
import socket
import statistics
import subprocess
import sys
import xmlrpc.client
from pathlib import Path

MODEL = "ch12_hall_speed"
NAMES = (
    "ia_A", "ib_A", "ic_A", "ea_V", "eb_V", "ec_V", "speed_rad_s", "torque_Nm",
    "cmd_a", "cmd_b", "cmd_c", "vab_V", "vbc_V", "vca_V", "mechanical_angle_rad",
    "hall_a", "hall_b", "hall_c", "hall_valid", "hall_code",
    "hall_transition_class", "hall_direction", "hall_legal_event",
    "speed_raw_rad_s", "speed_filtered_rad_s", "timeout", "legal_edge_count",
)
SCENARIOS = (
    {"name": "slow_25", "speed": 25.0, "pole_pairs": 1},
    {"name": "medium_100", "speed": 100.0, "pole_pairs": 1},
    {"name": "fast_400", "speed": 400.0, "pole_pairs": 1},
    {"name": "reverse_100", "speed": -100.0, "pole_pairs": 1},
    {"name": "medium_100_pp4", "speed": 100.0, "pole_pairs": 4},
    {"name": "stopped_timeout", "speed": 0.0, "pole_pairs": 1},
)
def main() -> int:
    root = Path(__file__).resolve().parents[1]
    model = root / "models/plecs/ch12_hall_speed/ch12_hall_speed.plecs"
    wave = root / "waveforms/12-hall-speed"
    assets = root / "assets/12-hall-speed"
    wave.mkdir(parents=True, exist_ok=True)
    assets.mkdir(parents=True, exist_ok=True)

    try:
        with socket.create_connection(("localhost", 1080), timeout=2):
            pass
    except OSError:
        print("PLECS_RPC_NOT_READY", file=sys.stderr)
        return 2

    times = [round(index * 0.0001, 10) for index in range(2501)]
    server = xmlrpc.client.ServerProxy("http://localhost:1080/RPC2", allow_none=True)
    rows: list[dict[str, object]] = []
    try:
        try:
            server.plecs.close(MODEL)
        except Exception:
            pass
        server.plecs.load(str(model))
        for scenario in SCENARIOS:
            result = server.plecs.simulate(MODEL, {"ModelVars": {
                "Udc_V": 300.0, "load_torque_Nm": 0.0, "current_ref_A": 0.0,
                "initial_speed_rad_s": scenario["speed"], "phase_cmd": [0, 0, 0],
                "pole_pairs": scenario["pole_pairs"], "hall_offset_rad": 0.0,
                "force_invalid": 0, "invalid_code": 0,
            }, "SolverOpts": {"OutputTimes": times}})
            values = result["Values"]
            if len(values) != len(NAMES):
                raise RuntimeError(f"signals={len(values)}")
            data = {name: list(value) for name, value in zip(NAMES, values, strict=True)}
            data["time_s"] = list(result["Time"])
            bit_codes = [
                (round(a) << 2) | (round(b) << 1) | round(c)
                for a, b, c in zip(data["hall_a"], data["hall_b"], data["hall_c"], strict=True)
            ]
            native_codes = [int(round(value)) for value in data["hall_code"]]
            if bit_codes != native_codes:
                raise RuntimeError(f"hall_code mismatch in {scenario['name']}")
            edges = int(round(max(data["legal_edge_count"])))
            columns = (
                "time_s", "mechanical_angle_rad", "speed_rad_s",
                "hall_a", "hall_b", "hall_c", "hall_code",
                "hall_transition_class", "hall_direction", "hall_legal_event",
                "speed_raw_rad_s", "speed_filtered_rad_s", "timeout", "legal_edge_count",
            )
            with (wave / f"plecs_{scenario['name']}.csv").open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream, lineterminator="\r\n")
                writer.writerow(columns)
                for index in range(len(times)):
                    writer.writerow(data[column][index] for column in columns)

            valid = [abs(value) for value in data["speed_raw_rad_s"] if abs(value) > 1e-9]
            signed_valid = [value for value in data["speed_raw_rad_s"] if abs(value) > 1e-9]
            median = statistics.median(signed_valid) if signed_valid else 0.0
            actual = abs(statistics.fmean(data["speed_rad_s"]))
            error = abs(abs(median) - actual) / actual if actual > 1e-9 else 0.0
            if float(scenario["speed"]) > 0:
                passed = edges >= 3 and error < 0.03 and median > 0
            elif float(scenario["speed"]) < 0:
                passed = edges >= 3 and error < 0.03 and median < 0
            else:
                passed = edges == 0 and round(data["timeout"][-1]) == 1 and data["speed_raw_rad_s"][-1] == 0
            rows.append({
                "scenario": scenario["name"],
                "pole_pairs": scenario["pole_pairs"],
                "initial_speed_rad_s": scenario["speed"],
                "legal_edge_count": edges,
                "median_raw_speed_rad_s": median if valid else 0.0,
                "mean_actual_abs_speed_rad_s": actual,
                "relative_error": error,
                "timeout_final": int(round(data["timeout"][-1])),
                "result": "PASS" if passed else "FAIL",
            })
            if scenario["name"] == "fast_400":
                capture = subprocess.run([
                    "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                    str(root / "scripts/capture_plecs_window.ps1"), "-TitlePattern",
                    f"*{MODEL}/Scope*", "-OutputPath", str(assets / "plecs_scope_hall_edges_fast.png"),
                ], text=True, capture_output=True)
                if capture.returncode:
                    raise RuntimeError(capture.stderr)
    finally:
        try:
            server.plecs.close(MODEL)
        except Exception:
            pass

    with (wave / "plecs_hall_speed_summary.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys(), lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# 第 12 章 Hall 边沿测速 PLECS 报告",
        "",
        "| 场景 | 极对数 | 初速/rad/s | 合法边沿数 | 原始估算中位数/rad/s | 实际速度绝对均值/rad/s | 相对误差 | 最终超时 | 结果 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {scenario} | {pole_pairs} | {initial_speed_rad_s:.1f} | {legal_edge_count} | "
            "{median_raw_speed_rad_s:.3f} | {mean_actual_abs_speed_rad_s:.3f} | "
            "{relative_error:.4f} | {timeout_final} | {result} |".format(**row)
        )
    (root / "reports/12-hall-speed-test_report.md").write_text(
        "\r\n".join(lines) + "\r\n", encoding="utf-8", newline=""
    )
    passed = sum(row["result"] == "PASS" for row in rows)
    print(
        f"Generated chapter 12 PLECS Hall-speed evidence. "
        f"scenarios={len(rows)} pass={passed} time_points=2501 signals={len(NAMES)}"
    )
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())

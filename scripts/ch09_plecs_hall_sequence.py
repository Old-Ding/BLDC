"""运行第 09 章 Hall 正反转和非法状态场景。"""

from __future__ import annotations

import csv
import socket
import subprocess
import sys
import xmlrpc.client
from pathlib import Path

MODEL = "ch09_hall_sequence"
BASE_NAMES = (
    "ia_A", "ib_A", "ic_A", "ea_V", "eb_V", "ec_V", "speed_rad_s", "torque_Nm",
    "cmd_a", "cmd_b", "cmd_c", "vab_V", "vbc_V", "vca_V", "mechanical_angle_rad",
)
NAMES = (*BASE_NAMES, "hall_a", "hall_b", "hall_c", "hall_valid")
SEQUENCE = (5, 1, 3, 2, 6, 4)
SCENARIOS = (
    {"name": "forward", "speed": 100.0, "force_invalid": 0, "invalid_code": 0},
    {"name": "reverse", "speed": -100.0, "force_invalid": 0, "invalid_code": 0},
    {"name": "invalid_000", "speed": 100.0, "force_invalid": 1, "invalid_code": 0},
    {"name": "invalid_111", "speed": 100.0, "force_invalid": 1, "invalid_code": 7},
)


def transition_codes(codes: list[int]) -> list[int]:
    output = [codes[0]]
    for code in codes[1:]:
        if code != output[-1]:
            output.append(code)
    return output


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    model = root / "models/plecs/ch09_hall_sequence/ch09_hall_sequence.plecs"
    wave = root / "waveforms/09-hall-sequence"
    assets = root / "assets/09-hall-sequence"
    wave.mkdir(parents=True, exist_ok=True)
    assets.mkdir(parents=True, exist_ok=True)
    try:
        with socket.create_connection(("localhost", 1080), timeout=2):
            pass
    except OSError:
        print("PLECS_RPC_NOT_READY", file=sys.stderr)
        return 2
    times = [round(index * 0.0001, 10) for index in range(701)]
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
                "pole_pairs": 1, "hall_offset_rad": 0.0, "force_invalid": scenario["force_invalid"],
                "invalid_code": scenario["invalid_code"],
            }, "SolverOpts": {"OutputTimes": times}})
            values = result["Values"]
            if len(values) != 19:
                raise RuntimeError(f"signals={len(values)}")
            data = {name: list(value) for name, value in zip(NAMES, values, strict=True)}
            data["time_s"] = list(result["Time"])
            codes = [
                (round(a) << 2) | (round(b) << 1) | round(c)
                for a, b, c in zip(data["hall_a"], data["hall_b"], data["hall_c"], strict=True)
            ]
            data["hall_code"] = codes
            columns = ("time_s", "mechanical_angle_rad", "speed_rad_s", "hall_a", "hall_b", "hall_c", "hall_valid", "hall_code")
            with (wave / f"plecs_{scenario['name']}.csv").open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream, lineterminator="\r\n")
                writer.writerow(columns)
                for index in range(len(times)):
                    writer.writerow(data[column][index] for column in columns)
            transitions = transition_codes(codes)
            valid_transitions = [code for code in transitions if code in SEQUENCE]
            direction_steps = []
            for first, second in zip(valid_transitions[:-1], valid_transitions[1:], strict=True):
                delta = (SEQUENCE.index(second) - SEQUENCE.index(first)) % 6
                if delta in (1, 5):
                    direction_steps.append(1 if delta == 1 else -1)
            illegal_samples = sum(code in (0, 7) for code in codes)
            if scenario["name"] == "forward":
                passed = len(valid_transitions) >= 5 and direction_steps and all(step == 1 for step in direction_steps) and illegal_samples == 0
            elif scenario["name"] == "reverse":
                passed = len(valid_transitions) >= 5 and direction_steps and all(step == -1 for step in direction_steps) and illegal_samples == 0
            else:
                passed = illegal_samples == len(codes) and len(transitions) == 1
            rows.append({
                "scenario": scenario["name"], "transition_count": len(transitions) - 1,
                "observed_sequence": "-".join(str(code) for code in transitions[:10]),
                "direction": ("forward" if direction_steps and sum(direction_steps) > 0 else "reverse" if direction_steps else "invalid"),
                "illegal_samples": illegal_samples, "result": "PASS" if passed else "FAIL",
            })
            if scenario["name"] == "forward":
                capture = subprocess.run([
                    "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                    str(root / "scripts/capture_plecs_window.ps1"), "-TitlePattern", f"*{MODEL}/Scope*",
                    "-OutputPath", str(assets / "plecs_scope_hall_forward.png"),
                ], text=True, capture_output=True)
                if capture.returncode:
                    raise RuntimeError(capture.stderr)
    finally:
        try:
            server.plecs.close(MODEL)
        except Exception:
            pass
    with (wave / "plecs_hall_summary.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys(), lineterminator="\r\n")
        writer.writeheader(); writer.writerows(rows)
    lines = ["# 第 09 章 Hall 序列 PLECS 报告", "", "| 场景 | 跳变数 | 观测序列 | 方向 | 非法采样数 | 结果 |", "|---|---:|---|---|---:|---|"]
    for row in rows:
        lines.append("| {scenario} | {transition_count} | {observed_sequence} | {direction} | {illegal_samples} | {result} |".format(**row))
    (root / "reports/09-hall-sequence-test_report.md").write_text("\r\n".join(lines) + "\r\n", encoding="utf-8", newline="")
    passed = sum(row["result"] == "PASS" for row in rows)
    print(f"Generated chapter 09 PLECS Hall evidence. scenarios=4 pass={passed} time_points=701 signals=19")
    return 0 if passed == 4 else 1


if __name__ == "__main__":
    raise SystemExit(main())

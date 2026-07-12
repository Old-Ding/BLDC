"""运行第 08 章缓斜坡、过快斜坡和负载扰动失步场景。"""

from __future__ import annotations

import csv
import math
import socket
import statistics
import subprocess
import sys
import xmlrpc.client
from pathlib import Path

MODEL = "ch08_open_loop_desync"
NAMES = (
    "ia_A", "ib_A", "ic_A", "ea_V", "eb_V", "ec_V", "speed_rad_s", "torque_Nm",
    "cmd_a", "cmd_b", "cmd_c", "vab_V", "vbc_V", "vca_V", "mechanical_angle_raw_rad",
)
SCENARIOS = (
    {"name": "gentle_ramp", "f0": 5.0, "f1": 25.0, "ramp": 0.25, "load_after": 0.0, "load_step": 1.0},
    {"name": "overfast_ramp", "f0": 5.0, "f1": 80.0, "ramp": 0.08, "load_after": 0.0, "load_step": 1.0},
    {"name": "load_step", "f0": 5.0, "f1": 25.0, "ramp": 0.25, "load_after": 8.0, "load_step": 0.18},
)


def command_phase(t: float, scenario: dict[str, float | str]) -> tuple[float, float]:
    run_t = t - 0.02
    if run_t <= 0:
        return 0.0, 0.0
    f0, f1, ramp = float(scenario["f0"]), float(scenario["f1"]), float(scenario["ramp"])
    if run_t < ramp:
        k = (f1 - f0) / ramp
        return 2 * math.pi * (f0 * run_t + 0.5 * k * run_t * run_t), f0 + k * run_t
    return 2 * math.pi * (0.5 * (f0 + f1) * ramp + f1 * (run_t - ramp)), f1


def unwrap(raw: list[float]) -> list[float]:
    output = [raw[0]]
    offset = 0.0
    for previous, current in zip(raw[:-1], raw[1:], strict=True):
        delta = current - previous
        if delta < -math.pi:
            offset += 2 * math.pi
        elif delta > math.pi:
            offset -= 2 * math.pi
        output.append(current + offset)
    return output


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    model = root / "models/plecs/ch08_open_loop_desync/ch08_open_loop_desync.plecs"
    wave = root / "waveforms/08-open-loop-desync"
    assets = root / "assets/08-open-loop-desync"
    wave.mkdir(parents=True, exist_ok=True)
    assets.mkdir(parents=True, exist_ok=True)
    try:
        with socket.create_connection(("localhost", 1080), timeout=2):
            pass
    except OSError:
        print("PLECS_RPC_NOT_READY", file=sys.stderr)
        return 2
    times = [round(index * 0.0005, 10) for index in range(701)]
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
                "Udc_V": 48.0, "load_torque_Nm": 0.0, "current_ref_A": 0.0,
                "initial_speed_rad_s": 0.0, "phase_cmd": [0, 0, 0], "pole_pairs": 1,
                "alignment_s": 0.02, "start_frequency_Hz": scenario["f0"],
                "end_frequency_Hz": scenario["f1"], "ramp_duration_s": scenario["ramp"],
                "sequence_direction": 1, "load_before_Nm": 0.0,
                "load_after_Nm": scenario["load_after"], "load_step_time_s": scenario["load_step"],
            }, "SolverOpts": {"OutputTimes": times}})
            values = result["Values"]
            if len(values) != 15:
                raise RuntimeError(f"signals={len(values)}")
            data = {name: list(value) for name, value in zip(NAMES, values, strict=True)}
            data["time_s"] = list(result["Time"])
            rotor = unwrap(data["mechanical_angle_raw_rad"])
            phase = [command_phase(t, scenario) for t in data["time_s"]]
            command = [item[0] for item in phase]
            frequency = [item[1] for item in phase]
            unwrapped_error = [cmd - angle for cmd, angle in zip(command, rotor, strict=True)]
            wrapped_error = [math.atan2(math.sin(value), math.cos(value)) for value in unwrapped_error]
            load = [0.0 if t < float(scenario["load_step"]) else float(scenario["load_after"]) for t in data["time_s"]]
            data.update(rotor_angle_unwrapped_rad=rotor, command_electrical_angle_rad=command,
                        command_frequency_Hz=frequency, phase_error_rad=wrapped_error,
                        phase_error_unwrapped_rad=unwrapped_error, load_torque_Nm=load)
            columns = ("time_s", "command_frequency_Hz", "command_electrical_angle_rad",
                       "mechanical_angle_raw_rad", "rotor_angle_unwrapped_rad", "phase_error_rad",
                       "phase_error_unwrapped_rad", "load_torque_Nm", *NAMES[:-1])
            with (wave / f"plecs_{scenario['name']}.csv").open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream, lineterminator="\r\n")
                writer.writerow(columns)
                for index in range(len(times)):
                    writer.writerow(data[column][index] for column in columns)
            tail = 100
            sync_speed = 2 * math.pi * frequency[-1]
            slip_cycles = abs(unwrapped_error[-1] - unwrapped_error[0]) / (2 * math.pi)
            rows.append({
                "scenario": scenario["name"], "final_frequency_Hz": frequency[-1],
                "synchronous_speed_rad_s": sync_speed, "final_speed_rad_s": data["speed_rad_s"][-1],
                "tail_mean_speed_rad_s": statistics.fmean(data["speed_rad_s"][-tail:]),
                "speed_ratio": statistics.fmean(data["speed_rad_s"][-tail:]) / sync_speed,
                "phase_slip_cycles": slip_cycles,
                "negative_torque_fraction": sum(value < 0 for value in data["torque_Nm"]) / len(times),
                "tail_mean_torque_Nm": statistics.fmean(data["torque_Nm"][-tail:]),
                "result": "MEASURED",
            })
            if scenario["name"] == "gentle_ramp":
                capture = subprocess.run([
                    "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                    str(root / "scripts/capture_plecs_window.ps1"), "-TitlePattern",
                    f"*{MODEL}/Scope*", "-OutputPath", str(assets / "plecs_scope_gentle_ramp.png"),
                ], text=True, capture_output=True)
                if capture.returncode:
                    raise RuntimeError(capture.stderr)
    finally:
        try:
            server.plecs.close(MODEL)
        except Exception:
            pass

    by_name = {str(row["scenario"]): row for row in rows}
    gentle = by_name["gentle_ramp"]
    by_name["gentle_ramp"]["result"] = "PASS" if (
        float(gentle["phase_slip_cycles"]) > 2.0 and float(gentle["speed_ratio"]) < 0.2
    ) else "FAIL"
    overfast = by_name["overfast_ramp"]
    by_name["overfast_ramp"]["result"] = "PASS" if (
        float(overfast["phase_slip_cycles"]) > 4.0 * float(gentle["phase_slip_cycles"])
        and abs(float(overfast["tail_mean_speed_rad_s"])) < 5.0
    ) else "FAIL"
    loaded = by_name["load_step"]
    by_name["load_step"]["result"] = "PASS" if (
        float(loaded["phase_slip_cycles"]) > float(gentle["phase_slip_cycles"]) + 0.2
        and abs(float(loaded["final_speed_rad_s"]) - float(gentle["final_speed_rad_s"])) > 20.0
    ) else "FAIL"

    with (wave / "plecs_desync_summary.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys(), lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(rows)
    lines = [
        "# 第 08 章开环失步诊断 PLECS 报告", "",
        "| 场景 | 最终电频率/Hz | 尾段平均速度/rad/s | 速度比 | 累计滑移/圈 | 负转矩占比 | 尾段转矩/N m | 结果 |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {scenario} | {final_frequency_Hz:.3f} | {tail_mean_speed_rad_s:.3f} | {speed_ratio:.4f} | "
            "{phase_slip_cycles:.3f} | {negative_torque_fraction:.3f} | {tail_mean_torque_Nm:.3f} | {result} |".format(**row)
        )
    (root / "reports/08-open-loop-desync-test_report.md").write_text(
        "\r\n".join(lines) + "\r\n", encoding="utf-8", newline=""
    )
    passed = sum(row["result"] == "PASS" for row in rows)
    print(f"Generated chapter 08 PLECS desynchronization evidence. scenarios=3 pass={passed} time_points=701 signals=15")
    return 0 if passed == 3 else 1


if __name__ == "__main__":
    raise SystemExit(main())

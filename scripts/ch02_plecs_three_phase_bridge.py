"""运行第 02 章 PLECS 三相桥场景并导出逐点证据。"""

from __future__ import annotations

import csv
import itertools
import socket
import statistics
import subprocess
import sys
import time
import xmlrpc.client
from dataclasses import dataclass
from pathlib import Path


RPC_URL = "http://localhost:1080/RPC2"
RPC_TIMEOUT_S = 60
MODEL_NAME = "ch02_three_phase_bridge"
U_DC_V = 48.0
SAMPLE_TIME_S = 10e-6
STOP_TIME_S = 2e-3


@dataclass(frozen=True)
class Scenario:
    name: str
    phase_cmd: tuple[int, int, int]
    high_phase: int | None
    low_phase: int | None


SCENARIOS = (
    Scenario("Apos_Bneg", (1, -1, 0), 0, 1),
    Scenario("Apos_Cneg", (1, 0, -1), 0, 2),
    Scenario("Bpos_Cneg", (0, 1, -1), 1, 2),
    Scenario("Bpos_Aneg", (-1, 1, 0), 1, 0),
    Scenario("Cpos_Aneg", (-1, 0, 1), 2, 0),
    Scenario("Cpos_Bneg", (0, -1, 1), 2, 1),
    Scenario("all_off", (0, 0, 0), None, None),
)


class TimeoutTransport(xmlrpc.client.Transport):
    def make_connection(self, host: str):  # type: ignore[no-untyped-def]
        connection = super().make_connection(host)
        connection.timeout = RPC_TIMEOUT_S
        return connection


def paths() -> dict[str, Path]:
    root = Path(__file__).resolve().parents[1]
    return {
        "root": root,
        "model": root / "models/plecs/ch02_three_phase_bridge/ch02_three_phase_bridge.plecs",
        "waveforms": root / "waveforms/02-three-phase-bridge",
        "assets": root / "assets/02-three-phase-bridge",
        "report": root / "reports/02-three-phase-bridge-test_report.md",
        "capture": root / "scripts/capture_plecs_window.ps1",
    }


def require_rpc() -> None:
    try:
        with socket.create_connection(("localhost", 1080), timeout=2):
            return
    except OSError as exc:
        raise RuntimeError("PLECS RPC 未监听 localhost:1080。") from exc


def output_times() -> list[float]:
    count = round(STOP_TIME_S / SAMPLE_TIME_S) + 1
    return [index * SAMPLE_TIME_S for index in range(count)]


def run_scenario(
    server: xmlrpc.client.ServerProxy,
    scenario: Scenario,
    times: list[float],
) -> dict[str, list[float]]:
    options = {
        "ModelVars": {
            "Udc_V": U_DC_V,
            "load_torque_Nm": 0.0,
            "current_ref_A": 0.0,
            "initial_speed_rad_s": 0.0,
            "phase_cmd": list(scenario.phase_cmd),
        },
        "SolverOpts": {"OutputTimes": times},
    }
    result = server.plecs.simulate(MODEL_NAME, options)
    values = result.get("Values", [])
    result_times = result.get("Time", [])
    if len(values) != 14 or len(result_times) != len(times):
        raise RuntimeError(
            f"PLECS 输出接口不匹配: signal_rows={len(values)}, time_points={len(result_times)}"
        )

    columns = (
        "ia_A",
        "ib_A",
        "ic_A",
        "ea_V",
        "eb_V",
        "ec_V",
        "speed_rad_s",
        "electromagnetic_torque_Nm",
        "phase_cmd_a",
        "phase_cmd_b",
        "phase_cmd_c",
        "vab_V",
        "vbc_V",
        "vca_V",
    )
    data = {name: list(row) for name, row in zip(columns, values, strict=True)}
    data["time_s"] = list(result_times)
    return data


def evaluate(data: dict[str, list[float]], scenario: Scenario) -> dict[str, object]:
    phase_currents = (data["ia_A"], data["ib_A"], data["ic_A"])
    line_voltages = data["vab_V"] + data["vbc_V"] + data["vca_V"]
    current_sum_peak = max(
        abs(ia + ib + ic)
        for ia, ib, ic in zip(*phase_currents, strict=True)
    )
    peak_line_voltage = max(abs(value) for value in line_voltages)
    final_currents = [phase[-1] for phase in phase_currents]

    if scenario.high_phase is None or scenario.low_phase is None:
        peak_phase_current = max(abs(value) for phase in phase_currents for value in phase)
        passed = peak_phase_current <= 1e-6 and peak_line_voltage <= 1e-6
        reason = (
            f"peak_phase_current_A={peak_phase_current:.6g}; "
            f"peak_line_voltage_V={peak_line_voltage:.6g}"
        )
    else:
        high_current = final_currents[scenario.high_phase]
        low_current = final_currents[scenario.low_phase]
        float_phase = 3 - scenario.high_phase - scenario.low_phase
        float_current = final_currents[float_phase]
        passed = (
            high_current >= 10.0
            and low_current <= -10.0
            and abs(float_current) <= 2.0
            and current_sum_peak <= 1e-6
            and peak_line_voltage >= 0.99 * U_DC_V
        )
        reason = (
            f"high_current_A={high_current:.4f}; low_current_A={low_current:.4f}; "
            f"float_current_A={float_current:.4f}; current_sum_peak_A={current_sum_peak:.3e}; "
            f"peak_line_voltage_V={peak_line_voltage:.4f}"
        )

    return {
        "scenario": scenario.name,
        "phase_cmd": " ".join(str(value) for value in scenario.phase_cmd),
        "final_ia_A": final_currents[0],
        "final_ib_A": final_currents[1],
        "final_ic_A": final_currents[2],
        "current_sum_peak_A": current_sum_peak,
        "peak_line_voltage_V": peak_line_voltage,
        "tail_torque_mean_Nm": statistics.fmean(data["electromagnetic_torque_Nm"][-20:]),
        "result": "PASS" if passed else "FAIL",
        "reason": reason,
    }


def write_timeseries(path: Path, data: dict[str, list[float]]) -> None:
    columns = (
        "time_s",
        "phase_cmd_a",
        "phase_cmd_b",
        "phase_cmd_c",
        "ia_A",
        "ib_A",
        "ic_A",
        "vab_V",
        "vbc_V",
        "vca_V",
        "ea_V",
        "eb_V",
        "ec_V",
        "speed_rad_s",
        "electromagnetic_torque_Nm",
    )
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\r\n")
        writer.writerow(columns)
        for index in range(len(data["time_s"])):
            writer.writerow(data[column][index] for column in columns)


def write_gate_truth_table(path: Path) -> dict[str, int]:
    counts = {"total": 0, "shoot_through": 0, "six_step": 0, "other_safe": 0}
    fields = (
        "AH",
        "BH",
        "CH",
        "AL",
        "BL",
        "CL",
        "phase_a",
        "phase_b",
        "phase_c",
        "shoot_through",
        "six_step_valid",
    )
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\r\n")
        writer.writeheader()
        for ah, bh, ch, al, bl, cl in itertools.product((0, 1), repeat=6):
            highs = (ah, bh, ch)
            lows = (al, bl, cl)
            shoot = any(high and low for high, low in zip(highs, lows, strict=True))
            states = tuple(
                2 if high and low else 1 if high else -1 if low else 0
                for high, low in zip(highs, lows, strict=True)
            )
            six_step = sorted(states) == [-1, 0, 1]
            counts["total"] += 1
            if shoot:
                counts["shoot_through"] += 1
            elif six_step:
                counts["six_step"] += 1
            else:
                counts["other_safe"] += 1
            writer.writerow(
                dict(
                    zip(
                        fields,
                        (*highs, *lows, *states, int(shoot), int(six_step)),
                        strict=True,
                    )
                )
            )
    return counts


def capture_scope(root_paths: dict[str, Path]) -> None:
    output = root_paths["assets"] / "plecs_scope_Apos_Bneg.png"
    command = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(root_paths["capture"]),
        "-TitlePattern",
        f"*{MODEL_NAME}/Scope*",
        "-OutputPath",
        str(output),
    ]
    completed = subprocess.run(command, check=False, text=True, capture_output=True)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())
    print(completed.stdout.strip())


def write_summary(path: Path, rows: list[dict[str, object]]) -> None:
    fields = tuple(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(rows)


def write_report(
    path: Path,
    rows: list[dict[str, object]],
    truth_counts: dict[str, int],
) -> None:
    lines = [
        "# 第 02 章 PLECS 三相桥实验报告",
        "",
        "## 参数摘要",
        "",
        "| 参数 | 数值 | 单位 |",
        "|---|---:|---|",
        "| 直流母线电压 | 48 | V |",
        "| BLDC 相电阻 | 0.388 | ohm |",
        "| BLDC 相电感 | 2.84 | mH |",
        "| 初始机械角速度 | 0 | rad/s |",
        "| 单场景时长 | 2 | ms |",
        "| 输出采样间隔 | 10 | us |",
        "",
        "## PLECS 场景结果",
        "",
        "| 场景 | 三值相命令 | 末值 ia/A | 末值 ib/A | 末值 ic/A | 峰值线电压/V | 结果 |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {scenario} | `{phase_cmd}` | {final_ia_A:.4f} | {final_ib_A:.4f} | "
            "{final_ic_A:.4f} | {peak_line_voltage_V:.4f} | {result} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## 六路门极组合审计",
            "",
            f"- 全组合：{truth_counts['total']} 组。",
            f"- 同桥臂直通：{truth_counts['shoot_through']} 组。",
            f"- 符合 120 度六步导通：{truth_counts['six_step']} 组。",
            f"- 无直通但不属于六步有效矢量：{truth_counts['other_safe']} 组。",
            "",
            "## 证据边界",
            "",
            "PLECS 结果证明三值相命令经过真实两电平 IGBT 桥后，会形成对应的线电压和绕组电流路径。",
            "64 组门极表用于区分同桥臂直通、六步有效矢量和其他安全组合。",
            "本章不把三值命令误称为六路物理门极，也不声称已经包含驱动器传播延迟、死区和器件损耗。",
        ]
    )
    path.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8", newline="")


def main() -> int:
    started = time.monotonic()
    project = paths()
    try:
        require_rpc()
    except RuntimeError as exc:
        print(f"PLECS_RPC_NOT_READY {exc}", file=sys.stderr)
        return 2
    if not project["model"].is_file():
        print(f"MODEL_MISSING {project['model']}", file=sys.stderr)
        return 2

    project["waveforms"].mkdir(parents=True, exist_ok=True)
    project["assets"].mkdir(parents=True, exist_ok=True)
    project["report"].parent.mkdir(parents=True, exist_ok=True)

    times = output_times()
    server = xmlrpc.client.ServerProxy(
        RPC_URL,
        allow_none=True,
        transport=TimeoutTransport(),
    )
    rows: list[dict[str, object]] = []
    try:
        try:
            server.plecs.close(MODEL_NAME)
        except Exception:
            pass
        server.plecs.load(str(project["model"]))
        for scenario in SCENARIOS:
            print(f"PLECS_SCENARIO_START scenario={scenario.name}", flush=True)
            data = run_scenario(server, scenario, times)
            row = evaluate(data, scenario)
            rows.append(row)
            write_timeseries(
                project["waveforms"] / f"plecs_{scenario.name}.csv",
                data,
            )
            print(
                f"PLECS_SCENARIO_DONE scenario={scenario.name} result={row['result']}",
                flush=True,
            )
            if scenario.name == "Apos_Bneg":
                capture_scope(project)
    finally:
        try:
            server.plecs.close(MODEL_NAME)
        except Exception:
            pass

    truth_counts = write_gate_truth_table(project["waveforms"] / "gate_truth_table.csv")
    write_summary(project["waveforms"] / "plecs_bridge_summary.csv", rows)
    write_report(project["report"], rows, truth_counts)
    passed = sum(row["result"] == "PASS" for row in rows)
    print(
        "Generated chapter 02 PLECS bridge evidence. "
        f"scenarios={len(rows)} pass={passed} time_points={len(times)} "
        f"signals=14 gate_combinations={truth_counts['total']} "
        f"elapsed_s={time.monotonic() - started:.2f}"
    )
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())

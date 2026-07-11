"""运行第 01 章 PLECS BLDC 基准场景并导出可审查证据。"""

from __future__ import annotations

import csv
import math
import socket
import statistics
import sys
import time
import xmlrpc.client
from dataclasses import dataclass
from pathlib import Path


RPC_HOST = "localhost"
RPC_PORT = 1080
RPC_URL = f"http://{RPC_HOST}:{RPC_PORT}/RPC2"
RPC_TIMEOUT_S = 120
MODEL_NAME = "ch01_bldc_baseline"
SAMPLE_TIME_S = 0.0005
STOP_TIME_S = 0.3


@dataclass(frozen=True)
class Scenario:
    name: str
    load_torque_nm: float
    current_ref_a: float
    expected_behavior: str


SCENARIOS = (
    Scenario("nominal_load", 3.0, 5.0, "torque_tracking"),
    Scenario("overload", 6.0, 5.0, "current_limited_stall"),
)


class TimeoutTransport(xmlrpc.client.Transport):
    """限制单次 PLECS RPC 等待时间，避免服务异常时脚本永久阻塞。"""

    def make_connection(self, host: str):  # type: ignore[no-untyped-def]
        connection = super().make_connection(host)
        connection.timeout = RPC_TIMEOUT_S
        return connection


def project_paths() -> dict[str, Path]:
    root = Path(__file__).resolve().parents[1]
    return {
        "root": root,
        "model": root
        / "models"
        / "plecs"
        / "ch01_bldc_baseline"
        / "ch01_bldc_baseline.plecs",
        "results": root / "waveforms" / "01-bldc-control-chain",
        "report": root / "reports" / "01-bldc-control-chain-test_report.md",
    }


def require_rpc() -> None:
    try:
        with socket.create_connection((RPC_HOST, RPC_PORT), timeout=2):
            return
    except OSError as exc:
        raise RuntimeError(
            "PLECS RPC 未监听 localhost:1080。请在 PLECS Preferences 中启用 XML-RPC。"
        ) from exc


def output_times() -> list[float]:
    point_count = round(STOP_TIME_S / SAMPLE_TIME_S) + 1
    return [index * SAMPLE_TIME_S for index in range(point_count)]


def run_scenario(
    server: xmlrpc.client.ServerProxy,
    scenario: Scenario,
    times: list[float],
) -> dict[str, list[float]]:
    options = {
        "ModelVars": {
            "Udc_V": 300.0,
            "load_torque_Nm": scenario.load_torque_nm,
            "current_ref_A": scenario.current_ref_a,
        },
        "SolverOpts": {"OutputTimes": times},
    }
    result = server.plecs.simulate(MODEL_NAME, options)
    values = result.get("Values", [])
    result_times = result.get("Time", [])

    # 11 路输出是模型与证据脚本之间的唯一接口，数量不一致时立即停止，避免错列数据继续传播。
    if len(values) != 11 or len(result_times) != len(times):
        raise RuntimeError(
            f"PLECS 输出接口不匹配: signal_rows={len(values)}, "
            f"time_points={len(result_times)}"
        )

    column_names = (
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
    )
    data = {name: list(row) for name, row in zip(column_names, values, strict=True)}
    data["time_s"] = list(result_times)
    data["speed_rpm"] = [value * 60.0 / (2.0 * math.pi) for value in data["speed_rad_s"]]
    return data


def compute_metrics(data: dict[str, list[float]], scenario: Scenario) -> dict[str, float]:
    point_count = len(data["time_s"])
    tail_start = round(point_count * 0.8)
    phase_currents = data["ia_A"] + data["ib_A"] + data["ic_A"]
    tail_speed = data["speed_rad_s"][tail_start:]
    tail_torque = data["electromagnetic_torque_Nm"][tail_start:]
    return {
        "load_torque_Nm": scenario.load_torque_nm,
        "current_ref_A": scenario.current_ref_a,
        "peak_phase_current_A": max(abs(value) for value in phase_currents),
        "tail_speed_mean_rad_s": statistics.fmean(tail_speed),
        "tail_speed_mean_rpm": statistics.fmean(tail_speed) * 60.0 / (2.0 * math.pi),
        "final_speed_rad_s": data["speed_rad_s"][-1],
        "tail_torque_mean_Nm": statistics.fmean(tail_torque),
    }


def evaluate(metrics: dict[str, float], scenario: Scenario) -> tuple[bool, str]:
    peak_current_ok = metrics["peak_phase_current_A"] <= scenario.current_ref_a + 1.2

    if scenario.expected_behavior == "torque_tracking":
        torque_error = abs(metrics["tail_torque_mean_Nm"] - scenario.load_torque_nm)
        speed_ok = metrics["tail_speed_mean_rad_s"] >= 320.0
        ok = peak_current_ok and torque_error <= 0.15 and speed_ok
        reason = (
            f"peak_current_ok={peak_current_ok}; torque_error_Nm={torque_error:.4f}; "
            f"tail_speed_rad_s={metrics['tail_speed_mean_rad_s']:.3f}"
        )
        return ok, reason

    torque_deficit = scenario.load_torque_nm - metrics["tail_torque_mean_Nm"]
    speed_collapsed = metrics["tail_speed_mean_rad_s"] <= 100.0
    ok = peak_current_ok and torque_deficit >= 1.5 and speed_collapsed
    reason = (
        f"peak_current_ok={peak_current_ok}; torque_deficit_Nm={torque_deficit:.4f}; "
        f"tail_speed_rad_s={metrics['tail_speed_mean_rad_s']:.3f}"
    )
    return ok, reason


def write_timeseries(path: Path, data: dict[str, list[float]]) -> None:
    columns = (
        "time_s",
        "ia_A",
        "ib_A",
        "ic_A",
        "ea_V",
        "eb_V",
        "ec_V",
        "speed_rad_s",
        "speed_rpm",
        "electromagnetic_torque_Nm",
        "phase_cmd_a",
        "phase_cmd_b",
        "phase_cmd_c",
    )
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(columns)
        for row_index in range(len(data["time_s"])):
            writer.writerow(data[column][row_index] for column in columns)


def write_summary(path: Path, rows: list[dict[str, object]]) -> None:
    columns = (
        "scenario",
        "load_torque_Nm",
        "current_ref_A",
        "peak_phase_current_A",
        "tail_speed_mean_rad_s",
        "tail_speed_mean_rpm",
        "final_speed_rad_s",
        "tail_torque_mean_Nm",
        "result",
        "reason",
    )
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def write_report(path: Path, rows: list[dict[str, object]], trace_path: Path) -> None:
    lines = [
        "# 第 01 章 PLECS BLDC 基准实验报告",
        "",
        "## 参数摘要",
        "",
        "| 参数 | 数值 | 单位 |",
        "|---|---:|---|",
        "| 直流母线电压 | 300 | V |",
        "| 电流参考 | 5 | A |",
        "| 初始机械角速度 | 300 | rad/s |",
        "| 仿真时长 | 0.3 | s |",
        "| 输出采样间隔 | 0.5 | ms |",
        "",
        "## 场景结果",
        "",
        "| 场景 | 负载转矩/Nm | 相电流峰值/A | 尾段转速/rpm | 尾段电磁转矩/Nm | 结果 |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {scenario} | {load_torque_Nm:.3f} | {peak_phase_current_A:.4f} | "
            "{tail_speed_mean_rpm:.2f} | {tail_torque_mean_Nm:.4f} | {result} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## 判定边界",
            "",
            "- `nominal_load`：电磁转矩跟随 3 Nm 负载，尾段转速保持在 320 rad/s 以上。",
            "- `overload`：6 Nm 负载超过 5 A 电流参考所能提供的转矩，预期现象是电流受限而转速塌落。",
            "- PASS 表示模型出现了场景定义的预期行为；过载场景的 PASS 不表示电机仍能维持转速。",
            "",
            "## 证据来源",
            "",
            f"- PLECS trace：`{trace_path.as_posix()}`",
            "- 逐点数据：`waveforms/01-bldc-control-chain/plecs_*.csv`",
            "- 汇总数据：`waveforms/01-bldc-control-chain/plecs_baseline_summary.csv`",
            "",
            "该模型验证电流换相、三相逆变器、BLDC 电磁模型和机械负载之间的因果链。",
            "速度 PI、Hall 量化、死区、器件损耗和硬件保护不在本实验的判定范围内。",
        ]
    )
    with path.open("w", encoding="utf-8", newline="") as stream:
        stream.write("\r\n".join(lines) + "\r\n")


def main() -> int:
    started_at = time.monotonic()
    paths = project_paths()
    if not paths["model"].is_file():
        print(f"MODEL_MISSING {paths['model']}", file=sys.stderr)
        return 2

    try:
        require_rpc()
    except RuntimeError as exc:
        print(f"PLECS_RPC_NOT_READY {exc}", file=sys.stderr)
        return 2

    paths["results"].mkdir(parents=True, exist_ok=True)
    paths["report"].parent.mkdir(parents=True, exist_ok=True)
    times = output_times()
    server = xmlrpc.client.ServerProxy(
        RPC_URL,
        allow_none=True,
        transport=TimeoutTransport(),
    )
    summary_rows: list[dict[str, object]] = []
    trace_base = paths["results"] / "ch01_bldc_baseline_scope"

    try:
        server.plecs.load(str(paths["model"]))
        server.plecs.scope(f"{MODEL_NAME}/Scope", "ClearTraces")

        for scenario in SCENARIOS:
            scenario_started_at = time.monotonic()
            print(f"PLECS_SCENARIO_START scenario={scenario.name}", flush=True)
            data = run_scenario(server, scenario, times)
            metrics = compute_metrics(data, scenario)
            passed, reason = evaluate(metrics, scenario)
            row: dict[str, object] = {
                "scenario": scenario.name,
                **metrics,
                "result": "PASS" if passed else "FAIL",
                "reason": reason,
            }
            summary_rows.append(row)
            write_timeseries(paths["results"] / f"plecs_{scenario.name}.csv", data)
            server.plecs.scope(f"{MODEL_NAME}/Scope", "HoldTrace", scenario.name)
            print(
                f"PLECS_SCENARIO_DONE scenario={scenario.name} result={row['result']} "
                f"elapsed_s={time.monotonic() - scenario_started_at:.2f}",
                flush=True,
            )

        server.plecs.scope(f"{MODEL_NAME}/Scope", "SaveTraces", str(trace_base))
    except TimeoutError:
        print(
            f"PLECS_RPC_TIMEOUT timeout_s={RPC_TIMEOUT_S}; "
            "请检查 PLECS 是否停在对话框或求解器是否未收敛。",
            file=sys.stderr,
        )
        return 3
    finally:
        try:
            server.plecs.close(MODEL_NAME)
        except Exception:
            pass

    trace_path = trace_base.with_suffix(".trace")
    write_summary(paths["results"] / "plecs_baseline_summary.csv", summary_rows)
    write_report(paths["report"], summary_rows, trace_path.relative_to(paths["root"]))

    passed_count = sum(row["result"] == "PASS" for row in summary_rows)
    print(
        "Generated chapter 01 PLECS baseline. "
        f"scenarios={len(summary_rows)} pass={passed_count} "
        f"time_points={len(times)} signals=11 "
        f"elapsed_s={time.monotonic() - started_at:.2f}"
    )
    return 0 if passed_count == len(summary_rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())

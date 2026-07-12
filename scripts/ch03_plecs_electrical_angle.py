"""运行第 03 章极对数与电角度 PLECS 场景。"""

from __future__ import annotations

import csv
import math
import socket
import statistics
import subprocess
import sys
import xmlrpc.client
from pathlib import Path


MODEL_NAME = "ch03_electrical_angle"
RPC_URL = "http://localhost:1080/RPC2"
SAMPLE_TIME_S = 0.0001
STOP_TIME_S = 0.05
INITIAL_SPEED_RAD_S = 100.0
SCENARIOS = (("one_pole_pair", 1), ("four_pole_pairs", 4))


def project_paths() -> dict[str, Path]:
    root = Path(__file__).resolve().parents[1]
    return {
        "root": root,
        "model": root / "models/plecs/ch03_electrical_angle/ch03_electrical_angle.plecs",
        "waveforms": root / "waveforms/03-electrical-angle",
        "assets": root / "assets/03-electrical-angle",
        "report": root / "reports/03-electrical-angle-test_report.md",
        "capture": root / "scripts/capture_plecs_window.ps1",
    }


def require_rpc() -> None:
    try:
        with socket.create_connection(("localhost", 1080), timeout=2):
            return
    except OSError as exc:
        raise RuntimeError("PLECS RPC 未监听 localhost:1080。") from exc


def run(server: xmlrpc.client.ServerProxy, pole_pairs: int) -> dict[str, list[float]]:
    times = [index * SAMPLE_TIME_S for index in range(round(STOP_TIME_S / SAMPLE_TIME_S) + 1)]
    result = server.plecs.simulate(
        MODEL_NAME,
        {
            "ModelVars": {
                "Udc_V": 300.0,
                "load_torque_Nm": 0.0,
                "current_ref_A": 0.0,
                "initial_speed_rad_s": INITIAL_SPEED_RAD_S,
                "phase_cmd": [0.0, 0.0, 0.0],
                "pole_pairs": pole_pairs,
            },
            "SolverOpts": {"OutputTimes": times},
        },
    )
    values = result.get("Values", [])
    if len(values) != 15 or len(result.get("Time", [])) != len(times):
        raise RuntimeError(f"PLECS 输出接口不匹配: signals={len(values)}")
    names = (
        "ia_A", "ib_A", "ic_A", "ea_V", "eb_V", "ec_V",
        "speed_rad_s", "torque_Nm", "phase_cmd_a", "phase_cmd_b", "phase_cmd_c",
        "vab_V", "vbc_V", "vca_V", "mechanical_angle_rad",
    )
    data = {name: list(row) for name, row in zip(names, values, strict=True)}
    data["time_s"] = list(result["Time"])
    raw_angle = data["mechanical_angle_rad"]
    unwrapped_angle = [raw_angle[0]]
    offset = 0.0
    for previous, current in zip(raw_angle[:-1], raw_angle[1:], strict=True):
        delta = current - previous
        if delta < -math.pi:
            offset += 2 * math.pi
        elif delta > math.pi:
            offset -= 2 * math.pi
        unwrapped_angle.append(current + offset)
    data["mechanical_angle_unwrapped_rad"] = unwrapped_angle
    data["electrical_angle_rad"] = [pole_pairs * value for value in unwrapped_angle]
    data["electrical_angle_wrapped_rad"] = [value % (2 * math.pi) for value in data["electrical_angle_rad"]]
    return data


def write_csv(path: Path, data: dict[str, list[float]]) -> None:
    columns = (
        "time_s", "mechanical_angle_rad", "mechanical_angle_unwrapped_rad", "electrical_angle_rad",
        "electrical_angle_wrapped_rad", "speed_rad_s", "ia_A", "ib_A", "ic_A",
    )
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\r\n")
        writer.writerow(columns)
        for index in range(len(data["time_s"])):
            writer.writerow(data[column][index] for column in columns)


def capture(paths: dict[str, Path]) -> None:
    completed = subprocess.run(
        [
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", str(paths["capture"]),
            "-TitlePattern", f"*{MODEL_NAME}/Scope*",
            "-OutputPath", str(paths["assets"] / "plecs_scope_mechanical_angle.png"),
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())
    print(completed.stdout.strip())


def main() -> int:
    paths = project_paths()
    try:
        require_rpc()
    except RuntimeError as exc:
        print(f"PLECS_RPC_NOT_READY {exc}", file=sys.stderr)
        return 2
    paths["waveforms"].mkdir(parents=True, exist_ok=True)
    paths["assets"].mkdir(parents=True, exist_ok=True)
    server = xmlrpc.client.ServerProxy(RPC_URL, allow_none=True)
    rows: list[dict[str, object]] = []
    try:
        try:
            server.plecs.close(MODEL_NAME)
        except Exception:
            pass
        server.plecs.load(str(paths["model"]))
        for name, pole_pairs in SCENARIOS:
            data = run(server, pole_pairs)
            write_csv(paths["waveforms"] / f"plecs_{name}.csv", data)
            mechanical_delta = data["mechanical_angle_unwrapped_rad"][-1] - data["mechanical_angle_unwrapped_rad"][0]
            electrical_delta = data["electrical_angle_rad"][-1] - data["electrical_angle_rad"][0]
            ratio = electrical_delta / mechanical_delta
            max_current = max(abs(value) for phase in (data["ia_A"], data["ib_A"], data["ic_A"]) for value in phase)
            speed_mean = statistics.fmean(data["speed_rad_s"])
            passed = abs(ratio - pole_pairs) <= 1e-9 and max_current <= 1e-9 and abs(speed_mean - INITIAL_SPEED_RAD_S) <= 0.1
            rows.append({
                "scenario": name,
                "pole_pairs": pole_pairs,
                "mechanical_delta_rad": mechanical_delta,
                "electrical_delta_rad": electrical_delta,
                "angle_ratio": ratio,
                "mean_speed_rad_s": speed_mean,
                "max_phase_current_A": max_current,
                "result": "PASS" if passed else "FAIL",
            })
            if pole_pairs == 4:
                capture(paths)
    finally:
        try:
            server.plecs.close(MODEL_NAME)
        except Exception:
            pass

    summary_path = paths["waveforms"] / "plecs_angle_summary.csv"
    with summary_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys(), lineterminator="\r\n")
        writer.writeheader(); writer.writerows(rows)

    lines = [
        "# 第 03 章机械角与电角度实验报告", "",
        "| 场景 | 极对数 | 机械角增量/rad | 电角增量/rad | 比值 | 平均速度/rad/s | 结果 |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {scenario} | {pole_pairs} | {mechanical_delta_rad:.6f} | "
            "{electrical_delta_rad:.6f} | {angle_ratio:.6f} | {mean_speed_rad_s:.6f} | {result} |".format(**row)
        )
    lines.extend([
        "", "断开三相桥后，PLECS Machine 以 100 rad/s 自由转动。机械角由 PLECS 角度传感器导出，",
        "电角度按机器极对数计算；PASS 要求电角增量与机械角增量之比严格等于极对数，且绕组电流为零。",
    ])
    paths["report"].write_text("\r\n".join(lines) + "\r\n", encoding="utf-8", newline="")
    passed = sum(row["result"] == "PASS" for row in rows)
    print(f"Generated chapter 03 PLECS angle evidence. scenarios={len(rows)} pass={passed} time_points=501 signals=15")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())

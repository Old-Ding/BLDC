"""用第 01 章 PLECS CSV 逐点核对反电动势功率和电磁机械功率。"""

from __future__ import annotations

import csv
import math
import socket
import statistics
import subprocess
import xmlrpc.client
from pathlib import Path


SCENARIOS = ("nominal_load", "overload", "regenerative_braking")


def generate_regenerative_source(root: Path, output_dir: Path) -> Path:
    try:
        with socket.create_connection(("localhost", 1080), timeout=2):
            pass
    except OSError as exc:
        raise RuntimeError("PLECS RPC 未监听 localhost:1080。") from exc

    model = root / "models/plecs/ch01_bldc_baseline/ch01_bldc_baseline.plecs"
    server = xmlrpc.client.ServerProxy("http://localhost:1080/RPC2", allow_none=True)
    model_name = "ch01_bldc_baseline"
    times = [index * 0.0002 for index in range(501)]
    try:
        try:
            server.plecs.close(model_name)
        except Exception:
            pass
        server.plecs.load(str(model))
        result = server.plecs.simulate(
            model_name,
            {
                "ModelVars": {"Udc_V": 300.0, "load_torque_Nm": 0.0, "current_ref_A": -5.0},
                "SolverOpts": {"OutputTimes": times},
            },
        )
        values = result.get("Values", [])
        if len(values) != 11:
            raise RuntimeError(f"PLECS 再生场景输出接口不匹配: signals={len(values)}")
        asset_dir = root / "assets/04-torque-power"
        asset_dir.mkdir(parents=True, exist_ok=True)
        completed = subprocess.run(
            [
                "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                "-File", str(root / "scripts/capture_plecs_window.ps1"),
                "-TitlePattern", "*ch01_bldc_baseline/Scope*",
                "-OutputPath", str(asset_dir / "plecs_scope_regenerative_braking.png"),
            ],
            check=False,
            text=True,
            capture_output=True,
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())
        print(completed.stdout.strip())
    finally:
        try:
            server.plecs.close(model_name)
        except Exception:
            pass

    names = (
        "ia_A", "ib_A", "ic_A", "ea_V", "eb_V", "ec_V", "speed_rad_s",
        "electromagnetic_torque_Nm", "phase_cmd_a", "phase_cmd_b", "phase_cmd_c",
    )
    source = output_dir / "plecs_regenerative_braking_source.csv"
    with source.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\r\n")
        writer.writerow(("time_s", *names))
        for index, current_time in enumerate(result["Time"]):
            writer.writerow((current_time, *(row[index] for row in values)))
    return source


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    source_dir = root / "waveforms/01-bldc-control-chain"
    output_dir = root / "waveforms/04-torque-power"
    report_path = root / "reports/04-torque-power-test_report.md"
    output_dir.mkdir(parents=True, exist_ok=True)
    regenerative_source = generate_regenerative_source(root, output_dir)
    rows: list[dict[str, object]] = []

    for scenario in SCENARIOS:
        source = regenerative_source if scenario == "regenerative_braking" else source_dir / f"plecs_{scenario}.csv"
        with source.open("r", encoding="utf-8", newline="") as stream:
            source_rows = list(csv.DictReader(stream))
        enriched: list[dict[str, float]] = []
        residuals: list[float] = []
        electrical_power: list[float] = []
        mechanical_power: list[float] = []
        for source_row in source_rows:
            pa = float(source_row["ea_V"]) * float(source_row["ia_A"])
            pb = float(source_row["eb_V"]) * float(source_row["ib_A"])
            pc = float(source_row["ec_V"]) * float(source_row["ic_A"])
            pe = pa + pb + pc
            pm = float(source_row["electromagnetic_torque_Nm"]) * float(source_row["speed_rad_s"])
            residual = pe - pm
            residuals.append(residual)
            electrical_power.append(pe)
            mechanical_power.append(pm)
            enriched.append({
                "time_s": float(source_row["time_s"]),
                "ia_A": float(source_row["ia_A"]),
                "ib_A": float(source_row["ib_A"]),
                "ic_A": float(source_row["ic_A"]),
                "ea_V": float(source_row["ea_V"]),
                "eb_V": float(source_row["eb_V"]),
                "ec_V": float(source_row["ec_V"]),
                "phase_a_power_W": pa,
                "phase_b_power_W": pb,
                "phase_c_power_W": pc,
                "electrical_conversion_power_W": pe,
                "speed_rad_s": float(source_row["speed_rad_s"]),
                "electromagnetic_torque_Nm": float(source_row["electromagnetic_torque_Nm"]),
                "mechanical_power_W": pm,
                "power_residual_W": residual,
            })

        output = output_dir / f"plecs_power_{scenario}.csv"
        with output.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=enriched[0].keys(), lineterminator="\r\n")
            writer.writeheader(); writer.writerows(enriched)

        tail = max(1, round(len(enriched) * 0.2))
        residual_rms = math.sqrt(statistics.fmean(value * value for value in residuals))
        max_residual = max(abs(value) for value in residuals)
        power_scale = max(max(abs(value) for value in electrical_power), 1.0)
        tail_torque = statistics.fmean(row["electromagnetic_torque_Nm"] for row in enriched[-tail:])
        tail_speed = statistics.fmean(row["speed_rad_s"] for row in enriched[-tail:])
        tail_power = statistics.fmean(electrical_power[-tail:])
        sign_ok = True
        if scenario == "regenerative_braking":
            sign_ok = tail_torque <= -2.0 and tail_speed >= 50.0 and tail_power <= -100.0
        passed = max_residual <= 1e-9 * power_scale and sign_ok
        rows.append({
            "scenario": scenario,
            "time_points": len(enriched),
            "tail_electrical_power_W": statistics.fmean(electrical_power[-tail:]),
            "tail_mechanical_power_W": statistics.fmean(mechanical_power[-tail:]),
            "residual_rms_W": residual_rms,
            "max_abs_residual_W": max_residual,
            "tail_torque_Nm": tail_torque,
            "tail_speed_rad_s": tail_speed,
            "result": "PASS" if passed else "FAIL",
        })

    with (output_dir / "plecs_power_summary.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys(), lineterminator="\r\n")
        writer.writeheader(); writer.writerows(rows)

    lines = [
        "# 第 04 章反电动势功率与电磁转矩核对报告", "",
        "| 场景 | 点数 | 尾段 e*i 功率/W | 尾段 Te*omega 功率/W | 尾段转矩/Nm | 尾段速度/rad/s | 最大绝对残差/W | 结果 |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {scenario} | {time_points} | {tail_electrical_power_W:.9f} | "
            "{tail_mechanical_power_W:.9f} | {tail_torque_Nm:.6f} | "
            "{tail_speed_rad_s:.6f} | {max_abs_residual_W:.3e} | {result} |".format(**row)
        )
    lines.extend([
        "", "逐点判定使用 `ea*ia + eb*ib + ec*ic = Te*omega`。",
        "该等式核对 PLECS BLDC Machine 的电磁能量转换，不包含逆变器导通损耗、开关损耗和机械摩擦损耗。",
    ])
    report_path.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8", newline="")
    passed = sum(row["result"] == "PASS" for row in rows)
    print(f"Generated chapter 04 power check. scenarios={len(rows)} pass={passed} source=PLECS time_points={sum(int(row['time_points']) for row in rows)}")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())

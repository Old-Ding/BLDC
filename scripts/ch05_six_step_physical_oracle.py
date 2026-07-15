"""生成第 05 章六步表的测试侧物理 oracle。

物理 oracle 的期望只来自电角扇区和反电动势极性，不从运行时
C 表推导。脚本读取 C 表只作为被测对象，并用独立期望逐扇区
检查它是否能产生目标驱动方向的正电磁功率。
"""

from __future__ import annotations

import csv
import math
import re
from dataclasses import dataclass
from pathlib import Path


PHASES = ("A", "B", "C")


@dataclass(frozen=True)
class SectorOracle:
    sector: int
    angle_start_deg: float
    angle_end_deg: float

    @property
    def angle_range_deg(self) -> str:
        return f"[{int(self.angle_start_deg)}, {int(self.angle_end_deg)})"

    @property
    def angle_center_deg(self) -> float:
        return 0.5 * (self.angle_start_deg + self.angle_end_deg)

    @property
    def bemf(self) -> dict[str, float]:
        theta = math.radians(self.angle_center_deg)
        return {
            "A": trapezoid_bemf(theta),
            "B": trapezoid_bemf(theta - 2.0 * math.pi / 3.0),
            "C": trapezoid_bemf(theta + 2.0 * math.pi / 3.0),
        }

    @property
    def positive_bemf_phase(self) -> str:
        return max(PHASES, key=lambda phase: self.bemf[phase])

    @property
    def negative_bemf_phase(self) -> str:
        return min(PHASES, key=lambda phase: self.bemf[phase])

    @property
    def floating_phase(self) -> str:
        return min(PHASES, key=lambda phase: abs(self.bemf[phase]))

    @property
    def expected_state(self) -> tuple[int, int, int]:
        state = {phase: 0 for phase in PHASES}
        state[self.positive_bemf_phase] = 1
        state[self.negative_bemf_phase] = -1
        return tuple(state[phase] for phase in PHASES)

    def normalized_power(self, state: tuple[int, int, int]) -> float:
        current = current_from_bridge_state(state)
        return sum(self.bemf[phase] * current[phase] for phase in PHASES)

    @property
    def expected_power(self) -> float:
        return self.normalized_power(self.expected_state)


SECTORS = (
    SectorOracle(0, 0.0, 60.0),
    SectorOracle(1, 60.0, 120.0),
    SectorOracle(2, 120.0, 180.0),
    SectorOracle(3, 180.0, 240.0),
    SectorOracle(4, 240.0, 300.0),
    SectorOracle(5, 300.0, 360.0),
)


def trapezoid_bemf(theta_rad: float) -> float:
    """解析梯形反电动势；零点只定义相位基准，不读取换相表。"""
    theta_deg = math.degrees(theta_rad) % 360.0
    if theta_deg < 120.0:
        return 1.0
    if theta_deg < 180.0:
        return 1.0 - (theta_deg - 120.0) / 30.0
    if theta_deg < 300.0:
        return -1.0
    return -1.0 + (theta_deg - 300.0) / 30.0


def current_from_bridge_state(state: tuple[int, int, int]) -> dict[str, int]:
    high = [phase for phase, value in zip(PHASES, state) if value > 0]
    low = [phase for phase, value in zip(PHASES, state) if value < 0]
    floating = [phase for phase, value in zip(PHASES, state) if value == 0]
    if len(high) != 1 or len(low) != 1 or len(floating) != 1:
        return {phase: 0 for phase in PHASES}
    current = {phase: 0 for phase in PHASES}
    current[high[0]] = 1
    current[low[0]] = -1
    return current


def state_text(state: tuple[int, int, int]) -> str:
    return " ".join(str(value) for value in state)


def current_text(state: tuple[int, int, int]) -> str:
    current = current_from_bridge_state(state)
    return " ".join(str(current[phase]) for phase in PHASES)


def bemf_text(sector: SectorOracle) -> str:
    return " ".join(f"{sector.bemf[phase]:.0f}" for phase in PHASES)


def parse_actual_forward_table(source_path: Path) -> list[tuple[int, int, int]]:
    text = source_path.read_text(encoding="utf-8")
    match = re.search(
        r"static\s+const\s+BldcPhaseCommand\s+forward\s*\[\s*6\s*\]\s*=\s*\{(?P<body>.*?)\};",
        text,
        re.DOTALL,
    )
    if not match:
        raise ValueError(f"forward[6] table not found in {source_path}")

    triples = re.findall(r"\{\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*\}", match.group("body"))
    if len(triples) != 6:
        raise ValueError(f"expected 6 forward table rows in {source_path}, found {len(triples)}")

    states: list[tuple[int, int, int]] = []
    for index, triple in enumerate(triples):
        state = tuple(int(value) for value in triple)
        if sorted(state) != [-1, 0, 1]:
            raise ValueError(f"forward[{index}] is not a two-phase six-step state: {state}")
        states.append(state)
    return states


def swap_ab(state: tuple[int, int, int]) -> tuple[int, int, int]:
    return (state[1], state[0], state[2])


def inverted_direction(state: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple(-value for value in state)


def mutation_rows(actual: list[tuple[int, int, int]]) -> list[dict[str, object]]:
    mutations = {
        "sector_shift_plus_60deg": actual[1:] + actual[:1],
        "phase_label_swap_A_B": [swap_ab(state) for state in actual],
        "direction_inverted": [inverted_direction(state) for state in actual],
    }
    rows: list[dict[str, object]] = []
    for name, states in mutations.items():
        mismatched_sector_ids: list[str] = []
        non_positive_power_sector_ids: list[str] = []
        below_expected_power_sector_ids: list[str] = []
        for oracle, state in zip(SECTORS, states):
            if state != oracle.expected_state:
                mismatched_sector_ids.append(str(oracle.sector))
            power = oracle.normalized_power(state)
            if power <= 0:
                non_positive_power_sector_ids.append(str(oracle.sector))
            if power < oracle.expected_power - 1e-9:
                below_expected_power_sector_ids.append(str(oracle.sector))
        rows.append(
            {
                "mutation": name,
                "mismatched_sectors": len(mismatched_sector_ids),
                "mismatched_sector_ids": " ".join(mismatched_sector_ids) if mismatched_sector_ids else "-",
                "below_expected_power_sectors": len(below_expected_power_sector_ids),
                "below_expected_power_sector_ids": " ".join(below_expected_power_sector_ids)
                if below_expected_power_sector_ids
                else "-",
                "non_positive_power_sectors": len(non_positive_power_sector_ids),
                "non_positive_power_sector_ids": " ".join(non_positive_power_sector_ids)
                if non_positive_power_sector_ids
                else "-",
                "result": "FAIL_DETECTED"
                if mismatched_sector_ids or below_expected_power_sector_ids or non_positive_power_sector_ids
                else "UNDETECTED",
            }
        )
    return rows


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    wave_dir = root / "waveforms" / "05-six-step-sequence"
    report_dir = root / "reports"
    wave_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    actual_states = parse_actual_forward_table(root / "src" / "bldc_six_step.c")
    oracle_rows = []
    for sector, actual in zip(SECTORS, actual_states):
        expected = sector.expected_state
        actual_power = sector.normalized_power(actual)
        state_match = expected == actual
        power_positive = actual_power > 0
        power_full = abs(actual_power - sector.expected_power) < 1e-9
        oracle_rows.append(
            {
                "sector": sector.sector,
                "electrical_angle_range_deg": sector.angle_range_deg,
                "bemf_abc_at_sector_center": bemf_text(sector),
                "positive_bemf_phase": sector.positive_bemf_phase,
                "negative_bemf_phase": sector.negative_bemf_phase,
                "floating_phase": sector.floating_phase,
                "expected_phase_state_abc": state_text(expected),
                "actual_phase_state_abc": state_text(actual),
                "actual_current_abc": current_text(actual),
                "expected_normalized_ei_power": f"{sector.expected_power:.0f}",
                "actual_normalized_ei_power": actual_power,
                "state_match": "PASS" if state_match else "FAIL",
                "power_positive": "PASS" if power_positive else "FAIL",
                "power_full": "PASS" if power_full else "FAIL",
                "result": "PASS" if state_match and power_positive and power_full else "FAIL",
            }
        )

    mutation_check_rows = mutation_rows(actual_states)

    oracle_csv = wave_dir / "six_step_physical_oracle.csv"
    with oracle_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(oracle_rows[0].keys()), lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(oracle_rows)

    mutation_csv = wave_dir / "six_step_oracle_mutations.csv"
    with mutation_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(mutation_check_rows[0].keys()), lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(mutation_check_rows)

    all_table_rows_pass = all(row["result"] == "PASS" for row in oracle_rows)
    all_mutations_detected = all(row["result"] == "FAIL_DETECTED" for row in mutation_check_rows)

    lines = [
        "# 第 05 章六步表物理 oracle 报告",
        "",
        "物理 oracle 的期望不从 `src/bldc_six_step.c` 生成。脚本先用解析梯形反电动势波形在每个 60 度电角扇区中心建立相位符号，再用理想两相导通桥臂/绕组电流路径计算 `sum(e*i)`；读取 C 表只作为被测对象。",
        "",
        "## 1. 扇区物理推导与 C 表对照",
        "",
        "| 扇区 | 电角范围/deg | 扇区中心 eA/eB/eC | 反电动势正相 | 反电动势负相 | 悬空相 | 期望 A/B/C | C 表 A/B/C | C 表电流 A/B/C | 期望 e*i | C 表 e*i | 状态匹配 | 功率方向 | 满功率 | 结果 |",
        "|---:|---|---|---|---|---|---|---|---|---:|---:|---|---|---|---|",
    ]
    for row in oracle_rows:
        lines.append(
            "| {sector} | `{electrical_angle_range_deg}` | `{bemf_abc_at_sector_center}` | "
            "{positive_bemf_phase} | {negative_bemf_phase} | {floating_phase} | "
            "`{expected_phase_state_abc}` | `{actual_phase_state_abc}` | `{actual_current_abc}` | "
            "{expected_normalized_ei_power} | {actual_normalized_ei_power:.0f} | "
            "{state_match} | {power_positive} | {power_full} | {result} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## 2. Mutation 检查",
            "",
            "| Mutation | 不匹配扇区数 | 不匹配扇区 | 低于期望功率扇区数 | 低于期望功率扇区 | 非正功率扇区数 | 非正功率扇区 | 结果 |",
            "|---|---:|---|---:|---|---:|---|---|",
        ]
    )
    for row in mutation_check_rows:
        lines.append(
            "| {mutation} | {mismatched_sectors} | {mismatched_sector_ids} | "
            "{below_expected_power_sectors} | {below_expected_power_sector_ids} | "
            "{non_positive_power_sectors} | {non_positive_power_sector_ids} | {result} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## 3. 结论",
            "",
            f"- C 表逐扇区匹配独立物理 oracle：{'PASS' if all_table_rows_pass else 'FAIL'}。",
            f"- 三类同源一致性错误检测：{'PASS' if all_mutations_detected else 'FAIL'}。",
        ]
    )
    report_path = report_dir / "05-six-step-physical-oracle.md"
    report_path.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8", newline="")

    print(
        "Generated chapter 05 physical oracle. "
        f"sectors={len(oracle_rows)} c_table_match={all_table_rows_pass} "
        f"mutations_detected={all_mutations_detected}"
    )
    return 0 if all_table_rows_pass and all_mutations_detected else 1


if __name__ == "__main__":
    raise SystemExit(main())

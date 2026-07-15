"""生成第 09 章 Hall 合法转移与故障分类契约。"""

from __future__ import annotations

import csv
from pathlib import Path


SEQUENCE = (5, 1, 3, 2, 6, 4)
INVALID_CODES = {0, 7}


def classify_transition(previous: int, current: int) -> tuple[str, str]:
    if previous in INVALID_CODES or current in INVALID_CODES:
        return "FAULT", "invalid_code"
    if previous not in SEQUENCE or current not in SEQUENCE:
        return "FAULT", "unknown_code"
    delta = (SEQUENCE.index(current) - SEQUENCE.index(previous)) % 6
    if delta == 1:
        return "FORWARD", "adjacent"
    if delta == 5:
        return "REVERSE", "adjacent"
    if delta == 0:
        return "HOLD", "same_sector"
    return "FAULT", "non_adjacent_legal_jump"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    wave_dir = root / "waveforms" / "09-hall-sequence"
    report_dir = root / "reports"
    wave_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    cases = [
        ("forward_5_to_1", 5, 1, "FORWARD", "adjacent"),
        ("reverse_5_to_4", 5, 4, "REVERSE", "adjacent"),
        ("hold_5_to_5", 5, 5, "HOLD", "same_sector"),
        ("invalid_000", 5, 0, "FAULT", "invalid_code"),
        ("invalid_111", 5, 7, "FAULT", "invalid_code"),
        ("non_adjacent_5_to_3", 5, 3, "FAULT", "non_adjacent_legal_jump"),
    ]

    rows = []
    for name, previous, current, expected_class, expected_reason in cases:
        actual_class, actual_reason = classify_transition(previous, current)
        rows.append(
            {
                "case": name,
                "previous_hall_code": previous,
                "current_hall_code": current,
                "expected_class": expected_class,
                "actual_class": actual_class,
                "expected_reason": expected_reason,
                "actual_reason": actual_reason,
                "result": "PASS"
                if actual_class == expected_class and actual_reason == expected_reason
                else "FAIL",
            }
        )

    csv_path = wave_dir / "hall_transition_oracle.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# 第 09 章 Hall 转移 oracle 报告",
        "",
        "Hall 解码层只负责把当前码和上一次码分类为相邻正转、相邻反转、保持或故障。换相安全层只消费故障标志并执行全关，不重复判断 Hall 码。",
        "",
        "| 用例 | 上一码 | 当前码 | 期望分类 | 实际分类 | 期望原因 | 实际原因 | 结果 |",
        "|---|---:|---:|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {case} | {previous_hall_code} | {current_hall_code} | {expected_class} | "
            "{actual_class} | {expected_reason} | {actual_reason} | {result} |".format(**row)
        )
    report_path = report_dir / "09-hall-transition-contract.md"
    report_path.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8", newline="")

    passed = sum(row["result"] == "PASS" for row in rows)
    print(f"Generated Hall transition oracle. cases={len(rows)} pass={passed}")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())

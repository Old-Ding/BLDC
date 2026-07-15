"""检查 Hall 测速只消费合法相邻转移，并覆盖极对数、非法码和超时恢复。"""

from __future__ import annotations

import csv
import math
from pathlib import Path


SEQUENCE = (5, 1, 3, 2, 6, 4)
TIMEOUT_S = 0.05
ALPHA = 0.25


def classify_transition(previous_code: int | None, code: int) -> tuple[str, int]:
    if code not in SEQUENCE:
        return "invalid_code", 0
    if previous_code is None:
        return "first_valid", 0
    if code == previous_code:
        return "hold", 0
    delta = (SEQUENCE.index(code) - SEQUENCE.index(previous_code)) % 6
    if delta == 1:
        return "legal_forward", 1
    if delta == 5:
        return "legal_reverse", -1
    return "non_adjacent", 0


def estimate_events(samples: list[tuple[float, int]], pole_pairs: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    previous_valid_code: int | None = None
    last_edge_time: float | None = None
    raw_speed = 0.0
    filtered_speed = 0.0
    legal_edge_count = 0
    timed_out_active = False

    for time_s, code in samples:
        transition_class, direction = classify_transition(previous_valid_code, code)
        legal_event = transition_class in {"legal_forward", "legal_reverse"}

        if legal_event:
            if timed_out_active or last_edge_time is None:
                raw_speed = 0.0
                filtered_speed = 0.0
            else:
                delta_t = time_s - last_edge_time
                raw_speed = direction * (math.pi / 3.0) / (pole_pairs * delta_t)
                filtered_speed = raw_speed if legal_edge_count <= 1 else ALPHA * raw_speed + (1 - ALPHA) * filtered_speed
            last_edge_time = time_s
            previous_valid_code = code
            legal_edge_count += 1
            timed_out_active = False
        elif transition_class == "first_valid":
            previous_valid_code = code

        timeout = (
            last_edge_time is None and time_s >= TIMEOUT_S
        ) or (
            last_edge_time is not None and time_s - last_edge_time >= TIMEOUT_S
        )
        if timeout:
            # 超时只由测速层清速度；它不把非法码或非相邻跳码升级成测速事件。
            raw_speed = 0.0
            filtered_speed = 0.0
            timed_out_active = True

        rows.append({
            "time_s": time_s,
            "hall_code": code,
            "pole_pairs": pole_pairs,
            "transition_class": transition_class,
            "direction": direction,
            "legal_event": int(legal_event),
            "legal_edge_count": legal_edge_count,
            "timeout": int(timeout),
            "raw_speed_rad_s": raw_speed,
            "filtered_speed_rad_s": filtered_speed,
        })
    return rows


CASES = {
    "pole_pairs_1_forward": {
        "pole_pairs": 1,
        "samples": [(0.00, 5), (0.01, 1), (0.02, 3)],
        "expected_last_speed": 104.719755,
        "expected_edges": 2,
        "expected_last_class": "legal_forward",
    },
    "pole_pairs_4_forward": {
        "pole_pairs": 4,
        "samples": [(0.00, 5), (0.01, 1), (0.02, 3)],
        "expected_last_speed": 26.179939,
        "expected_edges": 2,
        "expected_last_class": "legal_forward",
    },
    "reverse": {
        "pole_pairs": 1,
        "samples": [(0.00, 5), (0.01, 4), (0.02, 6)],
        "expected_last_speed": -104.719755,
        "expected_edges": 2,
        "expected_last_class": "legal_reverse",
    },
    "invalid_ignored": {
        "pole_pairs": 1,
        "samples": [(0.00, 5), (0.01, 0), (0.02, 1), (0.03, 3)],
        "expected_last_speed": 104.719755,
        "expected_edges": 2,
        "expected_last_class": "legal_forward",
    },
    "non_adjacent_ignored": {
        "pole_pairs": 1,
        "samples": [(0.00, 5), (0.01, 3), (0.02, 1), (0.03, 3)],
        "expected_last_speed": 104.719755,
        "expected_edges": 2,
        "expected_last_class": "legal_forward",
    },
    "hold_ignored": {
        "pole_pairs": 1,
        "samples": [(0.00, 5), (0.01, 5), (0.02, 1), (0.03, 3)],
        "expected_last_speed": 104.719755,
        "expected_edges": 2,
        "expected_last_class": "legal_forward",
    },
    "timeout_recovery": {
        "pole_pairs": 1,
        "samples": [(0.00, 5), (0.01, 1), (0.07, 1), (0.08, 3), (0.09, 2)],
        "expected_last_speed": 104.719755,
        "expected_edges": 3,
        "expected_last_class": "legal_forward",
    },
}


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    wave = root / "waveforms" / "12-hall-speed"
    wave.mkdir(parents=True, exist_ok=True)
    all_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []

    for case_name, case in CASES.items():
        event_rows = estimate_events(case["samples"], int(case["pole_pairs"]))
        for row in event_rows:
            all_rows.append({"case": case_name, **row})
        last = event_rows[-1]
        speed_ok = abs(float(last["raw_speed_rad_s"]) - float(case["expected_last_speed"])) < 1e-3
        edges_ok = int(last["legal_edge_count"]) == int(case["expected_edges"])
        class_ok = str(last["transition_class"]) == str(case["expected_last_class"])
        summary_rows.append({
            "case": case_name,
            "pole_pairs": case["pole_pairs"],
            "last_transition_class": last["transition_class"],
            "legal_edge_count": last["legal_edge_count"],
            "last_raw_speed_rad_s": last["raw_speed_rad_s"],
            "expected_raw_speed_rad_s": case["expected_last_speed"],
            "result": "PASS" if speed_ok and edges_ok and class_ok else "FAIL",
        })

    events_csv = wave / "hall_speed_event_oracle.csv"
    with events_csv.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=all_rows[0].keys(), lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(all_rows)

    summary_csv = wave / "hall_speed_event_oracle_summary.csv"
    with summary_csv.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=summary_rows[0].keys(), lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(summary_rows)

    lines = [
        "# 第 12 章 Hall 测速事件 oracle",
        "",
        "| 用例 | 极对数 | 最后转移分类 | 合法边沿数 | 实测末值/rad/s | 期望末值/rad/s | 结果 |",
        "|---|---:|---|---:|---:|---:|---|",
    ]
    for row in summary_rows:
        lines.append(
            "| {case} | {pole_pairs} | {last_transition_class} | {legal_edge_count} | "
            "{last_raw_speed_rad_s:.6f} | {expected_raw_speed_rad_s:.6f} | {result} |".format(**row)
        )
    lines.extend([
        "",
        "## 责任边界",
        "",
        "Hall 解码只把相邻合法跳变交给测速；`invalid_code`、`non_adjacent` 和 `hold` 不更新测速基准。",
        "测速层使用 `omega_m = s * (pi/3)/(pole_pairs * delta_t)`，因此同一 Hall 边沿间隔在 4 极对时机械速度是 1 极对的四分之一。",
    ])
    report = root / "reports" / "12-hall-speed-event-oracle.md"
    report.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8", newline="")

    passed = all(row["result"] == "PASS" for row in summary_rows)
    print(f"Generated C12 Hall-speed event oracle. cases={len(summary_rows)} pass={passed}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

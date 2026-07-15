# 第 09 章 Hall 转移 oracle 报告

Hall 解码层只负责把当前码和上一次码分类为相邻正转、相邻反转、保持或故障。换相安全层只消费故障标志并执行全关，不重复判断 Hall 码。

| 用例 | 上一码 | 当前码 | 期望分类 | 实际分类 | 期望原因 | 实际原因 | 结果 |
|---|---:|---:|---|---|---|---|---|
| forward_5_to_1 | 5 | 1 | FORWARD | FORWARD | adjacent | adjacent | PASS |
| reverse_5_to_4 | 5 | 4 | REVERSE | REVERSE | adjacent | adjacent | PASS |
| hold_5_to_5 | 5 | 5 | HOLD | HOLD | same_sector | same_sector | PASS |
| invalid_000 | 5 | 0 | FAULT | FAULT | invalid_code | invalid_code | PASS |
| invalid_111 | 5 | 7 | FAULT | FAULT | invalid_code | invalid_code | PASS |
| non_adjacent_5_to_3 | 5 | 3 | FAULT | FAULT | non_adjacent_legal_jump | non_adjacent_legal_jump | PASS |

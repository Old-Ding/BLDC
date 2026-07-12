# 第 09 章 Hall 序列 PLECS 报告

| 场景 | 跳变数 | 观测序列 | 方向 | 非法采样数 | 结果 |
|---|---:|---|---|---:|---|
| forward | 6 | 5-1-3-2-6-4-5 | forward | 0 | PASS |
| reverse | 7 | 5-4-6-2-3-1-5-4 | reverse | 0 | PASS |
| invalid_000 | 0 | 0 | invalid | 701 | PASS |
| invalid_111 | 0 | 7 | invalid | 701 | PASS |

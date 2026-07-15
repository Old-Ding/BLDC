# 第 14 章完整闭环验收检查

本检查只读取 C14 PLECS CSV 中已经原生导出的 Hall/control/gate 字段；若缺少这些列，检查直接失败。

| 场景 | 尾段误差/rad/s | Hall 偏差/rad/s | 起动到 50/s | 阶跃后到 55/s | 高限幅占比 | 全关占比 | Hall fault 占比 | Hall enable 尾段占比 | Hall 边沿数 | 峰值电流/A | 结果 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| zero_speed_start | 2.166 | 0.488 | 0.01211 | -1.00000 | 0.000 | 0.000 | 0.000 | 1.000 | 27 | 27.886 | PASS |
| target_step | 1.958 | 0.243 | 0.01347 | 0.09527 | 0.000 | 0.000 | 0.000 | 1.000 | 26 | 12.035 | PASS |
| load_step | 6.516 | 0.840 | 0.00940 | -1.00000 | 0.947 | 0.000 | 0.000 | 1.000 | 25 | 14.443 | PASS |
| invalid_hall | 1.988 | 0.842 | 0.00940 | -1.00000 | 0.000 | 1.000 | 0.040 | 1.000 | 19 | 12.650 | PASS |
| overload | 20.718 | 0.057 | 0.00940 | -1.00000 | 0.947 | 0.000 | 0.000 | 1.000 | 20 | 27.800 | PASS |

## 失败样本谓词

| 失败样本 | 对应场景 | 结果 |
|---|---|---|
| startup_failure | zero_speed_start | FAIL_DETECTED |
| steady_error_over_limit | target_step | FAIL_DETECTED |
| load_recovery_timeout | load_step | FAIL_DETECTED |
| invalid_hall_not_all_off | invalid_hall | FAIL_DETECTED |
| overload_misclassified | overload | FAIL_DETECTED |

## 证据边界

- Hall A/B/C、Hall code、decoded sector、fault、enable 和六路 gate 均来自 C14 PLECS CSV 原生列。
- 本脚本只复核字段完整性、验收谓词和失败样本，不从机械角重建被测 Hall 结果。

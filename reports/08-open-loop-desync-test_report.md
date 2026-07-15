# 第 08 章开环失步诊断 PLECS 报告

本报告使用同一组 PLECS 输出量和同一分类器，同时覆盖同步跟随正例、加速过快失步和负载扰动失步。

| 场景 | 角色 | 最终电频率/Hz | 尾段平均速度/rad/s | 速度比 | 累计滑移/圈 | 负转矩占比 | 尾段转矩/N m | 分类 | 结果 |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| sync_follow | sync_positive | 10.000 | 60.045 | 0.9556 | 0.096 | 0.589 | -0.015 | SYNC_FOLLOW_CONFIRMED | PASS |
| gentle_ramp | mild_desync | 25.000 | 13.900 | 0.0885 | 3.854 | 0.529 | 3.508 | DESYNC_CONFIRMED | PASS |
| overfast_ramp | overfast_desync | 80.000 | 0.077 | 0.0002 | 22.921 | 0.508 | -0.026 | DESYNC_CONFIRMED | PASS |
| load_step | load_desync | 25.000 | 13.930 | 0.0887 | 4.140 | 0.421 | 6.551 | DESYNC_CONFIRMED | PASS |

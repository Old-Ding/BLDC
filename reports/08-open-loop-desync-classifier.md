# 第 08 章同步/失步分类离线检查

本检查不生成新的 PLECS 波形。它复用同一个同步/失步分类函数，重读信号级参考和 C08 PLECS summary，确认同步正例与失步场景的判据一致。

| 场景 | 来源 | 速度比 | 累计滑移/圈 | 负转矩占比 | 期望分类 | 实际分类 | 结果 |
|---|---|---:|---:|---:|---|---|---|
| signal_locked_reference | signal_fixture | 0.9800 | 0.040 | 0.060 | SYNC_FOLLOW_CONFIRMED | SYNC_FOLLOW_CONFIRMED | PASS |
| sync_follow | plecs_csv | 0.9556 | 0.096 | 0.589 | SYNC_FOLLOW_CONFIRMED | SYNC_FOLLOW_CONFIRMED | PASS |
| gentle_ramp | plecs_csv | 0.0885 | 3.854 | 0.529 | DESYNC_CONFIRMED | DESYNC_CONFIRMED | PASS |
| overfast_ramp | plecs_csv | 0.0002 | 22.921 | 0.508 | DESYNC_CONFIRMED | DESYNC_CONFIRMED | PASS |
| load_step | plecs_csv | 0.0887 | 4.140 | 0.421 | DESYNC_CONFIRMED | DESYNC_CONFIRMED | PASS |

## 证据边界

- `signal_locked_reference` 只证明阈值能识别一个有界滑移的同步信号夹具，不是 PLECS 电机仿真。
- `sync_follow` 来自 PLECS CSV，和三个失步场景使用同一分类函数。
- 速度比和累计滑移是同步/失步主判据；负转矩占比只辅助观察转矩脉动，不单独否决同步。

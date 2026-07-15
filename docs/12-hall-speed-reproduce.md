# 第 12 篇复现说明：Hall 边沿测速

```powershell
Set-Location .\BLDC
python .\scripts\build_ch12_plecs_model.py
python .\scripts\ch12_plecs_hall_speed.py
python .\scripts\ch12_hall_speed_event_oracle.py
matlab -batch "run('scripts/ch12_hall_speed_postprocess.m')"
```

PLECS 可用时，脚本会运行 6 个场景，其中 `medium_100_pp4` 用于 4 极对测速。期望输出 `scenarios=6 pass=6 time_points=2501 signals=27`；离线事件 oracle 期望 `cases=7 pass=True`。采样间隔 100 μs，滤波系数 0.25，超时 50 ms。

PLECS CSV 原生导出 `hall_code`、`hall_transition_class`、`hall_legal_event`、`speed_raw_rad_s`、`speed_filtered_rad_s`、`timeout` 和 `legal_edge_count`。Python 脚本只负责导出 CSV、检查 Hall 位与 code 一致、汇总指标。

| 生成物 | 路径 |
|---|---|
| 模型 | `models/plecs/ch12_hall_speed/ch12_hall_speed.plecs` |
| CSV | `waveforms/12-hall-speed/plecs_*.csv` |
| 汇总 | `waveforms/12-hall-speed/plecs_hall_speed_summary.csv` |
| 事件 oracle | `waveforms/12-hall-speed/hall_speed_event_oracle.csv`、`waveforms/12-hall-speed/hall_speed_event_oracle_summary.csv` |
| PLECS Scope | `assets/12-hall-speed/plecs_scope_hall_edges_fast.png` |
| MATLAB 图 | `assets/12-hall-speed/hall_speed_quantization_timeout.png` |
| 报告 | `reports/12-hall-speed-test_report.md`、`reports/12-hall-speed-event-oracle.md` |

若高速场景实际均值不是 400 rad/s，应以 CSV 的 PLECS 实际速度为真值，不能把初始条件当成全程恒速。

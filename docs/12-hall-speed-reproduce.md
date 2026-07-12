# 第 12 篇复现说明：Hall 边沿测速

```powershell
Set-Location .\BLDC
python .\scripts\build_ch12_plecs_model.py
python .\scripts\ch12_plecs_hall_speed.py
matlab -batch "run('scripts/ch12_hall_speed_postprocess.m')"
```

期望 `scenarios=5 pass=5 time_points=2501 signals=19`。采样间隔 100 μs，滤波系数 0.25，超时 50 ms。

| 生成物 | 路径 |
|---|---|
| 模型 | `models/plecs/ch12_hall_speed/ch12_hall_speed.plecs` |
| CSV | `waveforms/12-hall-speed/plecs_*.csv` |
| 汇总 | `waveforms/12-hall-speed/plecs_hall_speed_summary.csv` |
| PLECS Scope | `assets/12-hall-speed/plecs_scope_hall_edges_fast.png` |
| MATLAB 图 | `assets/12-hall-speed/hall_speed_quantization_timeout.png` |
| 报告 | `reports/12-hall-speed-test_report.md` |

若高速场景实际均值不是 400 rad/s，应以 CSV 的 PLECS 实际速度为真值，不能把初始条件当成全程恒速。

# 第 09 篇复现说明：Hall 序列、方向与非法码

```powershell
Set-Location .\BLDC
python .\scripts\build_ch09_plecs_model.py
python .\scripts\ch09_plecs_hall_sequence.py
matlab -batch "run('scripts/ch09_hall_postprocess.m')"
```

期望 `scenarios=4 pass=4 time_points=701 signals=19`。

正反转场景使用 `300 V` 母线、桥臂全关、初始速度 `±100 rad/s`，避免低母线下反电动势经二极管回灌造成再生制动。非法场景由模型参数整段强制 `000/111`，目的是隔离码值检查；状态跳变故障留到后续固件测试。

| 生成物 | 路径 |
|---|---|
| PLECS 模型 | `models/plecs/ch09_hall_sequence/ch09_hall_sequence.plecs` |
| 原始 CSV | `waveforms/09-hall-sequence/plecs_*.csv` |
| 汇总 | `waveforms/09-hall-sequence/plecs_hall_summary.csv` |
| PLECS Scope | `assets/09-hall-sequence/plecs_scope_hall_forward.png` |
| MATLAB 图 | `assets/09-hall-sequence/hall_sequence_direction_invalid.png` |
| 报告 | `reports/09-hall-sequence-test_report.md` |

若正反转不足一个完整序列，先检查相电流是否为零和母线是否错误设为 48 V；低母线会使高速反电动势通过桥臂二极管制动转子。

# 第 14 篇复现说明：完整 Hall 六步闭环

## 环境

- Windows 11 PowerShell
- PLECS Standalone，XML-RPC 端口 `1080`
- Python 3
- MATLAB，提供 `readtable`、`tiledlayout` 和 `exportgraphics`

## 运行

```powershell
Set-Location .\BLDC
python .\scripts\build_ch14_plecs_model.py
python .\scripts\ch14_plecs_complete_closed_loop.py
python .\scripts\ch14_acceptance_check.py
matlab -batch "run('scripts/ch14_closed_loop_postprocess.m')"
```

期望输出：

```text
Generated models\plecs\ch14_complete_hall_closed_loop\ch14_complete_hall_closed_loop.plecs
Generated chapter 14 PLECS closed-loop evidence. scenarios=5 pass=5 time_points=50001 signals=35
Generated C14 acceptance check. formal_pass=True mutation_pass=True
Generated chapter 14 MATLAB closed-loop figure. scenarios=5 figures=1
```

## 验收条件

| 场景 | 关键条件 |
|---|---|
| `zero_speed_start` | 末值 55-62 rad/s；尾段目标误差 <3；Hall 均值偏差 <1.5 |
| `target_step` | 末值 57-65 rad/s；尾段目标误差 <3；Hall 均值偏差 <1.5；目标阶跃后到 55 rad/s 不超过 0.12 s |
| `load_step` | 尾段目标误差 <8；负载后高限幅占比 >0.5；末值 >45 rad/s |
| `invalid_hall` | 故障窗口全关占比 >0.999；恢复后尾段误差 <3；末值 >55 rad/s |
| `overload` | 末值 <55；尾段目标误差 >15；负载后高限幅占比 >0.85 |

所有场景还要求 Hall 尾段均值偏差小于 `1.5 rad/s`。最近一次验收只读取 PLECS 原生 Hall/control/gate 诊断列，正式场景 `5/5 PASS`，五类 mutation 均为 `FAIL_DETECTED`。

## 生成物

| 类型 | 路径 |
|---|---|
| PLECS 模型 | `models/plecs/ch14_complete_hall_closed_loop/ch14_complete_hall_closed_loop.plecs` |
| 场景 CSV | `waveforms/14-complete-hall-closed-loop/plecs_*.csv` |
| 汇总 CSV | `waveforms/14-complete-hall-closed-loop/plecs_closed_loop_summary.csv` |
| 验收 CSV | `waveforms/14-complete-hall-closed-loop/plecs_acceptance_summary_v2.csv`、`waveforms/14-complete-hall-closed-loop/acceptance_mutations.csv` |
| PLECS Scope | `assets/14-complete-hall-closed-loop/plecs_scope_complete_startup.png` |
| MATLAB 图 | `assets/14-complete-hall-closed-loop/complete_closed_loop_scenarios.png` |
| 报告 | `reports/14-complete-hall-closed-loop-test_report.md`、`reports/14-complete-hall-acceptance-check.md` |

## 信号边界

- `hall_speed_feedback_rad_s` 是 PI 实际使用的反馈，来自模型内 Hall interface 的合法边沿测速。
- `speed_rad_s` 来自 PLECS Machine，只用于验收。
- `hall_invalid` 是测试注入窗口，不是硬件输入电路模型。
- `effective_duty` 等于模型原生 `duty_cmd`，用于观察 PI 输出限幅。
- CSV 原生包含 Hall A/B/C、Hall code、decoded sector、合法转移、fault、enable、Hall 边沿计数和六路门极；`scripts/ch14_acceptance_check.py` 只复核这些列是否满足验收谓词。

## 常见失败解释

- 非法 Hall 后速度长期下降：检查恢复后的第一条边沿是否只用于同步，不能用残余扇区时间直接计算 60° 速度。
- `fault_all_off_fraction<1`：检查非法窗口是否在换相输出职责层强制三相全关。
- Hall 均值偏差正常但逐点差较大：边沿测速是采样保持阶梯信号，应结合边沿周期和尾段均值判断。
- 过载场景 FAIL：先确认负载为 `12 N m`，不要通过放宽速度目标掩盖 duty 未饱和或负载未接入。
- `signals!=35`：核对 `mechanical_angle_rad` 顶层输出是否仍为机械角 + 20 路 Hall/control/gate 诊断向量，以及脚本 `NAMES` 顺序。

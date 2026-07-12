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
matlab -batch "run('scripts/ch14_closed_loop_postprocess.m')"
```

期望输出：

```text
Generated models\plecs\ch14_complete_hall_closed_loop\ch14_complete_hall_closed_loop.plecs
Generated chapter 14 PLECS closed-loop evidence. scenarios=5 pass=5 time_points=50001 signals=16
Generated chapter 14 MATLAB closed-loop figure. scenarios=5 figures=1
```

## 验收条件

| 场景 | 关键条件 |
|---|---|
| `zero_speed_start` | 末值 55-62 rad/s；尾段目标误差 <3；Hall 均值偏差 <1.5 |
| `target_step` | 末值 57-65 rad/s；尾段目标误差 <3；Hall 均值偏差 <1.5 |
| `load_step` | 尾段目标误差 <8；负载后高限幅占比 >0.5；末值 >45 rad/s |
| `invalid_hall` | 故障窗口全关占比 >0.999；恢复后尾段误差 <3；末值 >55 rad/s |
| `overload` | 末值 <55；尾段目标误差 >15；负载后高限幅占比 >0.85 |

所有场景还要求 Hall 尾段均值偏差小于 `1.5 rad/s`。最近一次结果为 `5/5 PASS`。

## 生成物

| 类型 | 路径 |
|---|---|
| PLECS 模型 | `models/plecs/ch14_complete_hall_closed_loop/ch14_complete_hall_closed_loop.plecs` |
| 场景 CSV | `waveforms/14-complete-hall-closed-loop/plecs_*.csv` |
| 汇总 CSV | `waveforms/14-complete-hall-closed-loop/plecs_closed_loop_summary.csv` |
| PLECS Scope | `assets/14-complete-hall-closed-loop/plecs_scope_complete_startup.png` |
| MATLAB 图 | `assets/14-complete-hall-closed-loop/complete_closed_loop_scenarios.png` |
| 报告 | `reports/14-complete-hall-closed-loop-test_report.md` |

## 信号边界

- `hall_speed_feedback_rad_s` 是 PI 实际使用的反馈。
- `speed_rad_s` 来自 PLECS Machine，只用于验收。
- `hall_invalid` 是测试注入窗口，不是硬件输入电路模型。
- `effective_duty` 由三值相命令的滑动窗口统计得到，用于观察执行器限幅。

## 常见失败解释

- 非法 Hall 后速度长期下降：检查恢复后的第一条边沿是否只用于同步，不能用残余扇区时间直接计算 60° 速度。
- `fault_all_off_fraction<1`：检查非法窗口是否在换相输出职责层强制三相全关。
- Hall 均值偏差正常但逐点差较大：边沿测速是采样保持阶梯信号，应结合边沿周期和尾段均值判断。
- 过载场景 FAIL：先确认负载为 `12 N m`，不要通过放宽速度目标掩盖 duty 未饱和或负载未接入。
- `signals!=16`：核对顶层 `hall_speed_feedback_rad_s` 输出和脚本 `NAMES` 顺序。

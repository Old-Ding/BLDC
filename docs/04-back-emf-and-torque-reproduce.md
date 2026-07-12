# 第 04 篇复现说明：反电动势功率与转矩

## 命令

```powershell
Set-Location .\BLDC
python .\scripts\ch01_plecs_bldc_baseline.py
python .\scripts\ch04_torque_power_check.py
matlab -batch "run('scripts/ch04_torque_power_postprocess.m')"
```

## 期望输出

```text
Generated chapter 04 power check. scenarios=3 pass=3 source=PLECS time_points=1703
Generated chapter 04 MATLAB post-processing. scenarios=3 pass=3 figures=2
```

## 判定

逐点计算：

```text
residual = ea*ia + eb*ib + ec*ic - Te*omega
```

最大残差相对场景功率尺度必须低于 `1e-9`。再生场景还要求尾段速度为正、转矩为负、功率为负。

## 最新结果

| 场景 | 点数 | 尾段功率/W | 转矩/N m | 速度/rad/s | 最大残差/W | 结果 |
|---|---:|---:|---:|---:|---:|---|
| `nominal_load` | 601 | 1094.1534 | 2.9936 | 365.4961 | 4.547e-13 | PASS |
| `overload` | 601 | 114.5803 | 4.0098 | 28.4828 | 4.547e-13 | PASS |
| `regenerative_braking` | 501 | -476.2920 | -3.9832 | 119.5589 | 2.274e-13 | PASS |

## 生成物

| 类型 | 路径 |
|---|---|
| 三场景逐点功率 | `waveforms/04-torque-power/plecs_power_*.csv` |
| 汇总 | `waveforms/04-torque-power/plecs_power_summary.csv` |
| PLECS 再生截图 | `assets/04-torque-power/plecs_scope_regenerative_braking.png` |
| MATLAB 图 | `assets/04-torque-power/plecs_*.png` |
| 报告 | `reports/04-torque-power-test_report.md` |

## 常见失败

| 现象 | 检查 |
|---|---|
| 再生场景速度已经为负 | 仿真窗口是否错误延长到 0.1 s 之后 |
| 功率残差明显大于浮点误差 | 电流、反电动势、转矩和速度是否来自同一行 PLECS CSV |
| 只有两场景 | PLECS RPC 是否可用，再生场景是否成功运行 |

## 边界

本实验核对 BLDC Machine 内部理想电磁转换功率，不等价于直流输入功率与轴输出功率的整机效率核对。

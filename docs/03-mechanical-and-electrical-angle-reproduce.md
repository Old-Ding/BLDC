# 第 03 篇复现说明：机械角、电角度和极对数

## 目标

在同一 PLECS BLDC Machine 上保持机械运动一致，只改变极对数，验证电角增量与机械角增量之比等于极对数。

## 命令

PLECS Standalone 需启用 `localhost:1080` XML-RPC。

```powershell
Set-Location .\BLDC
python .\scripts\build_ch02_plecs_model.py
python .\scripts\build_ch03_plecs_model.py
python .\scripts\ch03_plecs_electrical_angle.py
matlab -batch "run('scripts/ch03_electrical_angle_postprocess.m')"
```

## 期望结果

```text
Generated chapter 03 PLECS angle evidence. scenarios=2 pass=2 time_points=501 signals=15
Generated chapter 03 MATLAB post-processing. scenarios=2 pass=2 figures=1
```

| 场景 | 极对数 | 机械角增量/rad | 电角增量/rad | 比值 | 结果 |
|---|---:|---:|---:|---:|---|
| `one_pole_pair` | 1 | 5 | 5 | 1 | PASS |
| `four_pole_pairs` | 4 | 5 | 20 | 4 | PASS |

## 生成物

| 类型 | 路径 |
|---|---|
| PLECS 模型 | `models/plecs/ch03_electrical_angle/ch03_electrical_angle.plecs` |
| 两场景 CSV | `waveforms/03-electrical-angle/plecs_*.csv` |
| 汇总 | `waveforms/03-electrical-angle/plecs_angle_summary.csv` |
| PLECS Scope | `assets/03-electrical-angle/plecs_scope_mechanical_angle.png` |
| MATLAB 图 | `assets/03-electrical-angle/mechanical_vs_electrical_angle.png` |
| 报告 | `reports/03-electrical-angle-test_report.md` |

## 关键实现

PLECS Angle Sensor 输出在 `[-pi, pi]` 回绕。Python 脚本先保存原始机械角，再执行 unwrap 得到连续机械角；电角度只从连续机械角计算。

## 失败解释

| 现象 | 检查 |
|---|---|
| 输出不是 15 路 | 重新运行第 02、03 篇模型生成脚本 |
| 机械角增量出现负值 | 是否错误使用了回绕角末值减初值 |
| 比值不是 1 或 4 | `pole_pairs` 是否进入 BLDC Machine 的 `p` 参数 |
| 三相电流非零 | 母线电压是否仍为 300 V、三值命令是否为全关 |

## 边界

本实验验证角度映射和扇区频率，不比较不同极数电机的转矩、损耗、绕组设计或最高转速。

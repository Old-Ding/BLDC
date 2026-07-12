# 第 11 篇复现说明：PWM duty 与 deadtime

```powershell
Set-Location .\BLDC
python .\scripts\build_ch11_plecs_model.py
python .\scripts\ch11_plecs_pwm_deadtime.py
matlab -batch "run('scripts/ch11_pwm_postprocess.m')"
```

期望 `scenarios=5 pass=5 time_points=25001 signals=15`。PLECS 输出间隔为 2 μs，用于分辨 10 kHz PWM 和 2 μs 开通延迟。

| 生成物 | 路径 |
|---|---|
| 模型 | `models/plecs/ch11_pwm_deadtime/ch11_pwm_deadtime.plecs` |
| CSV | `waveforms/11-pwm-deadtime/plecs_*.csv` |
| 汇总 | `waveforms/11-pwm-deadtime/plecs_pwm_summary.csv` |
| PLECS Scope | `assets/11-pwm-deadtime/plecs_scope_pwm_50.png` |
| MATLAB 图 | `assets/11-pwm-deadtime/pwm_duty_comparison.png` |
| 报告 | `reports/11-pwm-deadtime-test_report.md` |

若 Scope 只显示机械角，检查模型是否由最新 builder 生成：Scope 应连接 `phase_command`，时间窗应为 `0.002 s`。

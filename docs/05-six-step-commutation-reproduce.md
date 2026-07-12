# 第 05 篇复现说明：120 度导通与六步序列

```powershell
Set-Location .\BLDC
python .\scripts\build_ch02_plecs_model.py
python .\scripts\build_ch05_plecs_model.py
python .\scripts\ch05_plecs_six_step.py
matlab -batch "run('scripts/ch05_six_step_postprocess.m')"
```

期望：

```text
Generated chapter 05 PLECS six-step evidence. scenarios=3 pass=3 time_points=601 signals=14
Generated chapter 05 MATLAB post-processing. scenarios=3 pass=3 figures=2
```

生成物：

| 类型 | 路径 |
|---|---|
| PLECS 模型 | `models/plecs/ch05_six_step_sequence/ch05_six_step_sequence.plecs` |
| 三场景 CSV | `waveforms/05-six-step-sequence/plecs_*.csv` |
| 汇总 | `waveforms/05-six-step-sequence/plecs_six_step_summary.csv` |
| PLECS Scope | `assets/05-six-step-sequence/plecs_scope_forward_sequence.png` |
| MATLAB 图 | `assets/05-six-step-sequence/*.png` |
| 报告 | `reports/05-six-step-sequence-test_report.md` |

判定只覆盖状态合法性、顺序和三相电流 KCL。固定 1 ms 换相下转矩正负交替属于本实验的可观察结果，不作为 FAIL；启动同步问题进入第 06、07 篇。

# 第 10 篇复现说明：Hall 换相与安装偏置

```powershell
Set-Location .\BLDC
python .\scripts\build_ch10_plecs_model.py
python .\scripts\ch10_plecs_hall_commutation.py
matlab -batch "run('scripts/ch10_hall_commutation_postprocess.m')"
```

期望 `scenarios=8 pass=8 time_points=401 signals=15 best_offset=0`。

场景统一为 `48 V`、初速 `30 rad/s`、无负载、80 ms。脚本扫描偏置 0..5、反向表和全关基线。当前模型的关键复核值为：offset 0 平均转矩 `0.906 N m`，offset 1 平均转矩 `-0.195 N m` 且峰值电流 `65.388 A`。

| 生成物 | 路径 |
|---|---|
| 模型 | `models/plecs/ch10_hall_commutation/ch10_hall_commutation.plecs` |
| 原始 CSV | `waveforms/10-hall-commutation/plecs_*.csv` |
| 汇总 | `waveforms/10-hall-commutation/plecs_hall_commutation_summary.csv` |
| PLECS Scope | `assets/10-hall-commutation/plecs_scope_correct_hall.png` |
| MATLAB 图 | `assets/10-hall-commutation/hall_offset_sweep.png` |
| 报告 | `reports/10-hall-commutation-test_report.md` |

若模型报告 `Current controller` 端子重叠，检查 `rotor_angle` 到 Hall commutator 的显式折线路径 `[110,135;110,95]` 是否仍存在。

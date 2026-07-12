# 第 06 篇复现说明：开环电角频率

```powershell
Set-Location .\BLDC
python .\scripts\build_ch05_plecs_model.py
python .\scripts\build_ch06_plecs_model.py
python .\scripts\ch06_plecs_open_loop_angle.py
matlab -batch "run('scripts/ch06_open_loop_postprocess.m')"
```

期望 `scenarios=2 pass=2 time_points=601 signals=14`。生成物位于 `waveforms/06-open-loop-angle`、`assets/06-open-loop-angle` 和 `reports/06-open-loop-angle-test_report.md`。

PASS 分别表示慢场产生正平均转矩并明显加速，以及快场正确复现转矩抵消和无法跟随。两者都不代表已经完成启动闭环。

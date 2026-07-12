# 第 13 篇复现说明：速度 PI、限幅与积分抗饱和

## 环境

- Windows 11 PowerShell
- PLECS Standalone，XML-RPC 端口 `1080`
- Python 3
- MATLAB，提供 `readtable`、`tiledlayout` 和 `exportgraphics`

## 运行

```powershell
Set-Location .\BLDC
python .\scripts\build_ch13_plecs_model.py
python .\scripts\ch13_plecs_speed_pi.py
matlab -batch "run('scripts/ch13_speed_pi_postprocess.m')"
```

期望输出：

```text
Generated models\plecs\ch13_speed_pi\ch13_speed_pi.plecs
Generated chapter 13 PLECS speed-PI evidence. scenarios=4 pass=4 time_points=20001 signals=15
Generated chapter 13 MATLAB speed-PI figure. scenarios=4 figures=1
```

## 场景与关键结果

| 场景 | 关键输入 | 期望结果 |
|---|---|---|
| `speed_step_aw` | 45→60 rad/s，抗饱和开启 | 尾段误差小于 3 rad/s，高限幅占比小于 0.05 |
| `load_step_aw` | 0→3 N·m | 末值速度大于 50 rad/s，峰值电流高于普通阶跃 |
| `recovery_aw` | 200→40 rad/s，抗饱和开启 | 尾段误差小于 10 rad/s，迅速退出高限幅 |
| `recovery_no_aw` | 同输入，抗饱和关闭 | 尾段误差至少为开启时两倍，长期停在高限幅 |

最近一次运行应为 `4/4 PASS`。`recovery_no_aw` 的 PASS 表示预期的失效现象被复现。

## 生成物

| 类型 | 路径 |
|---|---|
| PLECS 模型 | `models/plecs/ch13_speed_pi/ch13_speed_pi.plecs` |
| 场景 CSV | `waveforms/13-speed-pi/plecs_*.csv` |
| 汇总 CSV | `waveforms/13-speed-pi/plecs_speed_pi_summary.csv` |
| PLECS Scope | `assets/13-speed-pi/plecs_scope_speed_pi.png` |
| MATLAB 图 | `assets/13-speed-pi/speed_pi_antiwindup.png` |
| 报告 | `reports/13-speed-pi-test_report.md` |

## 常见失败解释

- `PLECS_RPC_NOT_READY`：PLECS 未启动，或 XML-RPC 未监听 `1080`。
- `signals!=15`：顶层输出端口被改动，先核对模型与 `NAMES` 的顺序。
- `recovery_no_aw` 未长期高限幅：检查 `antiwindup_enable=0` 是否进入 C-Script 参数。
- 目标阶跃误差变大：先确认 `Kp`、`Ki`、duty 上下限和仿真时长没有被同时修改。
- PLECS 图与 MATLAB 图不同：Scope 是 PLECS 原生单场景截图；MATLAB 图读取四个 PLECS CSV 做并列比较。

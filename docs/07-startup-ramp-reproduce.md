# 第 07 篇复现说明：定位与开环频率斜坡

## 工具与前提

| 工具 | 要求 | 用途 |
|---|---|---|
| PLECS Standalone | 5.0，XML-RPC `localhost:1080` | 运行真实 IGBT 桥与 BLDC Machine |
| Python | 3.11 或更高 | 生成模型、运行场景、导出 CSV 和报告 |
| MATLAB | R2024b 或兼容版本 | 读取 PLECS CSV 并生成对比图 |

PLECS 是主仿真器。Python 只负责通过 XML-RPC 设置场景、导出 PLECS 返回值和计算指标；MATLAB 不重新仿真电机，只做后处理。

## 执行命令

```powershell
Set-Location .\BLDC
python .\scripts\build_ch02_plecs_model.py
python .\scripts\build_ch03_plecs_model.py
python .\scripts\build_ch07_plecs_model.py
python .\scripts\ch07_plecs_startup_ramp.py
matlab -batch "run('scripts/ch07_startup_postprocess.m')"
```

期望输出：

```text
Generated chapter 07 PLECS startup evidence. scenarios=2 pass=2 time_points=601 signals=15
Generated chapter 07 MATLAB post-processing. scenarios=2 pass=2 figures=1
```

## 场景与判据

| 场景 | 输入 | PASS 判据 | 物理含义 |
|---|---|---|---|
| `ramp_start` | 20 ms 定位，5 Hz 到 33.333 Hz/200 ms | 末值速度大于 70 rad/s，尾段平均转矩大于 1 N m | 复现斜坡比直接高频更容易建立正向加速 |
| `direct_fast` | 无定位，直接 166.667 Hz | 末值速度绝对值小于 10 rad/s，尾段平均转矩绝对值小于 1 N m | 复现命令场过快、转矩抵消、转子无法跟随 |

PASS 是教学现象判据，不是稳定同步判据。斜坡场景仍有持续相位滑移和大电流。

## 最新期望指标

| 场景 | 末值速度/rad/s | 尾段转矩/N m | 尾段绝对相差/rad | 峰值相电流/A |
|---|---:|---:|---:|---:|
| `ramp_start` | 92.088 | 5.525 | 1.334 | 61.063 |
| `direct_fast` | -1.225 | 0.110 | 1.540 | 14.460 |

允许不同机器或求解器版本引入末位数值差异，但 PASS/FAIL 结论不应变化。

## 生成物

| 类型 | 路径 |
|---|---|
| PLECS 模型 | `models/plecs/ch07_startup_ramp/ch07_startup_ramp.plecs` |
| 场景脚本 | `scripts/ch07_plecs_startup_ramp.py` |
| MATLAB 脚本 | `scripts/ch07_startup_postprocess.m` |
| 原始 CSV | `waveforms/07-startup-ramp/plecs_ramp_start.csv`、`plecs_direct_fast.csv` |
| 汇总 CSV | `waveforms/07-startup-ramp/plecs_startup_summary.csv` |
| PLECS 原生图 | `assets/07-startup-ramp/plecs_scope_ramp_start.png` |
| MATLAB 图 | `assets/07-startup-ramp/ramp_vs_direct_start.png` |
| 报告 | `reports/07-startup-ramp-test_report.md` |

## 常见失败解释

| 现象 | 优先检查 |
|---|---|
| `PLECS_RPC_NOT_READY` | PLECS 是否启动，XML-RPC 是否监听 1080 端口 |
| 返回信号不是 15 路 | 第 03 篇母模型是否重新生成，顶层输出接口是否被修改 |
| 转矩非零但三相电流全为零 | BLDC Machine 电流输出的两个 Branch 是否都存在，不能把多目标连接写成一个 Branch 加直接 Dst |
| step 在斜坡中倒跳 | 是否错误使用 `t/当前周期`，应积分频率得到连续命令电角 |
| PLECS Scope 截图失败 | Scope 窗口是否存在；脚本会枚举 PLECS 全部顶层窗口 |
| 峰值电流很高 | 当前是全母线六步、无 PWM 限流，这是模型边界，不应调低报告值掩盖问题 |

# 第 02 篇复现说明：三相桥的 6 个开关

本篇复现目标是确认 `AH/BH/CH/AL/BL/CL` 六路桥臂命令能够稳定映射为 A/B/C 三相状态，并能识别同一相上下桥直通。

## 章节合同

| 项目 | 内容 |
|---|---|
| 核心问题 | 六个 gate 命令如何决定 A/B/C 相状态和 `shoot_through` |
| 本篇不解决 | 换相表、PWM duty、电机电流、反电动势、转矩、硬件死区 |
| 成功标准 | 6 个场景全部 PASS，并生成 CSV、PNG 和测试报告 |
| 主要证据 | MATLAB 脚本、`bridge_state.c`、CSV、PNG、测试报告 |

## 环境

| 项目 | 要求 |
|---|---|
| 系统 | Windows 11 |
| Shell | PowerShell |
| 编码 | UTF-8 |
| 必需工具 | MATLAB |
| 可选工具 | PLECS RPC 服务、Python |

PLECS 不是本篇 MATLAB 图和 CSV 的必需条件。PLECS RPC 只用于自动加载教学模型。

## 检查本篇文件

```powershell
Set-Location D:\1codex\BLDC
Get-Content -LiteralPath .\blog\02-three-phase-bridge.md -Encoding UTF8
Get-Content -LiteralPath .\docs\02-three-phase-bridge-reproduce.md -Encoding UTF8
Get-Content -LiteralPath .\learning_model\steps\step_01_three_phase_bridge\bridge_state.c -Encoding UTF8
```

期望结果：

```text
能看到 AH/BH/CH/AL/BL/CL -> A/B/C state -> shoot_through 的最小数据流。
```

## 运行 MATLAB 场景测试

```powershell
Set-Location D:\1codex\BLDC
matlab -batch "run('D:\1codex\BLDC\scripts\ch02_three_phase_bridge_tests.m')"
```

当前期望输出：

```text
Generated chapter 02 three-phase bridge tests. scenarios=6 pass=6 figures=2
```

如果 MATLAB 报错，先不要改文章结论，应该先修复脚本或环境。文章中的结论必须来自重新生成的 CSV 和报告。

## 生成文件

| 文件 | 用途 |
|---|---|
| `scripts\ch02_three_phase_bridge_tests.m` | 生成本篇全部数据、图和报告 |
| `assets\02-three-phase-bridge\bridge_state_scenarios.png` | 六路 gate、三相状态和直通标志时序图 |
| `assets\02-three-phase-bridge\bridge_state_fault_matrix.png` | 正常导通与直通故障对比图 |
| `waveforms\02-three-phase-bridge\bridge_state_timeseries.csv` | 图 1 背后的逐点数据 |
| `waveforms\02-three-phase-bridge\bridge_state_summary.csv` | 6 个场景的 PASS/FAIL 汇总 |
| `reports\02-three-phase-bridge-test_report.md` | 参数摘要、测试结果和边界说明 |

## 检查场景汇总

```powershell
Get-Content -LiteralPath .\waveforms\02-three-phase-bridge\bridge_state_summary.csv -Encoding UTF8
```

当前期望摘要：

```text
scenario,gates,expected_phase_state,actual_phase_state,expected_shoot_through,actual_shoot_through,result,note
normal_AH_BL,AH=1 BH=0 CH=0 AL=0 BL=1 CL=0,A=HIGH B=LOW C=FLOAT,A=HIGH B=LOW C=FLOAT,0,0,PASS,A 相接正母线，B 相接负母线，C 相悬空
normal_BH_CL,AH=0 BH=1 CH=0 AL=0 BL=0 CL=1,A=FLOAT B=HIGH C=LOW,A=FLOAT B=HIGH C=LOW,0,0,PASS,B 相接正母线，C 相接负母线，A 相悬空
normal_CH_AL,AH=0 BH=0 CH=1 AL=1 BL=0 CL=0,A=LOW B=FLOAT C=HIGH,A=LOW B=FLOAT C=HIGH,0,0,PASS,C 相接正母线，A 相接负母线，B 相悬空
all_off,AH=0 BH=0 CH=0 AL=0 BL=0 CL=0,A=FLOAT B=FLOAT C=FLOAT,A=FLOAT B=FLOAT C=FLOAT,0,0,PASS,六个桥臂全关，三相都悬空
fault_AH_AL,AH=1 BH=0 CH=0 AL=1 BL=0 CL=0,A=FAULT B=FLOAT C=FLOAT,A=FAULT B=FLOAT C=FLOAT,1,1,PASS,A 相上下桥同时导通，进入直通故障
fault_BH_BL,AH=0 BH=1 CH=0 AL=0 BL=1 CL=0,A=FLOAT B=FAULT C=FLOAT,A=FLOAT B=FAULT C=FLOAT,1,1,PASS,B 相上下桥同时导通，进入直通故障
```

## 检查测试报告

```powershell
Get-Content -LiteralPath .\reports\02-three-phase-bridge-test_report.md -Encoding UTF8
```

重点检查：

| 检查项 | 期望 |
|---|---|
| 场景数 | 6 |
| PASS 数 | 6 |
| `normal_AH_BL` | `A=HIGH B=LOW C=FLOAT`，`shoot_through=0` |
| `all_off` | 三相都是 `FLOAT` |
| `fault_AH_AL` | `A=FAULT`，`shoot_through=1` |
| `fault_BH_BL` | `B=FAULT`，`shoot_through=1` |

## 可选：重新生成 PLECS 教学模型

```powershell
Set-Location D:\1codex\BLDC
powershell -ExecutionPolicy Bypass -File .\learning_model\steps\generate_step_plecs.ps1
```

期望输出：

```text
Generated step PLECS models.
```

这一步证明教学模型文件可以重新生成，不代表 PLECS 已经完成仿真。

## 可选：验证 PLECS RPC

先启动 PLECS RPC 服务，再运行：

```powershell
Set-Location D:\1codex\BLDC
python .\learning_model\steps\test_step_plecs_models.py
```

如果 PLECS RPC 已启动，期望 Step 01 至 Step 08 能加载并仿真。

如果输出：

```text
PLECS_RPC_NOT_READY
```

说明本机没有连接 PLECS RPC。这是环境状态，不影响本篇 MATLAB 生成的 CSV、PNG 和报告。

## 常见失败含义

| 现象 | 可能原因 | 处理 |
|---|---|---|
| MATLAB 找不到脚本 | 当前目录不是仓库根目录 | 先执行 `Set-Location D:\1codex\BLDC` |
| CSV 里出现 `FAIL` | 场景期望或状态判断逻辑不一致 | 先检查 `scripts\ch02_three_phase_bridge_tests.m` 和 `bridge_state.c` |
| PNG 没更新 | MATLAB 脚本没有完整跑完 | 重新运行脚本并确认控制台输出 `figures=2` |
| PLECS 报 `PLECS_RPC_NOT_READY` | PLECS RPC 未启动 | 启动 PLECS RPC 后再跑可选验证 |

## 复现结果怎么解读

运行结果为 `scenarios=6 pass=6` 时，可以这样读：

| 看到的结果 | 可以得出的结论 | 不要误读成 |
|---|---|---|
| `normal_AH_BL`、`normal_BH_CL`、`normal_CH_AL` 为 PASS | 三相桥状态层能识别正常的一相拉高、一相拉低、一相悬空 | 六步换相顺序已经正确 |
| `fault_AH_AL`、`fault_BH_BL` 为 PASS | 同一相上下桥同时导通会被标成 `FAULT` 和 `shoot_through=1` | 硬件死区和驱动保护已经完成 |
| PNG 和 CSV 均重新生成 | MATLAB 状态级测试链路可复现 | PLECS 完整电机模型已经完成仿真 |

后续章节会继续把换相顺序、PWM 调制、电机电流、转矩、硬件死区、过流保护和故障锁存分层接入。

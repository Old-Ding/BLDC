# 第 00 篇复现说明：BLDC 教程学习路线

本篇复现的目标不是跑电机波形，而是确认教程材料、模型入口和后续仿真命令都可定位。

配套仓库：

```text
https://github.com/Old-Ding/BLDC
```

## 环境

| 项目 | 要求 |
|---|---|
| 系统 | Windows 11 |
| Shell | PowerShell |
| 文件编码 | UTF-8 |
| 仿真工具 | PLECS 可选，用于加载 Step 01 到 Step 08 |
| 数据分析 | MATLAB 可选，从测速和 PI 扫参章节开始使用 |

## 检查教程文件

```powershell
Set-Location D:\1codex\BLDC
Get-Content -LiteralPath .\README.md -Encoding UTF8
Get-Content -LiteralPath .\blog\README.md -Encoding UTF8
Get-Content -LiteralPath .\docs\series-plan.md -Encoding UTF8
Get-Content -LiteralPath .\learning_model\steps\README.md -Encoding UTF8
```

期望结果：

```text
能看到第一阶段 00 到 11 篇文章规划。
能看到 Step 01 到 Step 08 的模型入口。
```

## 重新生成 PLECS 教学模型

```powershell
Set-Location D:\1codex\BLDC
powershell -ExecutionPolicy Bypass -File .\learning_model\steps\generate_step_plecs.ps1
```

期望输出：

```text
Generated step PLECS models.
```

这个命令只重新生成 Step 01 到 Step 07 的信号级教学模型，并复制 Step 08 的完整模型副本。它不等同于真实仿真通过。

## 批量加载仿真模型

先启动 PLECS RPC 服务，再运行：

```powershell
Set-Location D:\1codex\BLDC
python .\learning_model\steps\test_step_plecs_models.py
```

期望输出包含：

```text
SIM_OK step_01_three_phase_bridge
SIM_OK step_02_six_step_table
SIM_OK step_03_open_loop_commutation
SIM_OK step_04_hall_commutation
SIM_OK step_05_pwm_duty
SIM_OK step_06_speed_estimation
SIM_OK step_07_speed_pi
SIM_OK step_08_plecs_full_model
```

如果 PLECS RPC 没有启动，脚本会输出：

```text
PLECS_RPC_NOT_READY
```

这表示仿真服务未连接，不表示文章结构或模型文件路径错误。

## 本篇边界

本篇只证明教程路线、目录入口和复现命令已经建立。它不证明：

1. BLDC 电机已经能稳定闭环运行。
2. 参数已经适合硬件。
3. 保护状态机已经完整。
4. FOC 已经纳入当前主线。

这些内容分别放到后续章节处理。

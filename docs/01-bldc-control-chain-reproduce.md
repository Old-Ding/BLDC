# 第 01 篇复现说明：BLDC 控制链总览

本篇复现目标是确认 BLDC 六步控制链的每一层都有对应的本地材料，并能重新生成 PLECS 教学模型。

## 章节合同

| 项目 | 内容 |
|---|---|
| 核心问题 | BLDC 六步控制链里，各层输入输出是什么 |
| 本篇不解决 | 具体换相表、PI 参数、保护状态机、FOC |
| 成功标准 | 能把 Step 01 到 Step 08 映射到控制链职责层 |
| 主要证据 | `learning_model/steps/README.md` 和各 Step 目录 |

## 环境

| 项目 | 要求 |
|---|---|
| 系统 | Windows 11 |
| Shell | PowerShell |
| 编码 | UTF-8 |
| 必需工具 | PowerShell、Python |
| 可选工具 | PLECS RPC 服务 |

## 检查本篇文件

```powershell
Set-Location D:\1codex\BLDC
Get-Content -LiteralPath .\blog\01-bldc-control-chain.md -Encoding UTF8
Get-Content -LiteralPath .\docs\01-bldc-control-chain-reproduce.md -Encoding UTF8
```

期望结果：

```text
能看到 target_speed -> speed_controller -> duty -> PWM -> gates -> inverter -> motor -> feedback 的数据流。
```

## 检查 Step 目录

```powershell
Set-Location D:\1codex\BLDC
Get-ChildItem -LiteralPath .\learning_model\steps -Directory |
    Where-Object { $_.Name -like 'step_*' } |
    Select-Object Name |
    Format-Table -AutoSize
```

期望至少看到：

```text
step_01_three_phase_bridge
step_02_six_step_table
step_03_open_loop_commutation
step_04_hall_commutation
step_05_pwm_duty
step_06_speed_estimation
step_07_speed_pi
step_08_plecs_full_model
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

这个命令证明模型生成链路存在，不证明 PLECS 已经完成仿真。

## 批量验证 PLECS 模型

先启动 PLECS RPC 服务，再运行：

```powershell
Set-Location D:\1codex\BLDC
python .\learning_model\steps\test_step_plecs_models.py
```

如果 PLECS RPC 已启动，期望看到 Step 01 到 Step 08 的 `SIM_OK`。

如果输出：

```text
PLECS_RPC_NOT_READY
```

说明 PLECS RPC 没有连接。这是环境状态，不表示文章或模型路径错误。

## 本篇边界

本篇只验证控制链总览和材料映射。它不证明：

1. 具体三相桥逻辑完全正确。
2. Hall 换相表适配所有电机。
3. 速度 PI 参数已经可用于硬件。
4. 保护状态机已经完整。

这些内容会在后续章节分别验证。

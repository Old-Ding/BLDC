# 为什么 BLDC 教程要从最小模型开始

很多人第一次看 BLDC 仿真模型时，会直接打开完整 PLECS 示例。模型能跑，但一屏里同时出现电机、三相桥、角度传感器、电流控制器、PWM 脉冲和 Scope。现象很多，因果链却不清楚。

本系列不从完整模型开始，而是先把 BLDC 控制链拆成最小职责层。每一篇只新增一个概念，先看输入、输出和可观测变量，再回到完整 PLECS 模型。

配套仓库：

[https://github.com/Old-Ding/BLDC](https://github.com/Old-Ding/BLDC)

## 本系列的主线

第一阶段只做六步 BLDC 最小闭环：

```text
三相桥
  -> 六步换相表
  -> 开环换相
  -> Hall 换相
  -> PWM duty
  -> Hall 测速
  -> 速度 PI
  -> PLECS 完整模型对照
```

这条路线的目标不是一步到位做硬件控制器，而是先把每个职责层讲清楚。

## 为什么不用完整模型开头

完整模型的问题不是错误，而是信息密度太高。一个初学者看到 `pulses`、`theta`、`Current controller`、`Current shape` 时，很容易把三个问题混在一起：

| 问题 | 应该属于哪一层 |
|---|---|
| 哪两个桥臂导通 | 六步换相表 |
| 什么时候换下一步 | 开环节拍或 Hall 解码 |
| 输出多少能量 | PWM duty 和速度环 |

如果这三层没有分开，后面调试时就很难从症状追到根因。电机不转可能是换相表错、Hall 顺序错、duty 太小、开环节拍太快，也可能是完整模型里的负载或参数问题。最小模型的价值就是让每个问题有唯一入口。

## 工具怎么分工

本系列继续使用 PLECS 和 MATLAB，但不会让一个工具承担所有职责。

| 工具 | 本系列中的职责 |
|---|---|
| PLECS | 建系统现象，观察 Scope 波形，验证三相桥、电机和负载响应 |
| MATLAB | 做公式验证、参数扫描、数据处理和图表导出 |
| C 代码 | 表达换相表、Hall 解码、速度估算、速度 PI 和状态机 |
| Markdown | 记录数据流、实验结果、边界和复现命令 |

所以教程的数据流是：

```text
C 控制逻辑
  -> PLECS 观察系统现象
  -> MATLAB 分析数据和参数
  -> Markdown 写成可复现文章
```

## 第一阶段章节

| 篇章 | 标题 | 核心问题 |
|---:|---|---|
| 00 | 为什么 BLDC 教程要从最小模型开始 | 为什么不先看完整模型 |
| 01 | BLDC 控制链总览 | 控制器、PWM、三相桥、电机和反馈如何连接 |
| 02 | 三相桥的 6 个开关 | AH/BH/CH/AL/BL/CL 如何决定三相状态 |
| 03 | 电角度、机械角度和极对数 | 为什么机械圈和电周期不是一回事 |
| 04 | 六步换相表 | `step -> gates` 如何映射 |
| 05 | 开环换相 | 没有反馈时如何制造旋转磁场 |
| 06 | 开环为什么会失步 | 失步根因为什么不在三相桥层 |
| 07 | Hall 状态与六步换相 | `Hall -> gates` 的唯一职责层在哪里 |
| 08 | PWM 占空比 | PWM 为什么只调能量，不改换相顺序 |
| 09 | Hall 边沿测速 | 如何从边沿周期计算 rpm |
| 10 | 速度 PI 闭环 | 速度环为什么只输出 duty |
| 11 | 回到 PLECS 完整模型 | 最小模型如何映射回真实系统 |

## 当前配套文件

现有学习模型放在：

```text
learning_model/steps
```

GitHub 对应目录：

[https://github.com/Old-Ding/BLDC/tree/main/learning_model/steps](https://github.com/Old-Ding/BLDC/tree/main/learning_model/steps)

其中 Step 01 到 Step 07 是信号级 PLECS 教学模型，统一结构是：

```text
Clock -> StepLogic(C-Script) -> Demux -> Scope
```

这些模型只用于观察控制变量，不模拟真实绕组电流和机械负载。Step 08 才是完整 BLDC 电机模型对照。

| 步骤 | 学什么 | 目录 |
|---|---|---|
| Step 01 | 三相桥状态 | `learning_model/steps/step_01_three_phase_bridge` |
| Step 02 | 六步换相表 | `learning_model/steps/step_02_six_step_table` |
| Step 03 | 开环换相 | `learning_model/steps/step_03_open_loop_commutation` |
| Step 04 | Hall 换相 | `learning_model/steps/step_04_hall_commutation` |
| Step 05 | PWM 占空比 | `learning_model/steps/step_05_pwm_duty` |
| Step 06 | Hall 速度估算 | `learning_model/steps/step_06_speed_estimation` |
| Step 07 | 速度 PI | `learning_model/steps/step_07_speed_pi` |
| Step 08 | PLECS 完整模型 | `learning_model/steps/step_08_plecs_full_model` |

## 这个路线证明什么

这个路线证明：BLDC 教程可以按职责层递进，而不是一开始把所有模块揉在一起。读者每学一篇，都能回答当前层的输入、输出和观测变量。

## 这个路线不证明什么

这个路线不证明当前参数适合硬件，也不证明保护逻辑已经完整。硬件上电还需要 duty 限幅、软启动、过流保护、欠压保护、堵转检测和故障状态机。那些内容属于工程化阶段，不提前塞进六步换相入门篇。

## 如何复现

先查看路线：

```powershell
Set-Location D:\1codex\BLDC
Get-Content -LiteralPath .\learning_model\steps\README.md -Encoding UTF8
```

如果需要重新生成 PLECS 教学模型：

```powershell
powershell -ExecutionPolicy Bypass -File .\learning_model\steps\generate_step_plecs.ps1
```

如果已经启动 PLECS RPC 服务，可以批量验证模型能否加载仿真：

```powershell
python .\learning_model\steps\test_step_plecs_models.py
```

本篇的复现说明见：

```text
docs/00-bldc-learning-route-reproduce.md
```

## 下一篇

下一篇进入 BLDC 控制链总览。重点不是公式，而是先把数据流画清楚：

```text
target_speed
  -> speed_controller
  -> duty
  -> PWM
  -> gates
  -> inverter
  -> motor
  -> Hall / speed feedback
```

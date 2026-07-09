# BLDC 控制链总览：先看数据流，再看算法

很多 BLDC 入门资料一开始就讲换相表、PWM、霍尔、速度环。每个点单独看都不难，但放在一起时，读者容易不知道一个变量到底是谁产生的、谁消费的、出了问题应该查哪一层。

本篇先不讲具体算法，只回答一个问题：BLDC 六步控制链里，每一层的输入和输出是什么。

配套仓库：

[https://github.com/Old-Ding/BLDC](https://github.com/Old-Ding/BLDC)

## 本篇只解决什么

本篇只建立控制链总览：

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

这里的重点不是公式，而是先把职责边界固定下来。后续每篇文章只深入其中一层。

## 为什么要先看数据流

如果不先建数据流，常见问题会被混在一起：

| 现象 | 不应该直接归因到 | 应该先查的链路 |
|---|---|---|
| 电机不转 | PI 参数 | `gates -> inverter -> motor` 是否有有效输出 |
| 电机抖动 | PWM 频率 | `Hall -> gates` 是否顺序正确 |
| 速度不稳 | 三相桥 | `Hall edge -> speed feedback -> speed_controller` 是否更新稳定 |
| duty 到顶 | 换相表 | 目标、负载、限幅和反馈是否匹配 |

先看数据流的意义是：症状出现时，可以沿着调用链往上追，而不是在没有证据的层面猜原因。

## 六步 BLDC 的最小调用链

第一阶段教程采用六步 BLDC 主线。最小调用链可以拆成 8 个职责层：

| 层级 | 输入 | 输出 | 唯一职责 |
|---|---|---|---|
| 目标层 | 用户设定、上位机命令 | `target_speed` | 给出希望达到的速度 |
| 速度控制层 | `target_speed`、`actual_speed` | `duty` | 决定需要多少能量 |
| PWM 层 | `duty`、`carrier`、基础换相命令 | 带 PWM 的 gates | 把能量指令调制成开关命令 |
| 换相层 | `step` 或 Hall 状态 | 基础 gates | 决定哪两相导通 |
| 功率级 | gates、母线电压 | 三相端电压/电流 | 执行桥臂开关动作 |
| 电机本体 | 三相电压/电流、负载 | 转矩、转速、位置 | 产生机械响应 |
| 位置反馈层 | Hall A/B/C | Hall 状态或换相 step | 提供位置扇区 |
| 速度反馈层 | Hall 边沿周期、极对数 | `actual_speed` | 给速度环提供反馈 |

这张表是后续章节的边界。比如速度 PI 只输出 `duty`，它不应该直接处理桥臂，也不应该重复判断 Hall 合法性。

## 现有 PLECS 学习模型如何对应

当前仓库已经把这条链拆成 Step 01 到 Step 08。每一步只新增一个职责：

| 步骤 | 对应控制链 | 观察重点 |
|---|---|---|
| Step 01 三相桥状态 | gates -> phase state | 上下桥是否直通，三相分别接正母线、负母线还是悬空 |
| Step 02 六步换相表 | step -> gates | 每个 step 对应哪两个桥臂导通 |
| Step 03 开环换相 | tick -> step -> gates | 不靠反馈也能产生旋转磁场 |
| Step 04 Hall 换相 | Hall -> gates | 位置反馈如何决定换相 |
| Step 05 PWM duty | duty + carrier + gates -> PWM gates | PWM 只调能量，不改换相顺序 |
| Step 06 速度估算 | Hall edge -> actual_speed | 速度来自 Hall 边沿间隔 |
| Step 07 速度 PI | target_speed - actual_speed -> duty | 闭环只输出占空比 |
| Step 08 完整模型 | inverter + motor + sensor + controller | 把最小模型映射回真实系统 |

Step 01 到 Step 07 是信号级教学模型，统一结构是：

```text
Clock -> StepLogic(C-Script) -> Demux -> Scope
```

这不是完整电机仿真。它们的作用是先把控制变量看清楚。Step 08 才是完整 BLDC 电机模型对照。

## PLECS、MATLAB 和 C 的职责

本系列继续使用 PLECS 和 MATLAB，但它们不承担同一个职责。

| 工具 | 在本系列中的位置 | 不负责什么 |
|---|---|---|
| PLECS | 建立系统现象，观察桥臂、PWM、电机和反馈波形 | 不替代算法分层 |
| MATLAB | 计算公式、扫参数、处理导出数据、画图 | 不替代功率级仿真 |
| C 代码 | 表达换相、测速、PI、状态机等控制逻辑 | 不模拟真实电机本体 |
| Markdown | 记录调用链、实验命令和边界 | 不制造证据 |

所以正确工作流是：

```text
先用 C 写清唯一职责层
  -> 用 PLECS 看该层进入系统后的现象
  -> 用 MATLAB 分析参数和数据
  -> 再把结果写成教程
```

## 哪些内容留到后面

本篇不讲这些内容：

| 内容 | 放到哪篇 |
|---|---|
| 三相桥具体状态判断 | 第 02 篇 |
| 电角度、机械角度和极对数 | 第 03 篇 |
| 六步换相表 | 第 04 篇 |
| 开环换相和失步 | 第 05、06 篇 |
| Hall 状态表 | 第 07 篇 |
| PWM 占空比 | 第 08 篇 |
| Hall 边沿测速 | 第 09 篇 |
| 速度 PI | 第 10 篇 |
| 保护状态机、软启动、堵转检测 | 第二阶段工程化 |
| FOC、Clarke/Park、SVPWM | 第三阶段 FOC 进阶 |

这样拆分的目的，是让每个问题有唯一职责层。比如非法 Hall 状态只应该先在 `Hall -> gates` 这一层讨论；如果后续确实需要保护层重复关断，必须先说明它是安全授权层，而不是重复修正换相层。

## 这个总览证明什么

本篇证明的是：当前教程已经有一条可追踪的数据流，且仓库里的 Step 01 到 Step 08 能分别承接这条链上的关键职责。

它不证明电机已经能在硬件上安全运行。硬件仍然需要驱动器死区、过流保护、欠压保护、软启动、堵转检测、故障状态机和上电检查。

## 如何复现

先查看学习模型入口：

```powershell
Set-Location D:\1codex\BLDC
Get-Content -LiteralPath .\learning_model\steps\README.md -Encoding UTF8
```

重新生成 Step 01 到 Step 08 教学模型：

```powershell
powershell -ExecutionPolicy Bypass -File .\learning_model\steps\generate_step_plecs.ps1
```

如果已经启动 PLECS RPC 服务，可以验证模型能否加载仿真：

```powershell
python .\learning_model\steps\test_step_plecs_models.py
```

本篇复现说明见：

```text
docs/01-bldc-control-chain-reproduce.md
```

## 下一篇

下一篇进入三相桥的 6 个开关。重点是把 `AH/BH/CH/AL/BL/CL` 翻译成 A/B/C 三相状态，并明确直通检测属于三相桥状态层，不属于速度 PI 或 PWM 层。

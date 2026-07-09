# BLDC 最简模型学习路线

目标：先用最小模型学清楚一个职责，再进入 PLECS 完整模型。每一步只新增一个概念，避免把功率级、换相、PWM、速度环混在一起。

## 学习顺序

| 步骤 | 最小模型 | PLECS 文件 | 先看什么 |
|---|---|---|---|
| 01 | 三相桥状态模型 | `step_01_three_phase_bridge\step_01_three_phase_bridge.plecs` | 上下桥不能同时导通 |
| 02 | 六步换相表 | `step_02_six_step_table\step_02_six_step_table.plecs` | 每步只选一个上桥和一个下桥 |
| 03 | 开环换相 | `step_03_open_loop_commutation\step_03_open_loop_commutation.plecs` | 不靠反馈也能产生旋转磁场 |
| 04 | 霍尔换相 | `step_04_hall_commutation\step_04_hall_commutation.plecs` | 位置反馈如何决定换相 |
| 05 | PWM 占空比 | `step_05_pwm_duty\step_05_pwm_duty.plecs` | PWM 只调能量，不改换相顺序 |
| 06 | 速度估算 | `step_06_speed_estimation\step_06_speed_estimation.plecs` | 速度来自 Hall 边沿间隔 |
| 07 | 速度 PI | `step_07_speed_pi\step_07_speed_pi.plecs` | 闭环只输出占空比 |
| 08 | PLECS 完整模型 | `step_08_plecs_full_model\step_08_plecs_full_model.plecs` | 把最简模型映射回真实系统 |

## 使用原则

1. 每一步先读对应目录里的 `README.md`。
2. 先理解输入、输出和唯一职责，再看代码。
3. 代码只表达控制逻辑，不负责替代 PLECS 的功率器件仿真。
4. PLECS 官方模型放在最后对照，因为它一开始就包含电机、逆变器、电流控制器和传感器。

Step 01 到 Step 07 的 `.plecs` 是信号级教学模型，统一结构是：

```text
Clock -> StepLogic(C-Script) -> Demux -> Scope
```

它们用来观察控制变量，不模拟真实绕组电流和机械负载。Step 08 才是完整 BLDC 电机仿真。

实验记录统一写在：

```text
D:\1codex\BLDC\learning_model\steps\EXPERIMENT_LOG.md
```

## 为什么不直接手写多个 `.plecs` 文件

之前目录里的 `archive` 已经保留过一个手写模型失败案例。问题不是 BLDC 原理，而是 PLECS 文件结构、组件名称和版本兼容容易出错。

所以现在的路线是：

```text
最简 C/文档模型
  -> 在脑中建立唯一职责
  -> 按 README 在 PLECS 图形界面搭对应模块
  -> 最后对照官方可运行模型
```

这样学习路径更稳，也更容易定位问题。

## 重新生成模型

如果修改了生成脚本，可以运行：

```powershell
powershell -ExecutionPolicy Bypass -File D:\1codex\BLDC\learning_model\steps\generate_step_plecs.ps1
```

如果要批量验证 PLECS 能否加载这些模型，请先启动 PLECS_server，再运行：

```powershell
python D:\1codex\BLDC\learning_model\steps\test_step_plecs_models.py
```

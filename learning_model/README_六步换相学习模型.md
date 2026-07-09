# BLDC 一步一步最简学习模型

## 先从这里开始

现在学习入口改成最简模型路线：

```text
D:\1codex\BLDC\learning_model\steps\README.md
```

不要一开始就打开官方 PLECS 完整模型。官方模型能跑，但它同时包含电机、三相桥、电流控制器、角度传感器和脉冲生成器，不适合作为第一步教材。

## 新路线

| 步骤 | 学什么 | 对应目录 |
|---|---|---|
| 01 | 三相桥 6 个开关 | `steps\step_01_three_phase_bridge` |
| 02 | 六步换相表 | `steps\step_02_six_step_table` |
| 03 | 开环换相 | `steps\step_03_open_loop_commutation` |
| 04 | 霍尔换相 | `steps\step_04_hall_commutation` |
| 05 | PWM 占空比 | `steps\step_05_pwm_duty` |
| 06 | 霍尔速度估算 | `steps\step_06_speed_estimation` |
| 07 | 速度 PI | `steps\step_07_speed_pi` |
| 08 | PLECS 完整模型对照 | `steps\step_08_plecs_full_model` |

每一步只新增一个职责。先看该目录的 `README.md`，再打开对应 `.plecs` 看 Scope，最后再看里面的最小 C 逻辑。

Step 01 到 Step 07 都已经有对应的信号级 PLECS 教学模型。它们统一用：

```text
Clock -> StepLogic(C-Script) -> Demux -> Scope
```

这 7 个模型看控制变量，不假装模拟真实电机。Step 08 才是完整 BLDC 电机模型。

实验记录写在：

```text
D:\1codex\BLDC\learning_model\steps\EXPERIMENT_LOG.md
```

## 官方 PLECS 模型放到最后看

官方对照模型仍然保留：

```text
D:\1codex\BLDC\learning_model\bldc_six_step_learning.plecs
```

它来自你本机 PLECS 5.0 官方示例：

```text
D:\Users\ww\Documents\Plexim\PLECS 5.0 (64 bit)\demos\brushless_dc_machine\brushless_dc_machine.plecs
```

这个官方模型之前通过过 RPC 仿真测试：

```text
SIM_OK model=bldc_six_step_learning
```

当前这轮新增的 Step 01 到 Step 08 模型已做静态检查。要做真实 PLECS 加载仿真，请先启动 PLECS_server，再运行：

```powershell
python D:\1codex\BLDC\learning_model\steps\test_step_plecs_models.py
```

## 为什么这样改

之前直接讲官方模型时，`Current controller` 和 `Current shape` 会把多个概念压在一起：

```text
theta
  -> 三相电流形状
  -> 电流控制
  -> pulses
  -> 三相逆变器
```

新路线先拆成：

```text
桥臂状态
  -> 六步表
  -> 开环/Hall 产生换相步
  -> PWM 调能量
  -> 速度估算
  -> 速度 PI
  -> PLECS 完整系统
```

这样每个现象都有唯一职责层，后续调试时也能从症状追到根因。

## 旧模型说明

旧的手写错误模型已保留在：

```text
D:\1codex\BLDC\learning_model\archive
```

不要再用它作为学习入口。


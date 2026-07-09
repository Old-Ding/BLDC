# Step 01：三相桥状态模型

## 目标

先不管电机、霍尔和 PWM，只学习三相逆变器的 6 个开关如何决定 A/B/C 三相输出状态。

## 最小数据流

```text
AH/BH/CH/AL/BL/CL
  -> 三相桥状态判断
  -> A/B/C = 正母线 / 负母线 / 悬空 / 故障
```

## 桥臂含义

```text
AH：A 相上桥
AL：A 相下桥
BH：B 相上桥
BL：B 相下桥
CH：C 相上桥
CL：C 相下桥
```

同一相里，上桥和下桥不能同时导通。

## 对应代码

```text
bridge_state.c
```

这个文件只负责把 6 路桥臂命令翻译成三相状态。它不决定换相顺序，也不处理 PWM。

## 对应 PLECS 模型

```text
D:\1codex\BLDC\learning_model\steps\step_01_three_phase_bridge\step_01_three_phase_bridge.plecs
```

Scope 里看：

```text
AH/BH/CH/AL/BL/CL
A_state/B_state/C_state
shoot_through
```

## 成功标准

你能看着任意一组桥臂命令，说出：

1. A/B/C 哪一相接正母线。
2. 哪一相接负母线。
3. 哪一相悬空。
4. 是否出现同相上下桥直通。

## 对应完整 PLECS

官方模型里的模块：

```text
2-Level IGBT Conv.
```

就是这个三相桥的封装版本。

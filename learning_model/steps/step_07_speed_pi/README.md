# Step 07：速度 PI

## 目标

把目标转速和实际转速的误差转换成 duty。速度 PI 不直接控制桥臂。

## 最小数据流

```text
target_speed_rpm
  - actual_speed_rpm
  -> PI
  -> duty
  -> PWM 层
```

## 为什么先只用 PI

速度环里 D 项容易放大 Hall 速度估算的抖动。入门模型先用 P 提供快速响应，用 I 消除长期速度误差。

## 对应代码

```text
speed_pi.c
```

这个文件只输出 duty，不判断 Hall，不处理桥臂，不做故障状态机。

## 对应 PLECS 模型

```text
D:\1codex\BLDC\learning_model\steps\step_07_speed_pi\step_07_speed_pi.plecs
```

Scope 里看：

```text
target_rpm
actual_rpm
error
integral_view
duty
```

## 成功标准

你能解释：

1. 只用 P 为什么会有稳态误差。
2. I 为什么能补偿负载造成的长期误差。
3. 积分限幅为什么能减少目标突变后的恢复过慢。

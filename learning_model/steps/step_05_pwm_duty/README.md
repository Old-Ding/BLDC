# Step 05：PWM 占空比

## 目标

在换相表已经决定“哪两相导通”后，再用 PWM 决定输出能量大小。

## 最小数据流

```text
换相表输出 gates
  + duty
  + carrier
  -> 带 PWM 的 gates
```

## 本步骤采用的简化方式

先用高边 PWM：

```text
上桥 = 换相命令 AND PWM
下桥 = 换相命令保持导通
```

例如：

```text
A+ B-
  -> AH = PWM
  -> BL = ON
```

## 对应代码

```text
pwm_duty_gate.c
```

这个文件只做 PWM 调制，不决定换相顺序，也不修正 duty 范围。duty 的范围由实验参数或速度 PI 层负责。

## 对应 PLECS 模型

```text
D:\1codex\BLDC\learning_model\steps\step_05_pwm_duty\step_05_pwm_duty.plecs
```

Scope 里看：

```text
step
duty
carrier
AH_base
AH_pwm/BH_pwm/CH_pwm
AL/BL/CL
```

## 成功标准

你能解释：

1. duty 变大，平均输出电压为什么变大。
2. PWM 改变能量大小，为什么不改变当前处于哪一步换相。
3. 死区通常属于定时器或驱动器配置，不应该塞进速度 PI。

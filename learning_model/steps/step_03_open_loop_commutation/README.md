# Step 03：开环换相

## 目标

在没有霍尔反馈时，用固定节拍推动 step 前进，观察“控制器主动制造旋转磁场”的概念。

## 最小数据流

```text
tick
  -> 开环节拍器
  -> step 0..5
  -> 六步换相表
  -> AH/BH/CH/AL/BL/CL
```

## 这个模型说明什么

开环换相能产生旋转磁场，但它不知道转子有没有跟上。

如果节拍太快、占空比太小或负载太大，真实电机可能失步。这个失步不是三相桥错了，而是缺少位置反馈。

## 对应代码

```text
open_loop_commutation.c
```

这个文件只负责按节拍推进 step。它不判断 Hall，也不计算速度。

## 对应 PLECS 模型

```text
D:\1codex\BLDC\learning_model\steps\step_03_open_loop_commutation\step_03_open_loop_commutation.plecs
```

Scope 里看：

```text
ticks_per_step
step
elec_angle_deg
AH/BH/CH/AL/BL/CL
```

## 成功标准

你能解释：

1. 为什么开环能让磁场转起来。
2. 为什么开环不保证转子一定跟上。
3. 为什么无感 BLDC 启动常需要先开环拖动。

# Step 08：回到 PLECS 完整模型

## 目标

学完前 7 个最小模型后，再打开 PLECS 官方示例，看它如何把功率级、电机、传感器和控制器连成完整闭环。

## 打开模型

```text
D:\1codex\BLDC\learning_model\steps\step_08_plecs_full_model\step_08_plecs_full_model.plecs
```

它是官方完整模型的副本，原文件仍保留在：

```text
D:\1codex\BLDC\learning_model\bldc_six_step_learning.plecs
```

## 对应关系

| 最简步骤 | PLECS 模块 |
|---|---|
| Step 01 三相桥 | `2-Level IGBT Conv.` |
| Step 02 六步换相表 | `Current controller` 内部的导通形状逻辑 |
| Step 03 开环换相 | 可作为后续自己搭建的启动逻辑 |
| Step 04 霍尔换相 | 官方模型用 `Angle Sensor/theta`，不是离散 Hall |
| Step 05 PWM duty | `Current controller -> pulses` |
| Step 06 速度估算 | `BLDC` 输出的转速可用于对照 |
| Step 07 速度 PI | 后续在控制层新增，不改功率级 |

## 先看 Scope

```text
Stator Phase：三相电流
Back EMF：反电动势
Motor：转速
Machine：电磁转矩
```

## 关键提醒

这个 PLECS 模型适合做完整系统对照，不适合作为第一步教材。它的 `Current controller / Current shape` 使用 `theta` 生成连续角度下的三相电流形状，和最小 Hall 六步模型不是同一个输入形式。

所以正确学习顺序是：

```text
先学 steps 01..07
再用 Step 08 对照 PLECS 完整模型
```

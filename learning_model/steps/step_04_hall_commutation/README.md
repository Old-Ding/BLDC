# Step 04：霍尔六步换相

## 目标

把开环的 `tick -> step` 换成 `Hall -> step/桥臂命令`。这一步开始引入位置反馈。

## 最小数据流

```text
Hall A/B/C
  -> 霍尔状态
  -> 六步换相表
  -> AH/BH/CH/AL/BL/CL
```

## 对应代码

```text
D:\1codex\BLDC\learning_model\steps\step_04_hall_commutation\six_step_commutation_hall.c
```

这个文件已经是 PLECS C-Script 风格，输入输出可以直接对应 PLECS 信号：

```text
in[0] = Hall A
in[1] = Hall B
in[2] = Hall C

out[0] = A 相上桥
out[1] = B 相上桥
out[2] = C 相上桥
out[3] = A 相下桥
out[4] = B 相下桥
out[5] = C 相下桥
```

## 为什么非法 Hall 在这里处理

`Hall -> 桥臂命令` 是换相表的唯一职责层。`000` 和 `111` 不属于 120 度三霍尔的有效扇区，所以在这里关断输出最清楚。

不要在 PWM 层、速度层再重复判断 Hall 合法性。除非未来有明确安全需求，并先说明原因。

## 对应 PLECS 模型

```text
D:\1codex\BLDC\learning_model\steps\step_04_hall_commutation\step_04_hall_commutation.plecs
```

Scope 里看：

```text
HallA/HallB/HallC
hall_state
valid
AH/BH/CH/AL/BL/CL
```

## 成功标准

你能看到任意 Hall 状态，就写出对应导通相，比如：

```text
Hall = 101 -> A+ B-
Hall = 001 -> A+ C-
```

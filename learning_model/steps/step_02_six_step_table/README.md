# Step 02：六步换相表

## 目标

先不用霍尔，也不用时间，只学习“第几步换相”对应哪两个桥臂导通。

## 最小数据流

```text
step 0..5
  -> 六步换相表
  -> AH/BH/CH/AL/BL/CL
```

## 正转换相表

| step | 导通状态 | 桥臂命令 |
|---:|---|---|
| 0 | A+ B- | AH + BL |
| 1 | A+ C- | AH + CL |
| 2 | B+ C- | BH + CL |
| 3 | B+ A- | BH + AL |
| 4 | C+ A- | CH + AL |
| 5 | C+ B- | CH + BL |

## 对应代码

```text
six_step_table.c
```

这个文件只负责 `step -> gates`。它不关心 step 来自时间、霍尔还是别的传感器。

## 对应 PLECS 模型

```text
D:\1codex\BLDC\learning_model\steps\step_02_six_step_table\step_02_six_step_table.plecs
```

Scope 里看：

```text
step
AH/BH/CH/AL/BL/CL
```

## 成功标准

你能从 step 推出桥臂命令，并能解释为什么每一步只有两相参与导通，第三相悬空。

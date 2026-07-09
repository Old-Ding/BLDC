# Step 06：霍尔速度估算

## 目标

从 Hall 边沿间隔计算机械转速，为速度闭环准备反馈量。

## 最小数据流

```text
Hall 边沿周期
  + 极对数
  -> actual_speed_rpm
```

## 公式

三霍尔六步换相中：

```text
每机械圈 Hall 边沿数 = 极对数 * 6
rpm = 60 / (边沿周期秒 * 极对数 * 6)
```

例如 4 对极，Hall 边沿周期为 2 ms：

```text
rpm = 60 / (0.002 * 4 * 6) = 1250 rpm
```

## 对应代码

```text
hall_speed_estimator.c
```

这个文件只做速度估算，不输出 duty，也不改换相表。

## 对应 PLECS 模型

```text
D:\1codex\BLDC\learning_model\steps\step_06_speed_estimation\step_06_speed_estimation.plecs
```

Scope 里看：

```text
edge_period_ms
pole_pairs
edges_per_rev
rpm
```

## 成功标准

你能解释：

1. 为什么极对数越多，同样机械转速下 Hall 边沿越密。
2. 为什么低速时速度更新慢。
3. 为什么速度环周期不能盲目设得比反馈更新还快。

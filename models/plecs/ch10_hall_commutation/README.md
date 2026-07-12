# 第 10 章 PLECS Hall 换相与偏置模型

模型沿用第 07 章真实 IGBT bridge 与 BLDC Machine，将时间换相 C-Script 替换为 `Hall commutator`：

```text
Angle Sensor -> electrical sector -> offset -> six-step table -> IGBT bridge
```

`commutation_offset_steps` 扫描 0..5，`table_direction` 切换表方向，`hall_enable=0` 形成全关基线。

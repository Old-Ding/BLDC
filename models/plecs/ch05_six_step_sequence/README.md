# 第 05 章 PLECS 六步序列模型

该模型在第 02 章真实 IGBT 桥和 BLDC Machine 前加入 PLECS C-Script 六步表。

模型变量：

- `step_period_s`：每个 60 电角度状态保持时间；小于等于 0 时全关。
- `sequence_direction`：非负为正序，负值为反序。

模型内 `Clock -> C-Script -> 三值相命令 -> IGBT bridge` 是唯一时间数据流。

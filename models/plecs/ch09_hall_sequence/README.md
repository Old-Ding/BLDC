# 第 09 章 PLECS Hall 序列模型

模型从第 03 章角度模型派生。桥臂全关，`Hall encoder` C-Script 把 PLECS Angle Sensor 的机械角转换为机械角、Hall A/B/C 和 valid 五路向量，并通过原第 7 个顶层输出导出。

合法正转表为 `{5,1,3,2,6,4}`；`force_invalid` 可强制 `invalid_code=0/7`。

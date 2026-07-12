# 第 12 章 PLECS Hall 测速模型

模型扩展第 09 章仿真窗口到 250 ms，输出机械角、Hall A/B/C 和 valid。速度估算、滤波与超时由 Python 对 PLECS 边沿执行，PLECS Machine 的 `speed_rad_s` 作为交叉验证真值。

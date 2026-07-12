# 第 08 章 PLECS 开环失步诊断模型

该模型沿用第 07 章真实 IGBT bridge、BLDC Machine 和频率积分启动器，新增 PLECS 原生 `Step` 负载源：

```text
频率斜坡 -> 开环六步 -> IGBT bridge -> BLDC Machine
                                   ^
                     Step -> Torque 机械端口
```

`load_before_Nm`、`load_after_Nm` 和 `load_step_time_s` 由 XML-RPC 场景设置。机械角仍由 PLECS Angle Sensor 导出；累计滑移在 Python 中使用解包角度计算。

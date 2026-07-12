# 第 03 章 PLECS 角度模型

该模型由第 02 章真实功率级模型派生，增加：

- BLDC Machine 极对数参数 `pole_pairs`；
- PLECS Angle Sensor 顶层输出 `mechanical_angle_rad`；
- 机械角原生 Scope。

运行：

```powershell
python .\scripts\build_ch02_plecs_model.py
python .\scripts\build_ch03_plecs_model.py
python .\scripts\ch03_plecs_electrical_angle.py
```

RPC 返回 15 路信号。第 15 路是 PLECS 原始机械角，范围在 `[-pi, pi]`；连续角度和电角度由场景脚本生成。

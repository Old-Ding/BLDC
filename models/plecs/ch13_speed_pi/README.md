# 第 13 章 PLECS 速度 PI 模型

`ch13_speed_pi.plecs` 从第 11 章 PWM 模型派生，在 `Speed PI Hall PWM` C-Script 中加入一个连续积分状态：

```text
Machine speed -> speed error -> PI + clamp -> PWM Hall phase command -> bridge -> Machine
```

`OutputFcn` 计算 duty、PWM 和三值相命令，`DerivativeFcn` 只负责积分状态及条件积分抗饱和。模型使用 PLECS Machine 实际速度作为本章反馈，以隔离 Hall 边沿量化；完整 Hall 反馈闭环见第 14 章。

运行入口：

```powershell
python .\scripts\build_ch13_plecs_model.py
python .\scripts\ch13_plecs_speed_pi.py
```

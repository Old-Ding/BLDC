# 第 14 章 PLECS 完整 Hall 六步闭环模型

模型在第 13 章速度 PI 基础上，把 PI 反馈改为同一 C-Script 内的 Hall 扇区边沿测速：

```text
rotor angle -> Hall sector -> edge timing -> speed PI -> PWM six-step -> bridge -> BLDC
```

顶层同时输出：

- `hall_speed_feedback_rad_s`：控制器实际反馈；
- `speed_rad_s`：PLECS Machine 验收真值；
- 三相电流、反电动势、转矩、相命令、线电压和机械角。

非法 Hall 窗口内三相命令全关、积分冻结；恢复后第一条合法边沿只重新同步，第二条完整边沿才计算速度。

运行入口：

```powershell
python .\scripts\build_ch14_plecs_model.py
python .\scripts\ch14_plecs_complete_closed_loop.py
```

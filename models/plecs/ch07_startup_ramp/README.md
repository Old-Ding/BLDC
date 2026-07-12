# 第 07 章 PLECS 定位与频率斜坡模型

该模型从第 03 章真实 IGBT 桥与 BLDC Machine 模型派生，加入仓库自编的 `Startup angle generator` C-Script：

```text
Clock -> 定位/频率积分/60 度量化 -> 三值相命令 -> IGBT bridge -> BLDC Machine
```

模型参数 `alignment_s`、`start_frequency_Hz`、`end_frequency_Hz` 和 `ramp_duration_s` 由 XML-RPC 场景设置。C-Script 对频率积分，保证变频过程中命令电角连续。

运行：

```powershell
python .\scripts\build_ch02_plecs_model.py
python .\scripts\build_ch03_plecs_model.py
python .\scripts\build_ch07_plecs_model.py
python .\scripts\ch07_plecs_startup_ramp.py
```

RPC 返回 15 路 PLECS 信号。Python 另行生成解包机械角、连续命令电角、命令频率和相位差列。

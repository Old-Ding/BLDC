# 第 11 章 PLECS PWM 与 deadtime 模型

`Hall PWM commutator` 用 `CurrentTime` 生成 10 kHz 单极性 PWM。正相高侧按 duty 开关，负相低侧连续导通，Hall 扇区变化时全关 `deadtime_s`。

该模型不包含同桥臂同步整流互补 PWM，因此 deadtime 证据限定为高侧开通延迟和换相保护间隔。

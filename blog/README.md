# BLDC 教程文章索引

本目录存放面向读者的正式教程。实验模型、CSV、图片、报告和复现文档先在仓库完成，再进入 CSDN 转换。

## 阶段 A：功率级与电机物理基础

| 篇章 | 标题 | 文件 | 状态 |
|---:|---|---|---|
| 00 | BLDC 完整学习路线 | [`00-bldc-learning-route.md`](00-bldc-learning-route.md) | 路线入口 |
| 01 | 让 BLDC 在 PLECS 里真正转起来 | [`01-bldc-control-chain.md`](01-bldc-control-chain.md) | PLECS 实验包完成，三轮复核通过 |
| 02 | 三相桥的上桥、下桥与悬空 | [`02-three-phase-bridge.md`](02-three-phase-bridge.md) | 真实 PLECS 功率桥，三轮复核通过 |
| 03 | 电机参数、机械角度和电角度 | [`03-mechanical-and-electrical-angle.md`](03-mechanical-and-electrical-angle.md) | PLECS 极对数实验，三轮复核通过 |
| 04 | 梯形反电动势与电磁转矩 | [`04-back-emf-and-torque.md`](04-back-emf-and-torque.md) | PLECS 功率等式实验，三轮复核通过 |
| 05 | 120° 导通和六步换相表 | [`05-six-step-commutation-table.md`](05-six-step-commutation-table.md) | PLECS 六步序列实验，三轮复核通过 |

## 后续阶段

| 阶段 | 篇章 | 目标 |
|---|---|---|
| B | 06-14 | 开环启动、Hall、PWM、测速、速度 PI 和完整六步闭环 |
| C | 15-22 | C 编译、单元测试、定点化、外设映射、ISR、保护、CI/HIL 和硬件上电 |
| D | 23-29 | 反电动势过零、消隐滤波、无感接管、提前角和硬件验证 |
| E | 30-36 | Clarke/Park、电流环、SVPWM、FOC、弱磁和路线比较 |

完整章节契约见 [`../docs/series-plan.md`](../docs/series-plan.md)。

## 正式章节完成标准

1. 读者能说明核心对象的输入、内部作用、输出和证据来源。
2. 涉及开关、功率级或电机响应时，使用 PLECS/Simulink 主图。
3. 至少两个有区分度的场景，并提供逐点数据和指标报告。
4. 参数表包含数值、单位、用途和限制。
5. 图后说明观察顺序、教学结论和不要误读成什么。
6. PowerShell 复现命令能重新生成结果。
7. 文件索引位于核心模型和结果之后。
8. 工程、视觉和读者理解复核能列出实际检查对象、发现项和修改结果。

## CSDN 交付规则

GitHub 同步并验证公开图片链接后，再生成 `blog/csdn` 发布包。默认只保存 CSDN 草稿，最终发布必须单独确认。

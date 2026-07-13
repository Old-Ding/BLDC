# BLDC 教程文章索引

本目录存放面向读者的正式教程。实验模型、CSV、图片、报告和复现文档先在仓库完成，再进入 CSDN 转换。

## 阶段 A：功率级与电机物理基础

| 篇章 | 标题 | 文件 | 状态 |
|---:|---|---|---|
| 00 | BLDC 完整学习路线 | [`00-bldc-learning-route.md`](00-bldc-learning-route.md) | 路线入口 |
| 01 | 电流还在，BLDC 为什么会减速 | [`01-bldc-control-chain.md`](01-bldc-control-chain.md) | PLECS 实验包完成，三轮复核通过 |
| 02 | 三相桥的上桥、下桥与悬空 | [`02-three-phase-bridge.md`](02-three-phase-bridge.md) | 真实 PLECS 功率桥，三轮复核通过 |
| 03 | 电机参数、机械角度和电角度 | [`03-mechanical-and-electrical-angle.md`](03-mechanical-and-electrical-angle.md) | PLECS 极对数实验，三轮复核通过 |
| 04 | 梯形反电动势与电磁转矩 | [`04-back-emf-and-torque.md`](04-back-emf-and-torque.md) | PLECS 功率等式实验，三轮复核通过 |
| 05 | 120° 导通和六步换相表 | [`05-six-step-commutation-table.md`](05-six-step-commutation-table.md) | PLECS 六步序列实验，三轮复核通过 |

## 阶段 B：开环启动与 Hall 六步闭环

| 篇章 | 标题 | 文件 | 状态 |
|---:|---|---|---|
| 06 | 开环电角度如何旋转 | [`06-open-loop-electrical-angle.md`](06-open-loop-electrical-angle.md) | PLECS 开环频率实验，三轮复核通过 |
| 07 | 静止启动与加速斜坡 | [`07-startup-ramp.md`](07-startup-ramp.md) | PLECS 定位/斜坡实验，三轮复核通过 |
| 08 | 开环失步根因与诊断 | [`08-open-loop-desynchronization.md`](08-open-loop-desynchronization.md) | PLECS 三场景，三轮复核通过 |
| 09 | Hall 序列、扇区与方向 | [`09-hall-sequence-and-direction.md`](09-hall-sequence-and-direction.md) | 正反转与非法码，三轮复核通过 |
| 10 | Hall 换相与安装偏置 | [`10-hall-commutation-offset.md`](10-hall-commutation-offset.md) | 偏置扫参与全关边界，三轮复核通过 |
| 11 | PWM 占空比和死区 | [`11-pwm-duty-and-deadtime.md`](11-pwm-duty-and-deadtime.md) | 真实 10 kHz PWM，三轮复核通过 |
| 12 | Hall 边沿测速与滤波 | [`12-hall-edge-speed-estimation.md`](12-hall-edge-speed-estimation.md) | 五速度/方向/超时场景，三轮复核通过 |
| 13 | 速度 PI、限幅与抗饱和 | [`13-speed-pi-antiwindup.md`](13-speed-pi-antiwindup.md) | 四场景 PLECS PI，三轮复核通过 |
| 14 | 完整 Hall 六步闭环 | [`14-complete-hall-closed-loop.md`](14-complete-hall-closed-loop.md) | 五场景综合验收，三轮复核通过 |

## 后续阶段

| 阶段 | 篇章 | 目标 |
|---|---|---|
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

# 第 01 章 PLECS BLDC 基准实验报告

## 参数摘要

| 参数 | 数值 | 单位 |
|---|---:|---|
| 直流母线电压 | 300 | V |
| 电流参考 | 5 | A |
| 初始机械角速度 | 300 | rad/s |
| 仿真时长 | 0.3 | s |
| 输出采样间隔 | 0.5 | ms |

## 场景结果

| 场景 | 负载转矩/Nm | 相电流峰值/A | 尾段转速/rpm | 尾段电磁转矩/Nm | 结果 |
|---|---:|---:|---:|---:|---|
| nominal_load | 3.000 | 5.9941 | 3490.23 | 2.9936 | PASS |
| overload | 6.000 | 5.9982 | 271.99 | 4.0098 | PASS |

## 判定边界

- `nominal_load`：电磁转矩跟随 3 Nm 负载，尾段转速保持在 320 rad/s 以上。
- `overload`：6 Nm 负载超过 5 A 电流参考所能提供的转矩，预期现象是电流受限而转速塌落。
- PASS 表示模型出现了场景定义的预期行为；过载场景的 PASS 不表示电机仍能维持转速。

## 证据来源

- PLECS trace：`waveforms/01-bldc-control-chain/ch01_bldc_baseline_scope.trace`
- 逐点数据：`waveforms/01-bldc-control-chain/plecs_*.csv`
- 汇总数据：`waveforms/01-bldc-control-chain/plecs_baseline_summary.csv`

该模型验证电流换相、三相逆变器、BLDC 电磁模型和机械负载之间的因果链。
速度 PI、Hall 量化、死区、器件损耗和硬件保护不在本实验的判定范围内。

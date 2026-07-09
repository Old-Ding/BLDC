# 第 02 篇测试报告：三相桥状态模型

生成时间：2026-07-09 17:20:27

## 参数摘要

- 采样周期：50 us
- 每个场景采样点：80
- 单场景持续时间：4.000 ms
- 状态编码：HIGH=1，LOW=-1，FLOAT=0，FAULT=2
- 源码参照：`learning_model/steps/step_01_three_phase_bridge/bridge_state.c`
- 生成脚本：`scripts/ch02_three_phase_bridge_tests.m`

## 测试结果

| 场景 | Gates | 期望状态 | 实际状态 | 期望直通 | 实际直通 | 结果 | 说明 |
|---|---|---|---|---:|---:|---|---|
| `normal_AH_BL` | AH=1 BH=0 CH=0 AL=0 BL=1 CL=0 | A=HIGH B=LOW C=FLOAT | A=HIGH B=LOW C=FLOAT | 0 | 0 | PASS | A 相接正母线，B 相接负母线，C 相悬空 |
| `normal_BH_CL` | AH=0 BH=1 CH=0 AL=0 BL=0 CL=1 | A=FLOAT B=HIGH C=LOW | A=FLOAT B=HIGH C=LOW | 0 | 0 | PASS | B 相接正母线，C 相接负母线，A 相悬空 |
| `normal_CH_AL` | AH=0 BH=0 CH=1 AL=1 BL=0 CL=0 | A=LOW B=FLOAT C=HIGH | A=LOW B=FLOAT C=HIGH | 0 | 0 | PASS | C 相接正母线，A 相接负母线，B 相悬空 |
| `all_off` | AH=0 BH=0 CH=0 AL=0 BL=0 CL=0 | A=FLOAT B=FLOAT C=FLOAT | A=FLOAT B=FLOAT C=FLOAT | 0 | 0 | PASS | 六个桥臂全关，三相都悬空 |
| `fault_AH_AL` | AH=1 BH=0 CH=0 AL=1 BL=0 CL=0 | A=FAULT B=FLOAT C=FLOAT | A=FAULT B=FLOAT C=FLOAT | 1 | 1 | PASS | A 相上下桥同时导通，进入直通故障 |
| `fault_BH_BL` | AH=0 BH=1 CH=0 AL=0 BL=1 CL=0 | A=FLOAT B=FAULT C=FLOAT | A=FLOAT B=FAULT C=FLOAT | 1 | 1 | PASS | B 相上下桥同时导通，进入直通故障 |

## 曲线文件

| 文件 | 作用 |
|---|---|
| `assets/02-three-phase-bridge/bridge_state_scenarios.png` | 六个 gate、三相状态和直通标志的场景时序 |
| `assets/02-three-phase-bridge/bridge_state_fault_matrix.png` | 正常导通与直通故障的状态矩阵对比 |
| `waveforms/02-three-phase-bridge/bridge_state_timeseries.csv` | 图 1 背后的逐点数据 |
| `waveforms/02-three-phase-bridge/bridge_state_summary.csv` | 场景级 PASS/FAIL 汇总 |

## 边界说明

本报告只验证 6 路桥臂命令到 A/B/C 相状态和直通标志的映射。它不验证死区时间、驱动芯片保护、电流变化、电机反电动势或机械负载响应。

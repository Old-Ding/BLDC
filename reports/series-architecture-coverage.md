# 系列架构覆盖检查

检查日期：2026-07-15
候选文件：`docs/series-architecture.md`
候选版本：`v7-local-candidate`

## 1. 模板与公开口吻

| 检查项 | 结果 |
|---|---|
| 模板变量 | PASS，未命中 |
| 模板词与 CSDN 默认模板 | PASS，未命中 |
| 15 篇博客公开口吻脚本 | PASS，0 命中 |
| `git diff --check` | PASS |

## 2. 前置 ID 解析

| 项目 | 数量 | 结果 |
|---|---:|---|
| 注册表 ID | 18 | PASS |
| 单章前置 ID 行 | 15 | PASS |
| 前置 ID 引用 | 38 | PASS |
| 未解析前置 ID | 0 | PASS |

注册表覆盖 `ENTRY-*`、`K-*` 和 `CAPABILITY_OUTPUT-*` 三类节点。章节前置没有直接引用宽泛的 `CAP-*` 终局能力。

## 3. DAG 与职责边界

| 检查项 | 结果 |
|---|---|
| 知识依赖图方向 | PASS，入口知识先于首次概念，首次概念先于能力产出 |
| 已知循环依赖 | PASS，未发现循环 |
| DAG 覆盖章节前置 ID | PASS，`reports/series-architecture-dag-check.json` 中 `missing_from_dag=[]`、`owner_order_violations=[]`、`cycle=[]` |
| 功率级、电机对象、反馈/控制器职责 | PASS，分别在 `SYS-DC`、`SYS-MOTOR`、`SYS-FEEDBACK` 中定义 |
| 仿真、C 编译、MCU、HIL、硬件边界 | PASS，C14 只声明 PLECS 仿真闭环；C 编译、MCU、HIL 和硬件验证仍明确留到后续阶段 |

## 4. 能力到章节覆盖

| 能力 ID | 建设章节 | 集成章节 | 覆盖结果 |
|---|---|---|---|
| CAP-CHAIN-01 | C01、C03、C04 | C14 | PASS |
| CAP-BRIDGE-01 | C02 | C05、C14 | PASS |
| CAP-SIXSTEP-01 | C03、C04、C05 | C10、C14 | PASS |
| CAP-OPENLOOP-01 | C06、C07、C08 | C14 | PASS，C08 PLECS 同一观测链覆盖同步正例和三类失步 |
| CAP-HALL-01 | C09、C10 | C14 | PASS，C10/C14 模型直接消费 Hall interface 并原生导出 Hall code、decoded sector、合法转移、enable/fault |
| CAP-PWM-01 | C11 | C13、C14 | PASS |
| CAP-SPEED-01 | C12 | C14 | PASS，C12 PLECS 原生测速覆盖 1/4 极对、正反向、高速和停止超时 |
| CAP-PI-01 | C13 | C14 | PASS |
| CAP-INTEGRATION-01 | C01-C14 | C14 | PASS，C14 PLECS 原生导出 Hall/control/gate 诊断，5/5 场景和 5/5 mutation 通过 |
| CAP-FW-01 | C15-C22 | C22 | FUTURE，第一季不声明完成 |
| CAP-SENSORLESS-01 | C23-C29 | C29 | FUTURE，第一季不声明完成 |
| CAP-FOC-01 | C30-C36 | C36 | FUTURE，第一季不声明完成 |

## 5. 章节到能力覆盖

| 章节 | 核心问题数量 | 推进能力 | 结果 |
|---|---:|---|---|
| C00 | 1 | 第一季导航 | PASS |
| C01 | 1 | CAP-CHAIN-01 | PASS |
| C02 | 1 | CAP-BRIDGE-01 | PASS |
| C03 | 1 | CAP-SIXSTEP-01 | PASS |
| C04 | 1 | CAP-CHAIN-01、CAP-SIXSTEP-01 | PASS |
| C05 | 1 | CAP-SIXSTEP-01、CAP-BRIDGE-01 | PASS |
| C06 | 1 | CAP-OPENLOOP-01 | PASS |
| C07 | 1 | CAP-OPENLOOP-01 | PASS |
| C08 | 1 | CAP-OPENLOOP-01 | PASS |
| C09 | 1 | CAP-HALL-01 | PASS |
| C10 | 1 | CAP-HALL-01、CAP-SIXSTEP-01 | PASS |
| C11 | 1 | CAP-PWM-01 | PASS |
| C12 | 1 | CAP-SPEED-01 | PASS |
| C13 | 1 | CAP-PI-01、CAP-PWM-01 | PASS |
| C14 | 1 | CAP-INTEGRATION-01 | PASS |

## 6. 图注与掌握标准

| 检查项 | 结果 |
|---|---|
| 单章契约包含最小心智模型 | PASS |
| 单章契约包含正常与边界场景 | PASS |
| 单章契约包含模型/源码、结果数据、图片、报告/复现文档 | PASS |
| 单章契约包含图注契约 | PASS |
| 单章契约包含目标掌握级别 | PASS |
| 单章契约包含可测过关标准 | PASS |
| 证据/掌握映射覆盖 C01-C14 | PASS |
| 学习者独立验收任务 | PASS，已与系统验收分离，覆盖 CAP-CHAIN-01 到 CAP-INTEGRATION-01 |
| C05 六步物理 oracle | PASS，包含解析梯形反电动势、桥臂/绕组电流路径、6 个扇区、3 类 mutation |
| C09 Hall 转移 oracle | PASS，覆盖相邻正转、相邻反转、保持、非法码和非相邻合法跳码 |
| C08 同步/失步分类 | PASS，PLECS 同一观测链覆盖 `sync_follow`、`gentle_ramp`、`overfast_ramp` 和 `load_step` |
| C12 Hall 测速公式 | PASS，`omega_m = s * (pi/3) / (pole_pairs * delta_t)` 由事件 oracle 和 4 极对 PLECS 原生测速共同覆盖 |
| C14 场景量化验收 | PASS，PLECS 原生诊断五正式场景 PASS、五 mutation `FAIL_DETECTED` |

## 7. 当前待审状态

本文件只说明候选架构的覆盖检查结果。正式状态必须由三轨独立审查记录给出；在三轨通过前，不得把候选写成 `ARCHITECTURE_READY`。

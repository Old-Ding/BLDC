# BLDC 第一季架构 v7 本地验证记录

状态：ARCHITECTURE_CANDIDATE

本记录用于冻结包前的本地可复现检查，不代表独立三轨审查通过。

## 1. PLECS 与判据重跑

| 检查 | 结果 |
|---|---|
| `python scripts\ch05_six_step_physical_oracle.py` | PASS，6/6 C 表匹配，3/3 mutation `FAIL_DETECTED` |
| `python scripts\ch08_desync_classifier_oracle.py` | PASS，分类 oracle 通过 |
| `python scripts\ch08_plecs_desync.py` | PASS，4/4 场景，含 `sync_follow` 同步正例 |
| `python scripts\build_ch10_plecs_model.py` | PASS，生成 C10 PLECS 模型 |
| `python scripts\ch10_plecs_hall_commutation.py` | PASS，8/8 场景，25 路信号 |
| `python scripts\build_ch12_plecs_model.py` | PASS，生成 C12 PLECS 模型 |
| `python scripts\ch12_plecs_hall_speed.py` | PASS，6/6 场景，含 `medium_100_pp4`，27 路信号 |
| `python scripts\ch12_hall_speed_event_oracle.py` | PASS，7/7 事件 oracle |
| `python scripts\build_ch14_plecs_model.py` | PASS，生成 C14 PLECS 模型 |
| `python scripts\ch14_plecs_complete_closed_loop.py` | PASS，5/5 场景，35 路信号 |
| `python scripts\ch14_acceptance_check.py` | PASS，正式场景与 mutation 检出均通过 |

## 2. 图像后处理

| 检查 | 结果 |
|---|---|
| `matlab -batch "run('scripts/ch08_desync_postprocess.m'); run('scripts/ch12_hall_speed_postprocess.m'); run('scripts/ch14_closed_loop_postprocess.m');"` | PASS，重生成 C08、C12、C14 MATLAB 图 |

## 3. 架构与渲染门禁

| 检查 | 结果 |
|---|---|
| `python scripts\check_series_architecture_dag.py` | PASS，`missing_from_dag=[]`、`unresolved_prerequisite_ids=[]`、`owner_order_violations=[]`、`cycle=[]` |
| `node scripts\render_series_architecture_review.js` | PASS，6 个 viewport、4 个 diagram、8 个 contract 截图 |
| `reports/renders/series-architecture-render-check.json` | PASS，4/4 图无节点越界、无节点重叠、无 edge list 裁剪、无页面溢出，最小字体 16 px |
| public voice | PASS，17 个 Markdown 输入 0 命中 |
| `git diff --check` | PASS |

## 4. 当前证据边界

- v7 候选只声明第一季 PLECS 仿真、CSV、MATLAB 后处理和本地报告范围内的闭环证据。
- C14 可作为后续 C15 主机侧测试参考，不替代 C 编译、MCU 定时器、HIL 或硬件上电证据。
- 下一步必须冻结 `series-architecture-v7-local` packet，并用 `gpt-5.6-sol`、`gpt-5.6-terra`、`gpt-5.5` 各跑一轮独立三轨审查。

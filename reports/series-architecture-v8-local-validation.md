# BLDC 第一季架构 v8 本地验证记录

状态：ARCHITECTURE_CANDIDATE

本记录用于修复 v7 reader-comprehension 轨 `READ-01` 后的本地可复现检查，不代表独立三轨审查通过。

## 1. v7 审查阻断项修复

| Finding | 处理 |
|---|---|
| READ-01 | C08 的 `sync_follow` 在 PLECS 报告中为同步正例，但分类 oracle 仍按旧阈值判为失步。已把 C08 分类责任集中到 `scripts/ch08_desync_classifier_oracle.py`，并让 `scripts/ch08_plecs_desync.py` 调用同一分类函数。 |

## 2. C08 重跑结果

| 检查 | 结果 |
|---|---|
| `python scripts\ch08_plecs_desync.py` | PASS，4/4 PLECS 场景，`sync_follow` 为 `SYNC_FOLLOW_CONFIRMED`，三类失步为 `DESYNC_CONFIRMED` |
| `python scripts\ch08_desync_classifier_oracle.py` | PASS，信号级参考和 4 个 PLECS 场景均与期望分类一致 |
| `matlab -batch "run('scripts/ch08_desync_postprocess.m');"` | PASS，重生成 C08 MATLAB 图 |

## 3. 架构与渲染门禁

| 检查 | 结果 |
|---|---|
| `python scripts\check_series_architecture_dag.py` | PASS，`missing_from_dag=[]`、`unresolved_prerequisite_ids=[]`、`owner_order_violations=[]`、`cycle=[]` |
| `node scripts\render_series_architecture_review.js` | PASS，6 个 viewport、4 个 diagram、8 个 contract 截图 |
| public voice | PASS，17 个 Markdown 输入 0 命中 |
| `git diff --check` | PASS after CRLF normalization |

## 4. 当前证据边界

- v8 候选只声明第一季 PLECS 仿真、CSV、MATLAB 后处理和本地报告范围内的闭环证据。
- C08 同步/失步判断以速度比和累计滑移为主判据；负转矩占比只辅助观察转矩脉动，不单独否决同步。
- C14 可作为后续 C15 主机侧测试参考，不替代 C 编译、MCU 定时器、HIL 或硬件上电证据。
- 下一步必须冻结 `series-architecture-v8-local` packet，并重新执行正式三轨审查。

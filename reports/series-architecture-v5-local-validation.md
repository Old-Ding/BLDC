# series-architecture-v5 本地验证记录

日期：2026-07-15

## 1. 可运行检查

| 检查 | 结果 |
|---|---|
| `python scripts\ch05_six_step_physical_oracle.py` | PASS，6/6 C 表匹配，3/3 mutation 检出。 |
| `python scripts\ch09_hall_transition_oracle.py` | PASS，6/6 Hall 转移用例通过。 |
| `python scripts\check_series_architecture_dag.py` | PASS，`missing_from_dag=[]`。 |
| `python scripts\ch08_desync_classifier_oracle.py` | PASS，4 行分类检查通过。 |
| `python scripts\ch12_hall_speed_event_oracle.py` | PASS，7 个事件 oracle 用例通过。 |
| `python scripts\ch14_acceptance_check.py` | PASS，五个正式场景通过，五类 mutation 均 `FAIL_DETECTED`。 |
| `node scripts\render_series_architecture_review.js` | PASS，6 个页面视图、4 个图视图、8 个 contract 截图生成。 |
| `check_public_voice.ps1` | PASS，19 个 GitHub/source Markdown 文件 0 命中。 |
| Markdown 占位扫描 | PASS，排除历史冻结包后 0 命中。 |
| `git diff --check` | PASS。 |

## 2. 当前环境边界

| 项 | 结果 |
|---|---|
| PLECS XML-RPC `localhost:1080` | `PLECS_RPC_NOT_READY: timed out` |
| 本轮是否重跑 C08/C12/C14 PLECS | 否 |
| 本轮新增证据类型 | 现有 PLECS CSV 的离线分类、事件 oracle、验收谓词和诊断 CSV |

## 3. 仍需 PLECS 重跑的项目

| 项 | 原因 |
|---|---|
| C08 PLECS 同步正例 | 当前三个 PLECS 场景均为失步，信号级同步夹具不能替代 PLECS 电机仿真。 |
| C12 `medium_100_pp4` | 脚本已加入 4 极对场景，当前环境没有 PLECS RPC，尚未生成 PLECS CSV。 |
| C14 模型内 Hall 链诊断 | 当前诊断 CSV 来自已有 CSV 后处理；正式闭环证据需要模型直接输出 Hall A/B/C、Hall code、合法转移、fault、enable 和六路门极。 |

packet_hash_before

`120f74ef0829dddc9506042dcd138f97bcc17caafc45f08bb0b8396ee69f3605`

packet_validation_before: PASS

Command: `test_review_snapshot.ps1 ...`
Result: exit code `0`; `SNAPSHOT_VALID`; `file_count=252`; manifest SHA-256 matched.

reviewed_files

See subagent raw notification for grouped full manifest coverage. The reviewer grouped all manifest paths by directory and noted review depth for `*-review.md` files.

findings

ID: SA-001; Severity: P1; Location: `docs/series-architecture.md:131-174,645-669`, `models/plecs/ch14_complete_hall_closed_loop/ch14_complete_hall_closed_loop.plecs:661-690`, `scripts/ch14_plecs_complete_closed_loop.py:25-44`; Evidence: C14 控制块只有实际速度和机械角两个输入，直接以 `theta=Input(1)*pole_pairs` 生成 sector；所谓非法 Hall 是时间窗布尔量，没有 Hall A/B/C、Hall code、合法转移事件、decoder fault 或 safety enable。`alignment_s/start_frequency_Hz/end_frequency_Hz/ramp_duration_s` 被脚本传入却未进入控制块参数或执行逻辑；原始 `invalid` 条件还分别在 OutputFcn 和 DerivativeFcn 中重复计算。 Failure mechanism: C14 绕过了架构声明的 Hall 解码、合法转移、测速、安全判定和启动链，因此当前数据只能证明“机械角量化反馈闭环”，不能证明 CAP-HALL-01/CAP-INTEGRATION-01 的完整 Hall 链，也违反唯一职责层和禁止重复防护的契约。 Required correction: 在唯一 Hall 解码层从 A/B/C 生成 sector、legal-event、direction、fault；测速只消费 legal-event；安全层把 fault 转为 enable；门极合成层唯一执行全关。明确实现并测试启动状态机，或删除未使用的启动参数、失败夹具和集成主张。 Verification: C14 CSV 必须可观察 Hall code、transition classification、fault、enable 和 gate output；分别注入 `000`、`111`、非相邻合法跳码及启动参数变异，证明责任链和唯一全关位置。

ID: SA-002; Severity: P1; Location: `reports/14-complete-hall-acceptance-contract.md:3,40-79`, `scripts/ch14_plecs_complete_closed_loop.py:40-49`, `docs/14-complete-hall-closed-loop-reproduce.md:27-37`, `docs/series-architecture.md:658-669`; Evidence: 契约要求正式 PASS 检查全部场景字段并执行五类失败样本，但脚本未运行任何失败样本，且漏判多项契约字段，例如零速启动的全关占比/峰值电流、目标阶跃的上升时间/高限幅占比/全关占比、过载的峰值电流/全关占比。复现文档又使用另一组更严格但不同的阈值。目标阶跃的“上升时间”从仿真起点计算，结果 `0.01347 s` 发生在 `0.12 s` 目标阶跃之前。 Failure mechanism: 被漏判字段发生回归时脚本仍可返回 `5/5 PASS`，失败检测能力和目标阶跃动态主张均未被证据证明。 Required correction: 建立唯一机器可执行验收谓词，由契约生成或与契约同源；逐场景检查全部字段；实际运行并报告五类失败样本；目标阶跃上升时间必须相对阶跃时刻定义。 Verification: 每个正式场景满足全部契约字段；五个 mutation 各自稳定 FAIL；对任一当前漏判字段做越界变异时总门禁必须失败。

ID: SA-003; Severity: P1; Location: `docs/series-architecture.md:483-505`, `scripts/ch08_plecs_desync.py:131-145`, `waveforms/08-open-loop-desync/plecs_desync_summary.csv:2-4`, `reports/08-open-loop-desync-test_report.md:3-7`; Evidence: 架构把 `gentle_ramp` 定义为正常跟随场景，但脚本要求它 `phase_slip_cycles > 2` 且 `speed_ratio < 0.2` 才 PASS。实际结果为累计滑移 `3.854` 圈、速度比 `0.0885`、负转矩占比 `0.529`；正式图显示相位差持续增长和速度反复换向，符合架构自身的失步定义。 Failure mechanism: 正常、过快和负载场景都处于失步，仅程度不同，证据无法区分“同步跟随”与“失步”，所以 K-DESYNC 和 CAP-OPENLOOP-01 的竞争性解释未成立。 Required correction: 先建立真正锁定的正常基线，再让过快斜坡和锁定后的负载阶跃破坏同步；正常判据应约束尾段滑移率、相位误差和实际/同步速度比，而不是要求已经失步。 Verification: 正常场景尾段未解包相位误差不再单调累积、速度比接近 1；两种边界场景分别触发明确的滑移和失步阈值。

ID: SA-004; Severity: P2; Location: `docs/series-architecture.md:591-613,687`, `scripts/ch12_plecs_hall_speed.py:8-21,34-42`; Evidence: 架构公式为 `omega_m=s*(pi/3)/(pole_pairs*delta_t)`，但 C12 实现硬编码 `direction*(pi/3)/(t-last_edge)`，所有场景固定 `pole_pairs=1`。非相邻合法跳码得到 `direction=0` 后虽然不计算速度，仍更新 `last_edge`、`last_code` 并增加 `edges`，污染下一次周期和边沿计数；测试没有非法码、非相邻跳码或多极对场景。 Failure mechanism: CAP-SPEED-01 中“给定极对数计算机械速度”没有被实现或证明，且测速层自行做不完整的 Hall 合法性判断，越过唯一 Hall 解码职责层。 Required correction: 让测速模块只消费 decoder 产生的合法事件、方向、时间戳和极对数；无合法事件时不得更新测速基准。增加多极对、保持、非法码、非相邻跳码和超时恢复测试。 Verification: `pole_pairs=1/4` 均按公式得到正确机械速度；非法或非相邻输入不改变最后合法时间戳、边沿计数和滤波状态。

ID: SA-005; Severity: P2; Location: `docs/series-architecture.md:268-290`, `reports/series-architecture-evidence-baseline.md:8-23`, `manifest.json`; Evidence: C00 契约引用的 `docs/series-plan.md`、`blog/00-bldc-learning-route.md`、`docs/00-bldc-learning-route-reproduce.md` 均不在冻结清单；证据基线列出的 C01-C14 博客正文也全部缺席。 Failure mechanism: 冻结包可以审查模型、数据和报告，但不能审查 C00 的导航过关标准，也不能验证最终文章是否真正建立了计划中的解释、预测和复现任务。 Required correction: 将这些正文和 C00 复现入口纳入冻结包，或明确把文章内容排除出本轮已证明范围并移除相应完成主张。 Verification: 所有精确源路径均可在 manifest 中解析，且可从 C00 冻结入口到达 C01-C14 的复现材料。

ID: SA-006; Severity: P3; Location: `scripts/check_series_architecture_dag.py:10-50`, `reports/series-architecture-coverage.md:27-35`; Evidence: DAG 脚本只收集 Mermaid 标签并检查前置 ID 是否出现，没有解析边、拓扑排序、环检测或章节 owner/首次使用顺序检查；覆盖报告却把方向和无循环列为 PASS。当前图经独立检查未发现环，但自动门禁不能证明该结论。 Failure mechanism: 后续新增反向边、循环或先用后教时，检查仍可能 PASS。 Required correction: 解析实际边，执行拓扑排序，并按章节序号校验 prerequisite owner 早于首次 consumer。 Verification: 人为加入环、反向依赖或先用后教引用时，检查必须分别 FAIL。

packet_hash_after

`120f74ef0829dddc9506042dcd138f97bcc17caafc45f08bb0b8396ee69f3605`

packet_validation_after: PASS

verdict: REJECT

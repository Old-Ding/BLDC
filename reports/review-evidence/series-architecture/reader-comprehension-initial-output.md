packet_hash_before
35ff270d0a01b915b45a08e535feebd202e78d85eecef8ee9b7c23346982bfe9

packet_validation_before: PASS
command: `test_review_snapshot.ps1 -Manifest ...\series-architecture-v1\manifest.json -ExpectedManifestSha256 35ff270d0a01b915b45a08e535feebd202e78d85eecef8ee9b7c23346982bfe9`
result: `status: SNAPSHOT_VALID`, `packet_type: series_architecture`, `file_count: 24`, `manifest_sha256: 35ff270d0a01b915b45a08e535feebd202e78d85eecef8ee9b7c23346982bfe9`

reviewed_files:
- docs/series-architecture.md
- reports/series-architecture-coverage.md
- reports/series-architecture-evidence-baseline.md
- reports/renders/series-architecture-viewport-matrix.json
- reports/renders/series-architecture-diagram-matrix.json
- reports/renders/series-architecture-contract-matrix.json
- reports/renders/architecture-desktop-top.png
- reports/renders/architecture-desktop-middle.png
- reports/renders/architecture-desktop-bottom.png
- reports/renders/architecture-mobile-top.png
- reports/renders/architecture-mobile-middle.png
- reports/renders/architecture-mobile-bottom.png
- reports/renders/architecture-system-causal-map-desktop.png
- reports/renders/architecture-system-causal-map-mobile.png
- reports/renders/architecture-knowledge-dependency-dag-desktop.png
- reports/renders/architecture-knowledge-dependency-dag-mobile.png
- reports/renders/architecture-contract-chapter-index-desktop.png
- reports/renders/architecture-contract-chapter-index-mobile.png
- reports/renders/architecture-contract-detailed-chapter-contract-desktop.png
- reports/renders/architecture-contract-detailed-chapter-contract-mobile.png
- reports/renders/architecture-contract-evidence-mastery-mapping-desktop.png
- reports/renders/architecture-contract-evidence-mastery-mapping-mobile.png
- reports/renders/architecture-contract-bidirectional-coverage-desktop.png
- reports/renders/architecture-contract-bidirectional-coverage-mobile.png

teach_back:
  target_reader_to_exit_ability: 目标读者已有电机/功率/嵌入式基础，出口能力是把三相桥、电流/反电动势/转矩、六步、Hall、PWM、Hall 测速、PI 和完整闭环串成可复现实验链，并明确第一季只证明 PLECS 仿真闭环。
  system_causal_map: 源文档主链是直流母线 -> 三相桥 -> 相电流 -> 反电动势/转矩 -> 机械速度 -> Hall 边沿 -> 测速/扇区 -> PI/换相/PWM -> 三相桥，另有控制器非法码/全关输出。
  knowledge_prerequisite_dag: ENTRY-PWR/MATH/TOOL 进入净转矩、桥状态、电角度，再到反电动势功率、六步、开环、启动、失步、Hall 扇区、Hall 偏置、PWM、Hall 测速、速度 PI，最终到 C14。
  evidence_mastery_chain: C01-C14 每章都有模型/源码、场景、CSV/summary、图、报告、复现文档、独立判据、掌握级别和 PASS 标准；C14 聚合为第一季闭环能力。
  module_to_one_question_chapter: M00-M04 按路线入口、功率/电机物理、开环同步、Hall/执行器、反馈闭环划分；C00-C14 每章均声明唯一核心问题。
  worked_examples_and_scenarios: 每章有最小示例、正常场景和边界场景，例如 C10 的 offset 扫描、反向表、全关，C14 的启动、目标阶跃、负载阶跃、非法 Hall、过载。
  measurable_closure_and_reused_conclusion: 每章用 PASS 数量、报告、图注契约和“下一章复用结论”闭合；C14 输出作为 C15 主机侧测试参考，但不替代 C 编译证据。
  first_guess_or_backtrack_point: 第一次需要猜测出现在系统图/DAG 渲染材料与源文档 Mermaid 不一致时；读者必须回到源文档判断哪一个是权威架构图。

findings:
  ID: READ-01
  Severity: P2
  Location: `docs/series-architecture.md` lines 120-131 and 168-186; `reports/renders/architecture-system-causal-map-desktop.png`; `reports/renders/architecture-knowledge-dependency-dag-desktop.png`; `reports/renders/series-architecture-diagram-matrix.json`
  Evidence: 源文档系统图的控制节点是 `PI/换相/PWM`，反馈节点是 `测速/扇区`，并有 `CTRL --> INV` 与 `CTRL --> SAFE`；渲染图显示为 `速度/误差`、`PI/限幅/PWM`，并额外显示 `占空比/换相` 分支。源文档 DAG 是带 ENTRY-MATH、K-STARTUP、K-DESYNC 等分支的依赖图；渲染 DAG 变成近似线性链，缺少 `ENTRY-MATH`、`K-STARTUP`、`K-DESYNC` 等源图节点。
  Failure mechanism: 架构包同时提供源文档和渲染图作为审查证据，但二者表达不同因果/依赖结构。目标读者和后续作者无法确定应按哪张图执行章节依赖，容易把“控制器职责”“Hall 测速/扇区”“PI/限幅/换相”的 owner 和前置关系读错。
  Required correction: 选择唯一权威图源；最小改法是按 `docs/series-architecture.md` 的 Mermaid 源重新生成 diagram renders 和 diagram matrix，或反向修改源 Mermaid 与正文职责表，使源图、渲染图、矩阵三者完全一致。
  Verification: 逐项比对源 Mermaid 节点/边与 `architecture-system-causal-map-*.png`、`architecture-knowledge-dependency-dag-*.png` 可见节点/边；`series-architecture-diagram-matrix.json` 的 `reported_visible_labels` 必须来自同一源图；重新运行 snapshot 校验并得到新的 pinned hash。

packet_hash_after
35ff270d0a01b915b45a08e535feebd202e78d85eecef8ee9b7c23346982bfe9

packet_validation_after: PASS
command: `test_review_snapshot.ps1 -Manifest ...\series-architecture-v1\manifest.json -ExpectedManifestSha256 35ff270d0a01b915b45a08e535feebd202e78d85eecef8ee9b7c23346982bfe9`
result: `status: SNAPSHOT_VALID`, `packet_type: series_architecture`, `file_count: 24`, `manifest_sha256: 35ff270d0a01b915b45a08e535feebd202e78d85eecef8ee9b7c23346982bfe9`

verdict: REJECT

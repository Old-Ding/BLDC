packet_hash_before
`86c4e4bf89bd8cd868c45d703903a01e4d5ee7425652dc20d216518ce20e275e`

packet_validation_before: PASS
命令：`test_review_snapshot.ps1 -Manifest ...\manifest.json -ExpectedManifestSha256 86c4...275e`
结果：`SNAPSHOT_VALID`，`file_count=30`，哈希匹配。

reviewed_files:
`docs/series-architecture.md`
`reports/series-architecture-coverage.md`
`reports/series-architecture-evidence-baseline.md`
`reports/renders/series-architecture-viewport-matrix.json`
`reports/renders/series-architecture-diagram-matrix.json`
`reports/renders/series-architecture-contract-matrix.json`
`reports/renders/architecture-desktop-top.png`
`reports/renders/architecture-desktop-middle.png`
`reports/renders/architecture-desktop-bottom.png`
`reports/renders/architecture-mobile-top.png`
`reports/renders/architecture-mobile-middle.png`
`reports/renders/architecture-mobile-bottom.png`
`reports/renders/architecture-system-causal-map-desktop.png`
`reports/renders/architecture-system-causal-map-mobile.png`
`reports/renders/architecture-knowledge-dependency-dag-desktop.png`
`reports/renders/architecture-knowledge-dependency-dag-mobile.png`
`reports/renders/architecture-contract-chapter-index-desktop.png`
`reports/renders/architecture-contract-chapter-index-mobile.png`
`reports/renders/architecture-contract-detailed-chapter-contract-desktop.png`
`reports/renders/architecture-contract-detailed-chapter-contract-mobile.png`
`reports/renders/architecture-contract-evidence-mastery-mapping-desktop.png`
`reports/renders/architecture-contract-evidence-mastery-mapping-mobile.png`
`reports/renders/architecture-contract-bidirectional-coverage-desktop.png`
`reports/renders/architecture-contract-bidirectional-coverage-mobile.png`
`scripts/render_series_architecture_review.js`
`scripts/ch05_six_step_physical_oracle.py`
`waveforms/05-six-step-sequence/six_step_physical_oracle.csv`
`waveforms/05-six-step-sequence/six_step_oracle_mutations.csv`
`reports/05-six-step-physical-oracle.md`
`reports/14-complete-hall-acceptance-contract.md`

pixel_inspection_evidence:
六个视图：`desktop-top` 1365x900，显示“BLDC 技术教程系列架构”、目标读者表和 `CAP-CHAIN-01`；`desktop-middle` 1365x900，显示 C05 契约及 `L3 + L4`、物理 oracle 过关标准；`desktop-bottom` 1365x900，显示“11. 架构门禁自检”和“12. 变更控制”。`mobile-top` 390x844，显示标题及两列表格；`mobile-middle` 390x844，显示 C05 数据/图片/复现表项；`mobile-bottom` 390x844，显示变更控制和 `CAPABILITY_OUTPUT-C14 -> CAP-FW-01`。

四张图示：系统因果图桌面 1365x900，节点“直流母线→三相桥→相电流→反电动势/转矩→机械速度→Hall边沿”及反馈箭头可读；移动端 390x844，主链节点发生横向重叠/裁切。知识依赖 DAG 桌面 1365x900，`ENTRY-PWR→K-NET-TORQUE`、`K-PWM-DUTY→K-SPEED-PI→CAPABILITY_OUTPUT-C14` 可读；移动端 390x844，`ENTRY-PWR`、`CAPABILITY_OUTPUT-C14` 和边列表被左右裁切。

八个契约渲染：章节索引桌面 1365x779、移动端 390x1177，均显示 C00-C14、“唯一核心问题”和“查看”；详细契约桌面 1365x17486、移动端 390x23762，均含 C00-C14 字段表；证据映射桌面 1365x2474、移动端 390x8248，桌面表及移动卡片均显示 E-C05 oracle、E-C14 场景判据；双向覆盖桌面 1365x1441、移动端 390x2528，均显示“能力到章节”和“章节到能力”表。后四类契约没有横向溢出。

findings:
ID: UI-01
Severity: P1
Location: `reports/renders/architecture-system-causal-map-mobile.png`、`reports/renders/architecture-knowledge-dependency-dag-mobile.png`；根因位于 `scripts/render_series_architecture_review.js:107-116,266-299`。
Evidence: 两张 390x844 移动端图分别出现“直流母…”主链节点重叠/裁切，以及 `ENTRY-PWR`、`CAPABILITY_OUTPUT-C14`、边列表被裁切。矩阵虽声明 `page_scroll_width=390`，但像素中无法读完整节点或关系。
Failure mechanism: 目标读者无法在移动端建立“桥-电流-转矩-Hall-PI-PWM”闭环和前置依赖链，图示不能承担渐进披露中的导航职责。
Required correction: 仅在图示渲染器的移动媒体查询中为 system/DAG 使用独立纵向布局，解除固定最小节点宽度造成的碰撞，并让全部边列表可访问；不要改动架构内容或增加重复图。
Verification: 重渲染 390x844 两图；逐像素确认所有节点完整、相邻节点无重叠、所有箭头终点可辨，且所有边列表项可见或可纵向滚动。

packet_hash_after
`86c4e4bf89bd8cd868c45d703903a01e4d5ee7425652dc20d216518ce20e275e`

packet_validation_after: PASS
命令：`test_review_snapshot.ps1 -Manifest ...\manifest.json -ExpectedManifestSha256 86c4...275e`
结果：`SNAPSHOT_VALID`，`file_count=30`，哈希无漂移。

verdict: REJECT

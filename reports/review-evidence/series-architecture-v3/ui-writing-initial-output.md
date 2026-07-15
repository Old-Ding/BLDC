packet_hash_before
`3a187c22cc0ca28f381e24810c4d41b93f3cb4a291af14335da8b31fe5a6ac40`

packet_validation_before: PASS
命令：`test_review_snapshot.ps1 -Manifest ... -ExpectedManifestSha256 ...`
结果：`SNAPSHOT_VALID`，`file_count=31`，清单哈希匹配。

reviewed_files
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
`reports/renders/series-architecture-render-check.json`

findings
- ID: F-UI-01
  Severity: P2
  Location: `scripts/render_series_architecture_review.js:197-202`；`architecture-contract-detailed-chapter-contract-mobile.png`
  Evidence: 全量视图已核验：桌面 top/middle/bottom 均为 `1365x900`，分别可见目标读者表、C05 边界、门禁与变更控制；移动 top/middle/bottom 均为 `390x844`，无横向溢出但中段已显示路径逐字换行。两张系统图为 `1365x900`、`390x844`（17 节点、21 边），两张 DAG 为 `1365x900`、`390x844`（16 节点、23 边）。契约渲染均已检查：索引 `1365x779`、`390x1177`；详细契约 `1365x17748`、`390x23911`；证据映射 `1365x2145`、`390x8325`；双向覆盖 `1365x1440`、`390x2528`。其中详细契约移动图将双列表压入 390 px，字段名、文件路径和 ID 连续逐字换行；渲染器对所有移动表格强制 `table-layout:fixed` 且取消横向容器，只有证据映射被转换为卡片。
  Failure mechanism: 紧凑索引的“查看”会跳转至无法扫描的 C00-C14 契约，读者不能可靠地比对“前置 ID、场景、证据、过关标准、下一章复用结论”，破坏渐进披露和移动端可读性。
  Required correction: 仅在渲染器的“单章详细契约”区段转换为字段名-值的移动卡片布局，保留桌面表格；字段名列保持可读宽度，路径允许整词换行。
  Verification: 重新冻结后，在 `390x844` 下从 C00-C14 每个“查看”进入详细契约；确认字段不再逐字换行、无横向溢出，且全部字段和锚点仍存在。

- ID: F-UI-02
  Severity: P3
  Location: 四张系统因果图与知识依赖图
  Evidence: 四张图的节点为中文或 ID，但标题分别为 `System causal/data-flow map`、`Knowledge dependency DAG`，系统图底部边表使用未展开的 `DC/INV/PH/...` 缩写。
  Failure mechanism: 中文目标读者需要在图外反向推断缩写，图无法独立承担因果链教学职责。
  Required correction: 本地化图标题，并将边表改为中文实体名或提供中英对照图例。
  Verification: 四张图重新渲染后，节点、边表和标题均能脱离正文被中文读者直接解释。

packet_hash_after
`3a187c22cc0ca28f381e24810c4d41b93f3cb4a291af14335da8b31fe5a6ac40`

packet_validation_after: PASS
命令：`test_review_snapshot.ps1 -Manifest ... -ExpectedManifestSha256 ...`
结果：`SNAPSHOT_VALID`，`file_count=31`，清单哈希匹配。

verdict: REJECT

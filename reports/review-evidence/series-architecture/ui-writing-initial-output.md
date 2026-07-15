packet_hash_before
`35ff270d0a01b915b45a08e535feebd202e78d85eecef8ee9b7c23346982bfe9`

packet_validation_before: PASS
命令：`test_review_snapshot.ps1 -Manifest ...series-architecture-v1\manifest.json -ExpectedManifestSha256 35ff...bfe9`
结果：`SNAPSHOT_VALID`，`file_count=24`，哈希匹配。

reviewed_files:
- `docs/series-architecture.md`
- `reports/series-architecture-coverage.md`
- `reports/series-architecture-evidence-baseline.md`
- `reports/renders/series-architecture-viewport-matrix.json`
- `reports/renders/series-architecture-diagram-matrix.json`
- `reports/renders/series-architecture-contract-matrix.json`
- `reports/renders/architecture-desktop-top.png`
- `reports/renders/architecture-desktop-middle.png`
- `reports/renders/architecture-desktop-bottom.png`
- `reports/renders/architecture-mobile-top.png`
- `reports/renders/architecture-mobile-middle.png`
- `reports/renders/architecture-mobile-bottom.png`
- `reports/renders/architecture-system-causal-map-desktop.png`
- `reports/renders/architecture-system-causal-map-mobile.png`
- `reports/renders/architecture-knowledge-dependency-dag-desktop.png`
- `reports/renders/architecture-knowledge-dependency-dag-mobile.png`
- `reports/renders/architecture-contract-chapter-index-desktop.png`
- `reports/renders/architecture-contract-chapter-index-mobile.png`
- `reports/renders/architecture-contract-detailed-chapter-contract-desktop.png`
- `reports/renders/architecture-contract-detailed-chapter-contract-mobile.png`
- `reports/renders/architecture-contract-evidence-mastery-mapping-desktop.png`
- `reports/renders/architecture-contract-evidence-mastery-mapping-mobile.png`
- `reports/renders/architecture-contract-bidirectional-coverage-desktop.png`
- `reports/renders/architecture-contract-bidirectional-coverage-mobile.png`

pixel_inspection_evidence:
- 六视图：桌面 top `1365x900`，可见“目标读者”表和 `CAP-CHAIN-01`；桌面 middle `1365x900`，可见 C03 契约末尾及“C04 反电动势与转矩”；桌面 bottom `1365x900`，可见“11. 架构门禁自检”和“12. 变更控制”。
- 六视图：移动 top `390x844`，可见目标读者双列表；移动 middle `390x844`，可见 C04 的“独立判据、结果数据、正式图片”；移动 bottom `390x844`，可见变更控制五项及 `CAPABILITY_OUTPUT-C14 -> CAP-FW-01`。
- 四图：系统图桌面 `1365x900`，可见“直流母线 -> 三相桥 -> 相电流”和“PI/限幅/PWM”；移动 `390x844`，为纵向节点链。知识 DAG 桌面 `1365x900`，可见 `ENTRY-PWR`、`K-SIXSTEP`、`CAPABILITY_OUTPUT-C14`；移动 `390x844`，同样呈单一纵向链。
- 八契约图：章节索引桌面 `1365x778`、移动 `390x1177`，均可见 C00-C14、“唯一核心问题”和“查看”链接。详细契约桌面 `1365x15172`、移动 `390x22547`，均包含 C00-C14 的字段表。证据映射桌面 `1365x2203` 可读 11 列证据表；移动 `390x5454` 将多数列压为逐字竖排。双向覆盖桌面 `1365x1440`、移动 `390x2528`，均可见“能力到章节”与“章节到能力”。

findings:

ID: UI-01
Severity: P1
Location: `docs/series-architecture.md:120-132`，“3. 系统因果与数据流”；`architecture-system-causal-map-desktop.png`、`architecture-system-causal-map-mobile.png`
Evidence: 源图定义 `CTRL -> INV` 和 `CTRL -> SAFE["非法码/全关"]`。两张渲染图中控制节点均成为链路终点：未见返回“三相桥”的有向边，未见“非法码/全关”分支；反而显示源图不存在的“占空比/换相”。图中也没有速度给定输入。
Failure mechanism: 读者会把 PI/PWM 误解为因果链终点，无法从速度误差追到桥臂执行，再回到 Hall 的闭环；这直接破坏本系列的核心工程链路。
Required correction: 在第 3 节图的唯一职责层修正图定义和渲染：显式绘制“目标速度 -> 控制器”，保留 `控制器 -> 三相桥` 回边及“非法码 -> 全关”分支，并重新生成两张图。
Verification: 两张 PNG 均能目视追踪“目标速度、Hall/测速、PI、PWM/换相、三相桥、电机、Hall”的完整有向闭环，且标签与 Mermaid 源一致。

ID: UI-02
Severity: P1
Location: `docs/series-architecture.md:168-187`，“4. 知识依赖图”；`architecture-knowledge-dependency-dag-desktop.png`、`architecture-knowledge-dependency-dag-mobile.png`
Evidence: 源 DAG 是分支图，例如 `ENTRY-MATH -> K-ELEC-ANGLE`、`K6 -> K7 -> K8`、`K9 -> K10/K12`。两张 PNG 将节点压成线性链：把 `K-NET-TORQUE -> K-BRIDGE-STATE`、`K-OPENLOOP -> K-HALL-SECTOR`、`K-PWM-DUTY -> K-HALL-SPEED` 显示为前置关系，并遗漏 `ENTRY-MATH`、`K-STARTUP`、`K-DESYNC`。
Failure mechanism: 读者将被错误导航到不存在的前置依赖，且看不到启动、失步诊断与 Hall 分支的真实关系，无法据此安排学习或定位能力缺口。
Required correction: 仅在知识 DAG 图层重建布局，完整渲染源定义的所有节点和边，不得将并列分支线性化。
Verification: 对照第 4 节逐边检查，所有 17 条定义边和 `ENTRY-MATH`、`K-STARTUP`、`K-DESYNC` 均在桌面与移动图中可见、可辨且无额外边。

ID: UI-03
Severity: P1
Location: `docs/series-architecture.md:649-666`，“9. 证据与掌握映射”；`architecture-contract-evidence-mastery-mapping-mobile.png`
Evidence: `390x5454` 移动渲染把 11 列表压进 390 px；“主张”、CSV 路径、报告路径和判定责任均逐字断行。页面没有横向溢出，但表格已无法扫描或核对。
Failure mechanism: 目标读者不能在移动端把主张、独立判据、场景、读者任务和过关标准建立对应关系，证据/掌握映射失去可用性。
Required correction: 仅为第 9 节提供响应式展示，在移动端改为每条证据一张纵向字段表或保留主字段并提供同页详情；不得压缩为不可读的多列。
Verification: 在 `390x844` 视口检查 E-C01 至 E-C14，每条的主张、独立判据、场景、读者任务、掌握级别和过关标准均能正常换行阅读。

packet_hash_after
`35ff270d0a01b915b45a08e535feebd202e78d85eecef8ee9b7c23346982bfe9`

packet_validation_after: PASS
命令和结果同审查前：`SNAPSHOT_VALID`，`file_count=24`，哈希匹配。

verdict: REJECT

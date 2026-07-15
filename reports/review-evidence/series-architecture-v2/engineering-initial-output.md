packet_hash_before: 86c4e4bf89bd8cd868c45d703903a01e4d5ee7425652dc20d216518ce20e275e

packet_validation_before: PASS
command/result: `test_review_snapshot.ps1 -Manifest ...\manifest.json -ExpectedManifestSha256 86c4...275e` 返回 `SNAPSHOT_VALID`，`file_count=30`，manifest SHA-256 匹配。

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
- scripts/render_series_architecture_review.js
- scripts/ch05_six_step_physical_oracle.py
- waveforms/05-six-step-sequence/six_step_physical_oracle.csv
- waveforms/05-six-step-sequence/six_step_oracle_mutations.csv
- reports/05-six-step-physical-oracle.md
- reports/14-complete-hall-acceptance-contract.md

findings:

ID: ENG-01
Severity: P1
Location: `docs/series-architecture.md:120-133`，`## 3. 系统因果与数据流`；`architecture-system-causal-map-desktop.png`
Evidence: 图中 `CTRL --> SAFE["非法Hall/全关"]` 把输入故障条件和输出安全动作合为同一节点，并表示为控制器产生“非法 Hall”。但同文件第 159-161 行将非法码状态定义为反馈控制器输入，第 634、644 行又要求换相层判定非法码并输出全关。
Failure mechanism: 读者无法确定非法码由 Hall 解码/换相层检测，还是由速度 PI/PWM 层产生；条件、判定责任和桥级动作混在一起，破坏故障数据流及工程职责边界。
Required correction: 在唯一职责层拆开节点：`Hall 解码 -> 非法码标志 -> 换相安全判定 -> 三相桥全关命令`；PI 只输出 duty，不承担非法 Hall 检测。
Verification: 检查因果图中非法码标志有明确来源和判定 owner，全关命令明确流向三相桥，并与 SYS-FEEDBACK、C14 的输入/输出表逐项一致。

ID: ENG-02
Severity: P1
Location: `docs/series-architecture.md:165-188`，`## 4. 知识依赖图`；对照第 524、632 行章节前置
Evidence: DAG 将 `K-HALL-OFFSET` 仅连接到 `K-HALL-SECTOR`，但 C10 明确还要求 `K-SIXSTEP`、`K-BEMF-POWER`。最终 `CAPABILITY_OUTPUT-C14` 也只有 `K-SPEED-PI` 一条入边，而 C14 明确要求 Hall 偏置、PWM、Hall 测速、PI 和失步诊断。
Failure mechanism: DAG 声称“A -> B 表示没有 A 就无法独立验证 B”，却遗漏实际强制前置，导致读者可能绕过六步物理、功率方向、PWM或诊断知识直接进入集成验收。覆盖报告的“DAG PASS”因此不能证明真实先修闭包。
Required correction: 以章节前置注册表为唯一来源补齐 DAG 边，至少加入 `K-SIXSTEP/K-BEMF-POWER -> K-HALL-OFFSET`，并让 C14 能力出口覆盖其全部直接集成前置；同步重新执行无环和首次使用检查。
Verification: 自动比较每章 `前置 ID` 与 DAG 的祖先闭包，要求所有前置可达、无反向首次使用、无循环，差集为零。

ID: ENG-03
Severity: P1
Location: `scripts/ch05_six_step_physical_oracle.py:40-47,62-83,95-113`；`docs/series-architecture.md:395,404,660`
Evidence: 六个扇区的反电动势相位和期望状态都硬编码在同一 `SECTORS` 表中；mutation 只把该表生成的状态再与同一表的 `expected_state` 比较。脚本既不读取运行时 C 表，也不读取 PLECS 每扇区实际命令，因此只能证明自建表与其变体不一致，不能证明被验六步表符合该物理 oracle。
Failure mechanism: 即使运行时 C 表或 PLECS 换相表整体错误，oracle 仍可 6/6 PASS、mutation 3/3 `FAIL_DETECTED`。因此它不能闭合 CAP-SIXSTEP-01 的“物理来源 -> 实际实现”证据链。
Required correction: 保留独立物理推导，但增加单一比较步骤，将其逐扇区期望 H/L/Z 与实际 C 表或 PLECS 导出的六步命令进行比较；不要在多个层重复判定。
Verification: 正确实现应 6/6 匹配；对实际被验表分别施加扇区偏移、相标签交换和方向反置后，比较必须失败，并报告具体不匹配扇区。

ID: ENG-04
Severity: P2
Location: `architecture-system-causal-map-mobile.png`、`architecture-knowledge-dependency-dag-mobile.png`；生成责任位于 `scripts/render_series_architecture_review.js:107-117,266-299`
Evidence: 390×844 系统图的 `直流母线/三相桥/相电流/反电动势/机械速度/Hall边沿` 节点横向重叠；知识 DAG 左右节点被画布裁切，底部边列表也被截断。矩阵仅记录 `scrollWidth == clientWidth` 和字体尺寸，没有检测节点包围盒重叠或越界。
Failure mechanism: 移动端读者无法可靠辨认节点、边及先修顺序，核心架构图不能承担因果链和知识 DAG 的教学职责；现有自动检查会把不可读渲染误报为通过。
Required correction: 为移动端采用独立纵向布局或允许图内水平滚动，并在渲染检查中加入节点包围盒重叠、画布越界和边列表截断检测。
Verification: 在 390×844 截图中所有节点完整可见、节点包围盒互不相交、标签可辨读、全部边可追踪；自动检查的 overlap、out-of-bounds、clipping 数量均为 0。

packet_hash_after: 86c4e4bf89bd8cd868c45d703903a01e4d5ee7425652dc20d216518ce20e275e

packet_validation_after: PASS
command/result: 再次运行指定 `test_review_snapshot.ps1`，返回 `SNAPSHOT_VALID`，`file_count=30`，manifest SHA-256 仍与外部固定值一致。

verdict: REJECT

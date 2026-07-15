packet_hash_before

`3a187c22cc0ca28f381e24810c4d41b93f3cb4a291af14335da8b31fe5a6ac40`

packet_validation_before: PASS

Command: `& "$env:USERPROFILE\.codex\skills\technical-series-author\scripts\test_review_snapshot.ps1" -Manifest 'D:\1codex\BLDC\reports\review-packets\series-architecture-v3\manifest.json' -ExpectedManifestSha256 '3a187c22cc0ca28f381e24810c4d41b93f3cb4a291af14335da8b31fe5a6ac40'`

Result: exit code `0`; `SNAPSHOT_VALID`; `file_count=31`; manifest SHA-256 matches the externally pinned hash.

reviewed_files

```text
docs/series-architecture.md
reports/series-architecture-coverage.md
reports/series-architecture-evidence-baseline.md
reports/renders/series-architecture-viewport-matrix.json
reports/renders/series-architecture-diagram-matrix.json
reports/renders/series-architecture-contract-matrix.json
reports/renders/architecture-desktop-top.png
reports/renders/architecture-desktop-middle.png
reports/renders/architecture-desktop-bottom.png
reports/renders/architecture-mobile-top.png
reports/renders/architecture-mobile-middle.png
reports/renders/architecture-mobile-bottom.png
reports/renders/architecture-system-causal-map-desktop.png
reports/renders/architecture-system-causal-map-mobile.png
reports/renders/architecture-knowledge-dependency-dag-desktop.png
reports/renders/architecture-knowledge-dependency-dag-mobile.png
reports/renders/architecture-contract-chapter-index-desktop.png
reports/renders/architecture-contract-chapter-index-mobile.png
reports/renders/architecture-contract-detailed-chapter-contract-desktop.png
reports/renders/architecture-contract-detailed-chapter-contract-mobile.png
reports/renders/architecture-contract-evidence-mastery-mapping-desktop.png
reports/renders/architecture-contract-evidence-mastery-mapping-mobile.png
reports/renders/architecture-contract-bidirectional-coverage-desktop.png
reports/renders/architecture-contract-bidirectional-coverage-mobile.png
scripts/render_series_architecture_review.js
scripts/ch05_six_step_physical_oracle.py
waveforms/05-six-step-sequence/six_step_physical_oracle.csv
waveforms/05-six-step-sequence/six_step_oracle_mutations.csv
reports/05-six-step-physical-oracle.md
reports/14-complete-hall-acceptance-contract.md
reports/renders/series-architecture-render-check.json
```

findings

- **ID: ARCH-001; Severity: P1; Location:** `docs/series-architecture.md:118-173`，系统因果图两种渲染。**Evidence:** 图中 `COMM -> PWM duty -> INV`，但三相桥声明还需要三值相命令；没有“扇区→六步表→H/L/Z→门极合成”数据流。`PWM duty` 和 `全关命令` 又作为两条独立路径进入三相桥。**Failure mechanism:** 无法确定相状态、duty、deadtime 和全关覆盖的组合点及优先级，C14 即使闭环曲线通过也不能证明桥命令链职责正确。**Required correction:** 在唯一执行器命令层建立门极合成节点：换相表输出 H/L/Z，PI 输出 duty，安全层输出 enable/all-off，PWM/deadtime 合成六路门极；全关只在该层覆盖一次。**Verification:** 逐信号追踪 Hall 扇区到六路门极，并注入非法 Hall，证明仅该责任层执行全关且不存在第二处防护判断。

- **ID: ARCH-002; Severity: P1; Location:** `scripts/ch05_six_step_physical_oracle.py:28-48,86-113`，`six_step_oracle_mutations.csv:2`，`reports/05-six-step-physical-oracle.md:3-26`。**Evidence:** oracle 先硬编码每扇区正、负反电动势相，再由同一映射直接生成期望 H/L/Z；所谓功率把命令值 `-1/0/1` 直接当作相电流。60° 扇区偏移 mutation 的非正功率扇区数仍为 `0`，仅因不等于硬编码表而失败。**Failure mechanism:** 判据没有独立证明反电动势波形、相位零点、相标签和实际电流路径，不能支撑“六步表具有物理来源”的终局能力。**Required correction:** 从独立解析反电动势方程或独立采样的 Machine 波形建立相位/符号基准，并用桥与绕组模型得到电流后计算 `Σe_i i_i`；期望表不得由待证明的相符号映射直接生成。**Verification:** 在声明的角度零点和接线约定下逐扇区重算功率，并证明相位偏移、相标签交换和方向反置由物理判据而非表相等判据检出。

- **ID: ARCH-003; Severity: P1; Location:** `docs/series-architecture.md:80-88,225,587-610`。**Evidence:** CAP-SPEED 要求读者根据边沿时间和极对数计算速度，但 C12 没有边沿角度、时间单位或速度公式；数据流仅为 `Hall解码/扇区 -> Hall测速`，而解码器接口没有时间戳。**Failure mechanism:** 不同实现可分别按任意 Hall 边沿、单通道边沿或完整电周期计算，仍声称 5/5 PASS；能力与证据不可判定。**Required correction:** 在 Hall 测速唯一责任层定义有效转移事件、时间戳和 `ω_m=s·(π/3)/(p·Δt)`（每个合法 60° 电角转移时），并固定单位、滤波和 timeout 参数。**Verification:** 用已知 `p` 和 `Δt` 手算正转、反转、低速与停止结果，再与独立 Machine 速度对照。

- **ID: ARCH-004; Severity: P1; Location:** `docs/series-architecture.md:651-665`，`reports/14-complete-hall-acceptance-contract.md:5-33`。**Evidence:** 契约未定义目标值、阶跃时刻、负载值、初始电角度、仿真时长、“尾段”窗口、上升时间起点、高限幅阈值及占比的分母窗口；五类失败样本只有名称和预期结论。**Failure mechanism:** 判定脚本可通过选择窗口或场景参数改变 PASS/FAIL，现有数值不能证明完整闭环能力。**Required correction:** 固定每个场景的输入参数和时序，形式化定义每个指标的采样窗口、分母和边界包含关系，并给出五个失败夹具的具体变异。**Verification:** 独立脚本从原始 CSV 重算全部指标；正式场景逐项 PASS，且每个失败夹具只触发其绑定的失败条件。

- **ID: ARCH-005; Severity: P1; Location:** `manifest.json` 文件清单，`reports/series-architecture-evidence-baseline.md:8-33`，`docs/series-architecture.md:668-701`。**Evidence:** 架构和基线声明 C01-C14 仿真证据完整，但冻结包除 C05 oracle 与 C14 阈值表外，没有 C01-C14 模型、原始 CSV、summary、判定脚本、正式测试报告或 C14 失败样本。**Failure mechanism:** 在隔离审查条件下无法沿“源码→数据→报告→能力”复核任何完成声明，计划主张超过冻结包可提供的证据。**Required correction:** 将所声明的不可变主证据及哈希纳入冻结包，或把“证据完整/已通过”降级为待验证计划。**Verification:** 从新冻结包独立运行或重算每条 E-C01 至 E-C14 证据链，且产物哈希可追到 manifest。

- **ID: ARCH-006; Severity: P2; Location:** `docs/series-architecture.md:155-163,290-312,371-393`。**Evidence:** SYS-MOTOR 包含惯量和阻尼，但 C01 将净转矩固定为 `Te-TL`；C04 以 `Σ(ei)=Te·ω` 后直接“除以机械角速度得到转矩”，没有声明 `ω` 必须为 rad/s、符号约定或 `ω≈0` 的不可除边界。**Failure mechanism:** 有阻尼或零速启动时公式不成立或不可计算，读者可能错误解释速度趋势和启动转矩。**Required correction:** 明确 `J·dω/dt=Te-TL-Bω-Tloss`，并声明简化场景中哪些项为零；定义 `Σe_i i_i=Te·ω_m` 的 SI 单位、符号和非零速适用域。**Verification:** 做单位检查，并加入零速、正转驱动和再生三类边界推演。

- **ID: ARCH-007; Severity: P2; Location:** `docs/series-architecture.md:175-227,297,351,432,513,621`。**Evidence:** DAG 未包含 `ENTRY-TOOL` 和 `CAPABILITY_OUTPUT-C05`；同时章节声明的 `K-DESYNC -> C09`、`K-NET-TORQUE -> C13` 等前置关系没有出现在 DAG。**Failure mechanism:** DAG 与前置注册表不是同一依赖模型，无法可靠证明所有前置在首次使用前已建立。**Required correction:** 由注册表和章节前置关系生成或校验 DAG，或者明确区分“教学顺序前置”和“知识依赖”并分别建图。**Verification:** 自动比较章节前置、注册表 owner/首次使用和 DAG 可达关系，未解析及缺失边均为零。

- **ID: ARCH-008; Severity: P2; Location:** `docs/series-architecture.md:165-172,506-528,641-665`。**Evidence:** Hall 故障仅覆盖 `000/111`；六个合法码之间的非相邻跳变仍会被解码成扇区，没有场景验证其方向一致性或故障分类。**Failure mechanism:** 合法但物理不可能的跳码可直接选择错误换相步，而 C14 的非法码全关测试仍全部通过。**Required correction:** Hall 解码层唯一负责合法码和相邻转移检查并输出故障；换相安全层只消费该故障并执行一次全关，不重复检测。**Verification:** 增加正反合法序列和至少一个非相邻合法跳码；前两者正常换相，跳码产生单一故障并由安全层全关。

packet_hash_after

`3a187c22cc0ca28f381e24810c4d41b93f3cb4a291af14335da8b31fe5a6ac40`

packet_validation_after: PASS

Command: `& "$env:USERPROFILE\.codex\skills\technical-series-author\scripts\test_review_snapshot.ps1" -Manifest 'D:\1codex\BLDC\reports\review-packets\series-architecture-v3\manifest.json' -ExpectedManifestSha256 '3a187c22cc0ca28f381e24810c4d41b93f3cb4a291af14335da8b31fe5a6ac40'`

Result: exit code `0`; `SNAPSHOT_VALID`; `file_count=31`; manifest SHA-256 unchanged and matches the externally pinned hash.

verdict: REJECT

packet_hash_before: 789bedb2b53d89045dc4d814f62f30cd2385497cde0e417423ba5bb99e1290c8

packet_validation_before: PASS
command: `& "$env:USERPROFILE\.codex\skills\technical-series-author\scripts\test_review_snapshot.ps1" -Manifest 'D:\1codex\BLDC\reports\review-packets\series-architecture-v5\manifest.json' -ExpectedManifestSha256 '789bedb2b53d89045dc4d814f62f30cd2385497cde0e417423ba5bb99e1290c8'`
result: `Exit code 0; status=SNAPSHOT_VALID; label=series-architecture-v5; packet_type=series_architecture; file_count=286; manifest_sha256=789bedb2b53d89045dc4d814f62f30cd2385497cde0e417423ba5bb99e1290c8`

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
- assets/01-bldc-control-chain/plecs_commutation_zoom.png
- assets/01-bldc-control-chain/plecs_load_comparison.png
- assets/01-bldc-control-chain/plecs_scope_nominal_load.png
- assets/01-bldc-control-chain/plecs_scope_overload.png
- assets/02-three-phase-bridge/gate_truth_table_matrix.png
- assets/02-three-phase-bridge/plecs_bridge_paths.png
- assets/02-three-phase-bridge/plecs_scope_Apos_Bneg.png
- assets/03-electrical-angle/mechanical_vs_electrical_angle.png
- assets/03-electrical-angle/plecs_scope_mechanical_angle.png
- assets/04-torque-power/plecs_ei_to_torque_nominal.png
- assets/04-torque-power/plecs_power_balance_scenarios.png
- assets/04-torque-power/plecs_scope_regenerative_braking.png
- assets/05-six-step-sequence/forward_reverse_sequence.png
- assets/05-six-step-sequence/plecs_forward_six_step.png
- assets/05-six-step-sequence/plecs_scope_forward_sequence.png
- assets/06-open-loop-angle/plecs_scope_slow_field.png
- assets/06-open-loop-angle/slow_vs_fast_open_loop.png
- assets/07-startup-ramp/plecs_scope_ramp_start.png
- assets/07-startup-ramp/ramp_vs_direct_start.png
- assets/08-open-loop-desync/desync_three_scenarios.png
- assets/08-open-loop-desync/plecs_scope_gentle_ramp.png
- assets/09-hall-sequence/hall_sequence_direction_invalid.png
- assets/09-hall-sequence/plecs_scope_hall_forward.png
- assets/10-hall-commutation/hall_offset_sweep.png
- assets/10-hall-commutation/plecs_scope_correct_hall.png
- assets/11-pwm-deadtime/plecs_scope_pwm_50.png
- assets/11-pwm-deadtime/pwm_duty_comparison.png
- assets/12-hall-speed/hall_speed_quantization_timeout.png
- assets/12-hall-speed/plecs_scope_hall_edges_fast.png
- assets/13-speed-pi/plecs_scope_speed_pi.png
- assets/13-speed-pi/speed_pi_antiwindup.png
- assets/14-complete-hall-closed-loop/complete_closed_loop_scenarios.png
- assets/14-complete-hall-closed-loop/plecs_scope_complete_startup.png
- docs/01-bldc-control-chain-reproduce.md
- docs/02-three-phase-bridge-reproduce.md
- docs/03-mechanical-and-electrical-angle-reproduce.md
- docs/04-back-emf-and-torque-reproduce.md
- docs/05-six-step-commutation-reproduce.md
- docs/06-open-loop-electrical-angle-reproduce.md
- docs/07-startup-ramp-reproduce.md
- docs/08-open-loop-desynchronization-reproduce.md
- docs/09-hall-sequence-reproduce.md
- docs/10-hall-commutation-reproduce.md
- docs/11-pwm-deadtime-reproduce.md
- docs/12-hall-speed-reproduce.md
- docs/13-speed-pi-reproduce.md
- docs/14-complete-hall-closed-loop-reproduce.md
- models/plecs/ch01_bldc_baseline/ch01_bldc_baseline.plecs
- models/plecs/ch01_bldc_baseline/README.md
- models/plecs/ch02_three_phase_bridge/ch02_three_phase_bridge.plecs
- models/plecs/ch02_three_phase_bridge/README.md
- models/plecs/ch03_electrical_angle/ch03_electrical_angle.plecs
- models/plecs/ch03_electrical_angle/README.md
- models/plecs/ch05_six_step_sequence/ch05_six_step_sequence.plecs
- models/plecs/ch05_six_step_sequence/README.md
- models/plecs/ch06_open_loop_angle/ch06_open_loop_angle.plecs
- models/plecs/ch06_open_loop_angle/README.md
- models/plecs/ch07_startup_ramp/ch07_startup_ramp.plecs
- models/plecs/ch07_startup_ramp/README.md
- models/plecs/ch08_open_loop_desync/ch08_open_loop_desync.plecs
- models/plecs/ch08_open_loop_desync/README.md
- models/plecs/ch09_hall_sequence/ch09_hall_sequence.plecs
- models/plecs/ch09_hall_sequence/README.md
- models/plecs/ch10_hall_commutation/ch10_hall_commutation.plecs
- models/plecs/ch10_hall_commutation/README.md
- models/plecs/ch11_pwm_deadtime/ch11_pwm_deadtime.plecs
- models/plecs/ch11_pwm_deadtime/README.md
- models/plecs/ch12_hall_speed/ch12_hall_speed.plecs
- models/plecs/ch12_hall_speed/README.md
- models/plecs/ch13_speed_pi/ch13_speed_pi.plecs
- models/plecs/ch13_speed_pi/README.md
- models/plecs/ch14_complete_hall_closed_loop/ch14_complete_hall_closed_loop.plecs
- models/plecs/ch14_complete_hall_closed_loop/README.md
- reports/01-bldc-control-chain-review.md
- reports/01-bldc-control-chain-test_report.md
- reports/02-three-phase-bridge-review.md
- reports/02-three-phase-bridge-test_report.md
- reports/03-electrical-angle-test_report.md
- reports/03-mechanical-and-electrical-angle-review.md
- reports/04-back-emf-and-torque-review.md
- reports/04-torque-power-test_report.md
- reports/05-six-step-commutation-review.md
- reports/05-six-step-physical-oracle.md
- reports/05-six-step-sequence-test_report.md
- reports/06-open-loop-angle-test_report.md
- reports/06-open-loop-electrical-angle-review.md
- reports/07-startup-ramp-review.md
- reports/07-startup-ramp-test_report.md
- reports/08-open-loop-desynchronization-review.md
- reports/08-open-loop-desync-test_report.md
- reports/09-hall-sequence-review.md
- reports/09-hall-sequence-test_report.md
- reports/09-hall-transition-contract.md
- reports/10-hall-commutation-review.md
- reports/10-hall-commutation-test_report.md
- reports/11-pwm-deadtime-review.md
- reports/11-pwm-deadtime-test_report.md
- reports/12-hall-speed-review.md
- reports/12-hall-speed-test_report.md
- reports/13-speed-pi-review.md
- reports/13-speed-pi-test_report.md
- reports/14-complete-hall-acceptance-contract.md
- reports/14-complete-hall-closed-loop-review.md
- reports/14-complete-hall-closed-loop-test_report.md
- reports/renders/series-architecture-render-check.json
- reports/series-architecture-dag-check.json
- scripts/build_ch02_plecs_model.py
- scripts/build_ch03_plecs_model.py
- scripts/build_ch05_plecs_model.py
- scripts/build_ch06_plecs_model.py
- scripts/build_ch07_plecs_model.py
- scripts/build_ch08_plecs_model.py
- scripts/build_ch09_plecs_model.py
- scripts/build_ch10_plecs_model.py
- scripts/build_ch11_plecs_model.py
- scripts/build_ch12_plecs_model.py
- scripts/build_ch13_plecs_model.py
- scripts/build_ch14_plecs_model.py
- scripts/capture_plecs_window.ps1
- scripts/ch01_control_chain_demo.m
- scripts/ch01_plecs_bldc_baseline.py
- scripts/ch02_plecs_three_phase_bridge.py
- scripts/ch02_three_phase_bridge_tests.m
- scripts/ch03_electrical_angle_postprocess.m
- scripts/ch03_plecs_electrical_angle.py
- scripts/ch04_torque_power_check.py
- scripts/ch04_torque_power_postprocess.m
- scripts/ch05_plecs_six_step.py
- scripts/ch05_six_step_physical_oracle.py
- scripts/ch05_six_step_postprocess.m
- scripts/ch06_open_loop_postprocess.m
- scripts/ch06_plecs_open_loop_angle.py
- scripts/ch07_plecs_startup_ramp.py
- scripts/ch07_startup_postprocess.m
- scripts/ch08_desync_postprocess.m
- scripts/ch08_plecs_desync.py
- scripts/ch09_hall_postprocess.m
- scripts/ch09_hall_transition_oracle.py
- scripts/ch09_plecs_hall_sequence.py
- scripts/ch10_hall_commutation_postprocess.m
- scripts/ch10_plecs_hall_commutation.py
- scripts/ch11_plecs_pwm_deadtime.py
- scripts/ch11_pwm_postprocess.m
- scripts/ch12_hall_speed_postprocess.m
- scripts/ch12_plecs_hall_speed.py
- scripts/ch13_plecs_speed_pi.py
- scripts/ch13_speed_pi_postprocess.m
- scripts/ch14_closed_loop_postprocess.m
- scripts/ch14_plecs_complete_closed_loop.py
- scripts/check_series_architecture_dag.py
- scripts/render_series_architecture_review.js
- src/bldc_six_step.c
- src/bldc_six_step.h
- waveforms/01-bldc-control-chain/ch01_bldc_baseline_scope.trace
- waveforms/01-bldc-control-chain/plecs_baseline_summary.csv
- waveforms/01-bldc-control-chain/plecs_nominal_load.csv
- waveforms/01-bldc-control-chain/plecs_overload.csv
- waveforms/02-three-phase-bridge/gate_truth_table.csv
- waveforms/02-three-phase-bridge/plecs_all_off.csv
- waveforms/02-three-phase-bridge/plecs_Apos_Bneg.csv
- waveforms/02-three-phase-bridge/plecs_Apos_Cneg.csv
- waveforms/02-three-phase-bridge/plecs_Bpos_Aneg.csv
- waveforms/02-three-phase-bridge/plecs_Bpos_Cneg.csv
- waveforms/02-three-phase-bridge/plecs_bridge_summary.csv
- waveforms/02-three-phase-bridge/plecs_Cpos_Aneg.csv
- waveforms/02-three-phase-bridge/plecs_Cpos_Bneg.csv
- waveforms/03-electrical-angle/plecs_angle_summary.csv
- waveforms/03-electrical-angle/plecs_four_pole_pairs.csv
- waveforms/03-electrical-angle/plecs_one_pole_pair.csv
- waveforms/04-torque-power/plecs_power_nominal_load.csv
- waveforms/04-torque-power/plecs_power_overload.csv
- waveforms/04-torque-power/plecs_power_regenerative_braking.csv
- waveforms/04-torque-power/plecs_power_summary.csv
- waveforms/04-torque-power/plecs_regenerative_braking_source.csv
- waveforms/05-six-step-sequence/plecs_all_off.csv
- waveforms/05-six-step-sequence/plecs_forward.csv
- waveforms/05-six-step-sequence/plecs_reverse.csv
- waveforms/05-six-step-sequence/plecs_six_step_summary.csv
- waveforms/05-six-step-sequence/six_step_oracle_mutations.csv
- waveforms/05-six-step-sequence/six_step_physical_oracle.csv
- waveforms/06-open-loop-angle/plecs_fast_field.csv
- waveforms/06-open-loop-angle/plecs_open_loop_summary.csv
- waveforms/06-open-loop-angle/plecs_slow_field.csv
- waveforms/07-startup-ramp/plecs_direct_fast.csv
- waveforms/07-startup-ramp/plecs_ramp_start.csv
- waveforms/07-startup-ramp/plecs_startup_summary.csv
- waveforms/08-open-loop-desync/plecs_desync_summary.csv
- waveforms/08-open-loop-desync/plecs_gentle_ramp.csv
- waveforms/08-open-loop-desync/plecs_load_step.csv
- waveforms/08-open-loop-desync/plecs_overfast_ramp.csv
- waveforms/09-hall-sequence/hall_transition_oracle.csv
- waveforms/09-hall-sequence/plecs_forward.csv
- waveforms/09-hall-sequence/plecs_hall_summary.csv
- waveforms/09-hall-sequence/plecs_invalid_000.csv
- waveforms/09-hall-sequence/plecs_invalid_111.csv
- waveforms/09-hall-sequence/plecs_reverse.csv
- waveforms/10-hall-commutation/plecs_all_off.csv
- waveforms/10-hall-commutation/plecs_hall_commutation_summary.csv
- waveforms/10-hall-commutation/plecs_offset_0.csv
- waveforms/10-hall-commutation/plecs_offset_1.csv
- waveforms/10-hall-commutation/plecs_offset_2.csv
- waveforms/10-hall-commutation/plecs_offset_3.csv
- waveforms/10-hall-commutation/plecs_offset_4.csv
- waveforms/10-hall-commutation/plecs_offset_5.csv
- waveforms/10-hall-commutation/plecs_reverse_table.csv
- waveforms/11-pwm-deadtime/plecs_duty_025.csv
- waveforms/11-pwm-deadtime/plecs_duty_050.csv
- waveforms/11-pwm-deadtime/plecs_duty_075.csv
- waveforms/11-pwm-deadtime/plecs_large_deadtime.csv
- waveforms/11-pwm-deadtime/plecs_pwm_summary.csv
- waveforms/11-pwm-deadtime/plecs_zero_deadtime.csv
- waveforms/12-hall-speed/plecs_fast_400.csv
- waveforms/12-hall-speed/plecs_hall_speed_summary.csv
- waveforms/12-hall-speed/plecs_medium_100.csv
- waveforms/12-hall-speed/plecs_reverse_100.csv
- waveforms/12-hall-speed/plecs_slow_25.csv
- waveforms/12-hall-speed/plecs_stopped_timeout.csv
- waveforms/13-speed-pi/plecs_load_step_aw.csv
- waveforms/13-speed-pi/plecs_recovery_aw.csv
- waveforms/13-speed-pi/plecs_recovery_no_aw.csv
- waveforms/13-speed-pi/plecs_speed_pi_summary.csv
- waveforms/13-speed-pi/plecs_speed_step_aw.csv
- waveforms/14-complete-hall-closed-loop/plecs_closed_loop_summary.csv
- waveforms/14-complete-hall-closed-loop/plecs_invalid_hall.csv
- waveforms/14-complete-hall-closed-loop/plecs_load_step.csv
- waveforms/14-complete-hall-closed-loop/plecs_overload.csv
- waveforms/14-complete-hall-closed-loop/plecs_target_step.csv
- waveforms/14-complete-hall-closed-loop/plecs_zero_speed_start.csv
- blog/00-bldc-learning-route.md
- blog/01-bldc-control-chain.md
- blog/02-three-phase-bridge.md
- blog/03-mechanical-and-electrical-angle.md
- blog/04-back-emf-and-torque.md
- blog/05-six-step-commutation-table.md
- blog/06-open-loop-electrical-angle.md
- blog/07-startup-ramp.md
- blog/08-open-loop-desynchronization.md
- blog/09-hall-sequence-and-direction.md
- blog/10-hall-commutation-offset.md
- blog/11-pwm-duty-and-deadtime.md
- blog/12-hall-edge-speed-estimation.md
- blog/13-speed-pi-antiwindup.md
- blog/14-complete-hall-closed-loop.md
- docs/00-bldc-learning-route-reproduce.md
- docs/series-plan.md
- scripts/ch08_desync_classifier_oracle.py
- scripts/ch12_hall_speed_event_oracle.py
- scripts/ch14_acceptance_check.py
- reports/08-open-loop-desync-classifier.md
- reports/12-hall-speed-event-oracle.md
- reports/14-complete-hall-acceptance-check.md
- reports/series-architecture-v5-local-validation.md
- waveforms/08-open-loop-desync/desync_classifier_oracle.csv
- waveforms/12-hall-speed/hall_speed_event_oracle.csv
- waveforms/12-hall-speed/hall_speed_event_oracle_summary.csv
- waveforms/14-complete-hall-closed-loop/plecs_acceptance_summary_v2.csv
- waveforms/14-complete-hall-closed-loop/acceptance_mutations.csv
- waveforms/14-complete-hall-closed-loop/plecs_zero_speed_start_diagnostics.csv
- waveforms/14-complete-hall-closed-loop/plecs_target_step_diagnostics.csv
- waveforms/14-complete-hall-closed-loop/plecs_load_step_diagnostics.csv
- waveforms/14-complete-hall-closed-loop/plecs_invalid_hall_diagnostics.csv
- waveforms/14-complete-hall-closed-loop/plecs_overload_diagnostics.csv

findings:

ID: SA-P1-001
Severity: P1
Location: `docs/series-architecture.md`，真实系统因果/数据流图及对应能力链（约第 118-173、302、383 行）
Evidence: 因果图将“相电流 + 反电动势 → 电磁功率 → 电磁转矩”作为转矩生成主链，同时没有表示反电动势经绕组电压方程影响相电流的反馈。包内第四章材料使用 `sum(e*i)` 与 `Te*omega` 做功率平衡。
Failure mechanism: 永磁电机零速时反电动势和 `e*i` 均为零，但给定合适转子位置与相电流仍能产生启动转矩。因此 `sum(e*i)=Te*omega` 只能作为机电功率一致性关系，不能充当转矩产生的因果模型。该错误会使读者无法正确推导启动、堵转和低速换相行为。
Required correction: 将主链改为“相电压、R/L 和反电动势共同决定相电流；转子电角度/磁链与相电流共同决定电磁转矩；转矩经机械方程决定转速和位置”。把 `sum(e*i)` 与 `Te*omega` 放到独立的功率一致性验证支路。
Verification: 对修订图执行因果路径审查，并用零速有电流启动、稳态电动、再生制动三个反例/正例验证：零速时主链可预测非零转矩，非零速时功率支路满足约定符号下的一致性。

ID: SA-P1-002
Severity: P1
Location: `models/plecs/ch09_hall_sequence/ch09_hall_sequence.plecs`；`models/plecs/ch10_hall_commutation/ch10_hall_commutation.plecs`；`waveforms/10-hall-commutation/*.csv`；`docs/series-architecture.md` 的 `CAP-HALL-01` 证据链
Evidence: C09 的 Hall encoder 输出 A/B/C；C10 的 Hall commutator 没有消费这些输出，而是直接读取 `rotor_angle` 并计算 `sector`。C10 波形字段只有机械角和 `cmd_a/cmd_b/cmd_c`，没有 Hall A/B/C、Hall code、解码扇区或转移合法性。C11、C13、C14 也继续从机械角直接生成扇区。
Failure mechanism: C09 证明 Hall 序列、C10 证明按真实角度索引换相表，两项证据之间不存在实际数据流。Hall 极性、位序、非法码、方向判定或边沿错序即使错误，后续模型仍可能通过，因此现有证据不能证明“Hall 输入 → 解码 → 换相”的端到端能力。
Required correction: 在唯一 Hall 解码职责层输出 `hall_a/b/c`、`hall_code`、合法性、方向和扇区；让 C10 及后续集成模型只消费该接口，不再从机械角旁路计算扇区。重新定义相应 CSV 的原生观测字段和断言。
Verification: 注入正常正反转、Hall 位序交换、非法 000/111、跳码和相位偏置场景；确认错误会沿真实接口改变换相或触发故障，且 `CAP-HALL-01` 的证据可从 Hall 输入连续追踪到桥臂命令。

ID: SA-P1-003
Severity: P1
Location: `models/plecs/ch14_complete_hall_closed_loop/ch14_complete_hall_closed_loop.plecs`；`scripts/ch14_acceptance_check.py`；`waveforms/14-complete-hall-closed-loop/*diagnostics.csv`；`reports/14-complete-hall-acceptance-check.md`
Evidence: C14 模型直接由机械角生成 sector；无效窗口按时间产生并直接清零三值相命令。模型没有原生输出 Hall A/B/C、Hall code、合法转移、fault、enable 或六路门极。`ch14_acceptance_check.py` 再根据机械角离线重建这些诊断；`gate_all_off` 由三值 `cmd_a/b/c` 推断。
Failure mechanism: 验收器验证的是离线重建逻辑，而不是闭环模型实际执行的 Hall 解码、故障锁存、使能切断和门极合成。三值相命令为零也不能证明六路物理门极全部关闭，故 C14 的五场景 PASS 无法证明完整 Hall 六步闭环及故障安全能力。
Required correction: 在 C14 模型内接入真实 Hall 编码/解码、合法转移检查、fault/enable 状态和六路带死区门极合成；验收脚本只能断言 PLECS 原生导出的这些字段，不得由机械角重建被测结果。
Verification: 重新运行零速启动、目标阶跃、负载阶跃、过载、非法 Hall，并增加跳码和单路门极异常场景；CSV 必须原生包含 Hall、decoder、fault、enable 和六路 gate 字段，安全场景逐路证明所有门极关闭。

ID: SA-P1-004
Severity: P1
Location: `docs/series-architecture.md` 的 exit capabilities、章节合同和 evidence/mastery mapping；`reports/series-architecture-evidence-baseline.md`；C01-C14 测试报告
Evidence: CAP 定义要求读者能够解释、预测、复现和诊断；但章节合同及 `E-C01` 至 `E-C14` 的主要过关条件是模型场景或脚本断言 `n/n PASS`。冻结包没有为这些 CAP 提供独立学习者答案、未见样本、诊断提交物或评分 rubric。
Failure mechanism: 系统模型通过只能证明给定实现和验收器对给定样本成立，不能证明读者能在新输入或新故障上完成相应任务。当前 evidence/mastery chain 混淆了“工程系统证据”和“学习者掌握证据”，因此无法证成声明的退出能力。
Required correction: 分离系统验收与学习者验收。为每个 CAP 指定独立任务、未见输入或故障波形、要求提交的推理/计算/修改结果、关键评分点和通过阈值，并明确其前置知识及归属章节。
Verification: 建立 CAP-to-assessment 双向覆盖检查；逐项确认每个 CAP 至少有一个不复用教学答案的独立评测，评分 rubric 可区分仅复现脚本与真正解释、预测或诊断。

ID: SA-P2-005
Severity: P2
Location: `docs/series-architecture.md` 模块入口与 prerequisite registry（约第 233-242 行）；`scripts/check_series_architecture_dag.py`
Evidence: M03 的入口要求包含 `K-HALL-SECTOR`，但该知识项由 M03 首章 C09 首次建立；M04 的入口要求包含 `K-HALL-SPEED`，但该知识项由 M04 首章 C12 首次建立。DAG 检查器只确认 prerequisite ID 出现在 Mermaid 标签中，没有校验 owner 章节顺序、模块入口时序或依赖环。
Failure mechanism: 读者在进入模块前被要求掌握只能在该模块内首次获得的知识，模块合同因自依赖而不可执行。现有自动检查仍会报告通过，无法发现同类“先用后教”问题。
Required correction: 从模块入口移除由模块内部首章建立的知识项，或把对应教学节点提前到前一模块；扩展检查器，基于 chapter/module 顺序验证每个 prerequisite 的首次 owner 严格早于首次 use，并检测环路。
Verification: 对完整 registry 建立拓扑排序；自动报告每个知识项的 owner、first-use 和 module-entry use。要求所有非显式外部基线知识满足 `owner < first-use`，且依赖图无环。

ID: SA-P2-006
Severity: P2
Location: C08、C12 章节合同；`waveforms/08-open-loop-desync/plecs_desync_summary.csv`；`waveforms/12-hall-speed/plecs_hall_speed_summary.csv`；`reports/series-architecture-v5-local-validation.md`；`docs/series-architecture.md` 约第 683、687、700、703、738-739 行
Evidence: C08 的三个 PLECS 场景均为失步，同步正例仅由信号夹具提供。C12 的 PLECS summary 只有五个场景，不含 `medium_100_pp4`；四极对行为仅由事件 oracle 覆盖。架构及本地验证报告也记录了这些缺口。
Failure mechanism: C08 缺少同一物理模型下的同步基准，分类器可能把模型或阈值的系统性偏差误判为失步；C12 缺少带实际 Hall 生成和模型数据流的多极对场景，事件 oracle 只能证明公式自身，不能证明集成实现正确消费极对数。对应 `CAP-OPENLOOP-01` 和 `CAP-SPEED-01` 的物理证据链未闭合。
Required correction: 为 C08 增加同一 PLECS 模型和观测链下稳定同步的正例，并与三类失步共享判据；为 C12 增加至少一个非默认极对数的 PLECS 原生场景，使 Hall 边沿、时间差、方向、极对数和速度估计经过实际链路。
Verification: C08 验收必须同时正确区分同步正例与各失步反例；C12 summary 必须包含 `medium_100_pp4` 等多极对场景，并证明改变极对数会按预期改变机械速度换算，而不是由离线 oracle 代替被测实现。

packet_hash_after: 789bedb2b53d89045dc4d814f62f30cd2385497cde0e417423ba5bb99e1290c8

packet_validation_after: PASS
command: `& "$env:USERPROFILE\.codex\skills\technical-series-author\scripts\test_review_snapshot.ps1" -Manifest 'D:\1codex\BLDC\reports\review-packets\series-architecture-v5\manifest.json' -ExpectedManifestSha256 '789bedb2b53d89045dc4d814f62f30cd2385497cde0e417423ba5bb99e1290c8'`
result: `Exit code 0; status=SNAPSHOT_VALID; label=series-architecture-v5; packet_type=series_architecture; file_count=286; manifest_sha256=789bedb2b53d89045dc4d814f62f30cd2385497cde0e417423ba5bb99e1290c8`

verdict: REJECT

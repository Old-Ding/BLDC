# 系列架构证据基线

记录日期：2026-07-15
用途：列出 `docs/series-architecture.md` 用来声明第一季已完成能力的本地证据。该文件供架构三轨审查使用，不是公开文章正文。

## 1. 第一季证据总览

| 章节 | 文章 | 模型/主来源 | 脚本 | 数据/报告 | 图片 | 复现文档 |
|---|---|---|---|---|---|---|
| C00 | `blog/00-bldc-learning-route.md` | `docs/series-plan.md` | 无 | 无正式场景数据 | 无强制仿真图 | `docs/00-bldc-learning-route-reproduce.md` |
| C01 | `blog/01-bldc-control-chain.md` | `models/plecs/ch01_bldc_baseline/ch01_bldc_baseline.plecs` | `scripts/ch01_plecs_bldc_baseline.py`、`scripts/ch01_control_chain_demo.m` | `waveforms/01-bldc-control-chain/plecs_baseline_summary.csv`、`reports/01-bldc-control-chain-test_report.md` | `assets/01-bldc-control-chain/*.png` | `docs/01-bldc-control-chain-reproduce.md` |
| C02 | `blog/02-three-phase-bridge.md` | `models/plecs/ch02_three_phase_bridge/ch02_three_phase_bridge.plecs` | `scripts/ch02_plecs_three_phase_bridge.py`、`scripts/ch02_three_phase_bridge_tests.m` | `waveforms/02-three-phase-bridge/plecs_bridge_summary.csv`、`reports/02-three-phase-bridge-test_report.md` | `assets/02-three-phase-bridge/*.png` | `docs/02-three-phase-bridge-reproduce.md` |
| C03 | `blog/03-mechanical-and-electrical-angle.md` | `models/plecs/ch03_electrical_angle/ch03_electrical_angle.plecs` | `scripts/ch03_plecs_electrical_angle.py`、`scripts/ch03_electrical_angle_postprocess.m` | `waveforms/03-electrical-angle/plecs_angle_summary.csv`、`reports/03-electrical-angle-test_report.md` | `assets/03-electrical-angle/*.png` | `docs/03-mechanical-and-electrical-angle-reproduce.md` |
| C04 | `blog/04-back-emf-and-torque.md` | `models/plecs/ch01_bldc_baseline/ch01_bldc_baseline.plecs` | `scripts/ch04_torque_power_check.py`、`scripts/ch04_torque_power_postprocess.m` | `waveforms/04-torque-power/plecs_power_summary.csv`、`reports/04-torque-power-test_report.md` | `assets/04-torque-power/*.png` | `docs/04-back-emf-and-torque-reproduce.md` |
| C05 | `blog/05-six-step-commutation-table.md` | `models/plecs/ch05_six_step_sequence/ch05_six_step_sequence.plecs`、`src/bldc_six_step.c`、测试侧物理 oracle | `scripts/ch05_plecs_six_step.py`、`scripts/ch05_six_step_postprocess.m`、`scripts/ch05_six_step_physical_oracle.py` | `waveforms/05-six-step-sequence/plecs_six_step_summary.csv`、`waveforms/05-six-step-sequence/six_step_physical_oracle.csv`、`waveforms/05-six-step-sequence/six_step_oracle_mutations.csv`、`reports/05-six-step-sequence-test_report.md`、`reports/05-six-step-physical-oracle.md` | `assets/05-six-step-sequence/*.png` | `docs/05-six-step-commutation-reproduce.md` |
| C06 | `blog/06-open-loop-electrical-angle.md` | `models/plecs/ch06_open_loop_angle/ch06_open_loop_angle.plecs` | `scripts/ch06_plecs_open_loop_angle.py`、`scripts/ch06_open_loop_postprocess.m` | `waveforms/06-open-loop-angle/plecs_open_loop_summary.csv`、`reports/06-open-loop-angle-test_report.md` | `assets/06-open-loop-angle/*.png` | `docs/06-open-loop-electrical-angle-reproduce.md` |
| C07 | `blog/07-startup-ramp.md` | `models/plecs/ch07_startup_ramp/ch07_startup_ramp.plecs` | `scripts/ch07_plecs_startup_ramp.py`、`scripts/ch07_startup_postprocess.m` | `waveforms/07-startup-ramp/plecs_startup_summary.csv`、`reports/07-startup-ramp-test_report.md` | `assets/07-startup-ramp/*.png` | `docs/07-startup-ramp-reproduce.md` |
| C08 | `blog/08-open-loop-desynchronization.md` | `models/plecs/ch08_open_loop_desync/ch08_open_loop_desync.plecs`、信号级分类 oracle | `scripts/ch08_plecs_desync.py`、`scripts/ch08_desync_postprocess.m`、`scripts/ch08_desync_classifier_oracle.py` | `waveforms/08-open-loop-desync/plecs_desync_summary.csv`、`waveforms/08-open-loop-desync/desync_classifier_oracle.csv`、`reports/08-open-loop-desync-test_report.md`、`reports/08-open-loop-desync-classifier.md` | `assets/08-open-loop-desync/*.png` | `docs/08-open-loop-desynchronization-reproduce.md` |
| C09 | `blog/09-hall-sequence-and-direction.md` | `models/plecs/ch09_hall_sequence/ch09_hall_sequence.plecs`、Hall 转移 oracle | `scripts/ch09_plecs_hall_sequence.py`、`scripts/ch09_hall_transition_oracle.py`、`scripts/ch09_hall_postprocess.m` | `waveforms/09-hall-sequence/plecs_hall_summary.csv`、`waveforms/09-hall-sequence/hall_transition_oracle.csv`、`reports/09-hall-sequence-test_report.md`、`reports/09-hall-transition-contract.md` | `assets/09-hall-sequence/*.png` | `docs/09-hall-sequence-reproduce.md` |
| C10 | `blog/10-hall-commutation-offset.md` | `models/plecs/ch10_hall_commutation/ch10_hall_commutation.plecs` | `scripts/ch10_plecs_hall_commutation.py`、`scripts/ch10_hall_commutation_postprocess.m` | `waveforms/10-hall-commutation/plecs_hall_commutation_summary.csv`、`reports/10-hall-commutation-test_report.md`、`waveforms/10-hall-commutation/plecs_offset_0.csv` | `assets/10-hall-commutation/*.png` | `docs/10-hall-commutation-reproduce.md` |
| C11 | `blog/11-pwm-duty-and-deadtime.md` | `models/plecs/ch11_pwm_deadtime/ch11_pwm_deadtime.plecs` | `scripts/ch11_plecs_pwm_deadtime.py`、`scripts/ch11_pwm_postprocess.m` | `waveforms/11-pwm-deadtime/plecs_pwm_summary.csv`、`reports/11-pwm-deadtime-test_report.md` | `assets/11-pwm-deadtime/*.png` | `docs/11-pwm-deadtime-reproduce.md` |
| C12 | `blog/12-hall-edge-speed-estimation.md` | `models/plecs/ch12_hall_speed/ch12_hall_speed.plecs`、Hall 事件 oracle | `scripts/ch12_plecs_hall_speed.py`、`scripts/ch12_hall_speed_postprocess.m`、`scripts/ch12_hall_speed_event_oracle.py` | `waveforms/12-hall-speed/plecs_hall_speed_summary.csv`、`waveforms/12-hall-speed/plecs_medium_100_pp4.csv`、`waveforms/12-hall-speed/hall_speed_event_oracle.csv`、`waveforms/12-hall-speed/hall_speed_event_oracle_summary.csv`、`reports/12-hall-speed-test_report.md`、`reports/12-hall-speed-event-oracle.md` | `assets/12-hall-speed/*.png` | `docs/12-hall-speed-reproduce.md` |
| C13 | `blog/13-speed-pi-antiwindup.md` | `models/plecs/ch13_speed_pi/ch13_speed_pi.plecs` | `scripts/ch13_plecs_speed_pi.py`、`scripts/ch13_speed_pi_postprocess.m` | `waveforms/13-speed-pi/plecs_speed_pi_summary.csv`、`reports/13-speed-pi-test_report.md` | `assets/13-speed-pi/*.png` | `docs/13-speed-pi-reproduce.md` |
| C14 | `blog/14-complete-hall-closed-loop.md` | `models/plecs/ch14_complete_hall_closed_loop/ch14_complete_hall_closed_loop.plecs`、原生验收检查 | `scripts/ch14_plecs_complete_closed_loop.py`、`scripts/ch14_closed_loop_postprocess.m`、`scripts/ch14_acceptance_check.py` | `waveforms/14-complete-hall-closed-loop/plecs_closed_loop_summary.csv`、`waveforms/14-complete-hall-closed-loop/plecs_acceptance_summary_v2.csv`、`waveforms/14-complete-hall-closed-loop/acceptance_mutations.csv`、`reports/14-complete-hall-closed-loop-test_report.md`、`reports/14-complete-hall-acceptance-contract.md`、`reports/14-complete-hall-acceptance-check.md` | `assets/14-complete-hall-closed-loop/*.png` | `docs/14-complete-hall-closed-loop-reproduce.md` |

## 2. 完成边界

第一季证据支持以下结论：

- PLECS 开关功率级和 BLDC Machine 中，C01-C07、C09-C13 的章节证据可复现。
- C00-C14 均有文章或内部入口记录；C01-C14 均有命名场景、CSV 或 summary CSV、图片、报告和复现说明。
- C08 的 PLECS 数据包含 `sync_follow` 同步正例以及 `gentle_ramp`、`overfast_ramp`、`load_step` 三类失步场景。
- C10-C14 的 PLECS 模型已经形成 `Hall interface -> decoded sector / legal transition -> commutator / PI / gate` 数据流。
- C12 的 4 极对测速已经由 PLECS 原生输出重跑证明。
- C14 的五个 CSV 场景覆盖零速启动、目标阶跃、负载阶跃、非法 Hall 和过载，并通过只读取原生 Hall/control/gate 字段的验收谓词。
- C05 物理 oracle 的期望来自解析梯形反电动势和桥臂/绕组电流路径，并逐扇区对照 `src/bldc_six_step.c` 的 `forward[6]` 被测表；覆盖 6 个电角扇区和 3 类同源一致性 mutation。
- C09 Hall 转移 oracle 覆盖正向相邻、反向相邻、保持、`000/111` 非法码和非相邻合法跳码。
- C08 离线分类检查证明现有三个 PLECS 场景均为失步，且信号级同步夹具可被阈值识别。
- C12 事件 oracle 覆盖 1/4 极对、正反向、非法码、非相邻跳码、保持和超时恢复。
- C14 验收绑定速度误差、Hall 偏差、启动/阶跃时间、全关占比、高限幅占比、峰值电流、Hall fault/enable、Hall 边沿计数和五类失败样本谓词。
- 学习者独立验收任务已经从系统验收中分离出来，覆盖 CAP-CHAIN-01 到 CAP-INTEGRATION-01 的未见输入、提交物、评分关键点和通过阈值。

第一季证据不支持以下结论：

- C 控制核心已经可编译。
- MCU 定时器、ADC、PWM、ISR 或 HAL 已经验证。
- 真实硬件、HIL、温升、过流保护或量产安全裕量已经验证。
- 无感六步或 FOC 已经完成。

## 3. 当前工作区变更

本次架构审查候选包含未提交工作区变更，`git_commit_or_diff_base` 采用 `working-tree:<base-sha>` 形式记录。正式提交、推送或 CSDN 处理前，必须重新验证最终审批包与工作区文件字节一致。

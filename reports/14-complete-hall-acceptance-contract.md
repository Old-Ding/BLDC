# 第 14 章完整 Hall 六步闭环验收契约

本文件固定 C14 的输入、窗口和判据。`PASS` 只能来自本文件定义的字段，不允许通过改变场景参数、采样窗口或分母来改变结论。

## 1. 全局参数

| 参数 | 值 | 单位 | 用途 |
|---|---:|---|---|
| `Udc_V` | 48.0 | V | 直流母线。 |
| `pole_pairs` | 1 | - | Hall 速度换算。 |
| `alignment_s` | 0.02 | s | 启动定位时间。 |
| `start_frequency_Hz` | 5.0 | Hz | 开环启动初始频率。 |
| `end_frequency_Hz` | 25.0 | Hz | 开环启动末端频率。 |
| `ramp_duration_s` | 0.2 | s | 启动斜坡时间。 |
| `hall_offset_rad` | 0.0 | rad | Hall 安装偏置。 |
| `commutation_offset_steps` | 0 | step | 已验证换相偏置。 |
| `table_direction` | 1 | - | 正向六步表。 |
| `pwm_frequency_Hz` | 10000.0 | Hz | PWM 载波。 |
| `deadtime_s` | 2e-6 | s | 门极合成死区。 |
| `speed_kp` | 0.008 | - | 速度 PI 比例增益。 |
| `speed_ki` | 0.8 | 1/s | 速度 PI 积分增益。 |
| `duty_min` | 0.1 | - | duty 下限。 |
| `duty_max` | 0.9 | - | duty 上限。 |
| `antiwindup_enable` | 1 | - | 条件积分开启。 |
| `hall_speed_alpha` | 0.25 | - | Hall 速度一阶滤波系数。 |
| `hall_speed_timeout_s` | 0.05 | s | Hall 速度超时清零。 |
| `simulation_stop_s` | 0.5 | s | 仿真结束。 |
| `sample_period_s` | 1e-5 | s | 输出采样间隔。 |

## 2. 正式场景输入

| 场景 | 初始速度/rad/s | 目标前/rad/s | 目标后/rad/s | 目标阶跃/s | 负载前/Nm | 负载后/Nm | 负载阶跃/s | Hall 故障开始/s | Hall 故障结束/s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `zero_speed_start` | 0.0 | 60.0 | 60.0 | 1.0 | 0.0 | 0.0 | 1.0 | 1.0 | 1.0 |
| `target_step` | 30.0 | 45.0 | 60.0 | 0.12 | 0.0 | 0.0 | 1.0 | 1.0 | 1.0 |
| `load_step` | 30.0 | 60.0 | 60.0 | 1.0 | 0.0 | 3.0 | 0.15 | 1.0 | 1.0 |
| `invalid_hall` | 30.0 | 60.0 | 60.0 | 1.0 | 0.0 | 0.0 | 1.0 | 0.12 | 0.14 |
| `overload` | 30.0 | 60.0 | 60.0 | 1.0 | 0.0 | 12.0 | 0.15 | 1.0 | 1.0 |

## 3. 指标定义

| 指标 | 定义 | 窗口 / 分母 |
|---|---|---|
| 尾段速度误差 | `mean(abs(speed_target_rad_s - speed_rad_s))`。 | 最后 5000 个样本，即 `[0.45001, 0.50000] s`。 |
| Hall 尾段均值偏差 | `abs(mean(speed_rad_s[valid]) - mean(hall_speed_feedback_rad_s[valid]))`，`valid` 为 Hall 反馈非零样本。 | 最后 5000 个样本中的 `abs(hall_speed_feedback_rad_s) > 1e-9` 样本。 |
| 启动到 50 rad/s 时间 | 第一个 `speed_rad_s >= 50` 的采样时间；若不存在则为 `-1`。 | 仅用于 `zero_speed_start`，窗口为全仿真 `[0, 0.5] s`。 |
| 目标阶跃后到 55 rad/s 时间 | `speed_target_step_s` 之后第一个 `speed_rad_s >= 55` 的相对时间；若不存在则为 `-1`。 | 仅用于 `target_step`，时间零点为目标阶跃采样时刻。 |
| 负载后高限幅占比 | `effective_duty > 0.85` 的样本数除以负载阶跃后样本数。 | 仅 `load_step_time_s < 1.0` 的场景；分母为 `[load_step_time_s, 0.5] s` 的样本数。 |
| 故障全关占比 | Hall 故障注入窗口内 `abs(cmd_a)<0.5 && abs(cmd_b)<0.5 && abs(cmd_c)<0.5` 的样本数除以故障窗口样本数。 | `[hall_invalid_start_s, hall_invalid_end_s)`；无故障窗口时为 0。 |
| 峰值相电流 | `max(abs(ia_A), abs(ib_A), abs(ic_A))`。 | 全仿真 `[0, 0.5] s`。 |

## 4. 正式场景阈值

| 场景 | 速度误差 | Hall 偏差 | 上升时间 | 全关占比 | 高限幅占比 | 峰值电流 | PASS 含义 |
|---|---|---|---|---|---|---|---|
| `zero_speed_start` | 尾段 <= 5 rad/s | 尾段 <= 2 rad/s | 50 rad/s <= 0.03 s | = 0 | 不作为主判据 | <= 35 A | 零速启动后进入目标附近。 |
| `target_step` | 尾段 <= 5 rad/s | 尾段 <= 2 rad/s | 阶跃后到 55 rad/s <= 0.12 s | = 0 | <= 0.05 | 不作为主判据 | 目标阶跃后闭环能收敛。 |
| `load_step` | 尾段 <= 8 rad/s | 尾段 <= 2 rad/s | 不作为主判据 | = 0 | >= 0.5 | 不作为主判据 | 负载扰动后仍能维持闭环并进入限幅恢复。 |
| `invalid_hall` | 正常段尾段 <= 5 rad/s | 尾段 <= 2 rad/s | 不作为主判据 | >= 0.99 | = 0 | 不作为主判据 | 非法 Hall 被换相层判定并全关。 |
| `overload` | 尾段 >= 15 rad/s | 尾段 <= 2 rad/s | 不作为主判据 | = 0 | >= 0.8 | <= 35 A | 正确识别过载饱和；不要求达到目标速度。 |

## 5. 当前 summary 对照

| 场景 | 尾段速度误差/rad/s | Hall 偏差/rad/s | 50 rad/s 上升时间/s | 高限幅占比 | 全关占比 | 峰值电流/A | 当前结果 |
|---|---:|---:|---:|---:|---:|---:|---|
| `zero_speed_start` | 2.166 | 0.488 | 0.01211 | 0.000 | 0.000 | 27.886 | PASS |
| `target_step` | 1.958 | 0.243 | 0.09527 | 0.000 | 0.000 | 12.035 | PASS |
| `load_step` | 6.516 | 0.840 | 0.00940 | 0.888 | 0.000 | 14.443 | PASS |
| `invalid_hall` | 1.988 | 0.842 | 0.00940 | 0.000 | 1.000 | 12.650 | PASS |
| `overload` | 20.718 | 0.057 | 0.00940 | 0.904 | 0.000 | 27.800 | PASS |

## 6. 失败样本夹具

| 失败样本 | 变异方式 | 必须触发的 FAIL |
|---|---|---|
| `startup_failure` | 离线谓词把 `zero_speed_start` 的上升时间改为未达到并把尾段误差改为 18 rad/s。 | 速度达不到 50 rad/s 或尾段误差超限。 |
| `steady_error_over_limit` | 离线谓词把 `target_step` 的尾段误差改为 8 rad/s。 | 尾段速度误差超限。 |
| `load_recovery_timeout` | 离线谓词把 `load_step` 的尾段误差改为 12 rad/s、负载后高限幅占比改为 0.30。 | 尾段误差超限或负载后高限幅占比未达到恢复判据。 |
| `invalid_hall_not_all_off` | 离线谓词把 `invalid_hall` 的故障全关占比改为 0。 | 故障全关占比低于 0.99。 |
| `overload_misclassified` | 离线谓词把 `load_step` 指标按 `overload` 判据分类。 | 速度误差未达到过载阈值或高限幅占比不足。 |

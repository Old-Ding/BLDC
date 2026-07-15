# 第 08 篇复现说明：开环失步诊断

## 运行命令

启动 PLECS 5.0，并启用 XML-RPC `localhost:1080`：

```powershell
Set-Location .\BLDC
python .\scripts\build_ch08_plecs_model.py
python .\scripts\ch08_plecs_desync.py
python .\scripts\ch08_desync_classifier_oracle.py
matlab -batch "run('scripts/ch08_desync_postprocess.m')"
```

期望 `scenarios=4 pass=4 time_points=701 signals=15`；离线分类检查输出 `rows=4 pass=True`；MATLAB 生成 1 张三场景诊断图。

## 数据来源

| 数据 | 来源 |
|---|---|
| 相电流、反电动势、速度、转矩、机械角 | PLECS IGBT bridge 与 BLDC Machine |
| 负载阶跃 | PLECS 原生 `Step` 组件连接机械 Torque 端口 |
| 连续命令电角 | Python 对场景频率积分，用于核对模型 C-Script |
| 解包转子角、累计滑移、速度比 | Python 对 PLECS 返回值后处理 |
| 同步/失步分类阈值 | PLECS `sync_follow` 正例和三类失步场景使用同一组速度比/相位滑移观测链；`scripts/ch08_desync_classifier_oracle.py` 只固定分类器边界 |
| 对比图 | MATLAB 读取逐点 CSV |

## 最新结果

| 场景 | 角色 | 尾段速度/rad/s | 速度比 | 滑移/圈 | 分类 | 结果 |
|---|---|---:|---:|---:|---|---|
| `sync_follow` | 同步跟随正例 | 60.045 | 0.9557 | 0.096 | SYNC_FOLLOW_CONFIRMED | PASS |
| `gentle_ramp` | 缓斜坡失步基线 | 13.900 | 0.0885 | 3.854 | DESYNC_CONFIRMED | PASS |
| `overfast_ramp` | 过快失步 | 0.077 | 0.0002 | 22.921 | DESYNC_CONFIRMED | PASS |
| `load_step` | 负载失步 | 13.930 | 0.0887 | 4.140 | DESYNC_CONFIRMED | PASS |

四个 PLECS 场景共用同一套观测列和分类器；`sync_follow` 是同步跟随正例，其余三项是失步对照。

## 生成物

| 类型 | 路径 |
|---|---|
| 模型 | `models/plecs/ch08_open_loop_desync/ch08_open_loop_desync.plecs` |
| 原始 CSV | `waveforms/08-open-loop-desync/plecs_*.csv` |
| 汇总 | `waveforms/08-open-loop-desync/plecs_desync_summary.csv` |
| 分类 oracle | `waveforms/08-open-loop-desync/desync_classifier_oracle.csv` |
| PLECS 截图 | `assets/08-open-loop-desync/plecs_scope_gentle_ramp.png` |
| MATLAB 图 | `assets/08-open-loop-desync/desync_three_scenarios.png` |
| 报告 | `reports/08-open-loop-desync-test_report.md`、`reports/08-open-loop-desync-classifier.md` |

## 失败解释

| 现象 | 检查项 |
|---|---|
| `load_step` 与 `gentle_ramp` 逐点完全相同 | 负载源是否直接接到 Torque 端口；不要只在 CSV 中生成一列假负载 |
| 滑移曲线在 ±0.5 圈反复跳 | 使用了折回相位差，应改用解包角度差 |
| 过快场景的滑移没有明显增加 | 频率是否先积分成命令角，场景变量是否传入模型 |
| PLECS 信号不是 15 路 | 第 07 篇母模型顶层输出接口被修改 |

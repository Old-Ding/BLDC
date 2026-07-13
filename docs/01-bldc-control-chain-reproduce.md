# 第 01 章复现：PLECS BLDC 基准实验

## 实验目标

在同一个 PLECS BLDC 模型中运行额定负载和过载场景，复查“电流仍然存在时，电机为什么仍会减速”。最短判断路径是：

```text
三相电流仍受限
  -> 计算尾段平均电磁转矩
  -> 与负载转矩比较
  -> 平均净转矩为负
  -> 转速持续下降
```

模型同时导出换相命令和反电动势，便于后续章节继续使用；复查第 01 章核心结论时，先看转速、电磁转矩和负载转矩，不需要先分析换相细节。

## 环境

| 工具 | 要求 | 用途 |
|---|---|---|
| PLECS Standalone | 已验证 5.0.2 | 运行逆变器和 BLDC 电机模型、导出 Scope 主图 |
| Python | 3.10 或更新版本 | 通过标准库 XML-RPC 运行场景、导出 CSV 和报告 |
| MATLAB | 已验证 R2024b | 读取 PLECS CSV，生成对比图和换相局部图 |

模型来源和改动说明见 `models/plecs/ch01_bldc_baseline/README.md`。

## 第一步：启用 PLECS RPC

在 PLECS 中打开：

```text
File -> PLECS Preferences... -> General -> XML-RPC
```

启用服务并使用端口 `1080`。PowerShell 检查命令：

```powershell
Get-NetTCPConnection -LocalPort 1080 -State Listen
```

## 第二步：运行 PLECS 场景

```powershell
git clone https://github.com/Old-Ding/BLDC.git
Set-Location .\BLDC
python .\scripts\ch01_plecs_bldc_baseline.py
```

期望输出：

```text
PLECS_SCENARIO_START scenario=nominal_load
PLECS_SCENARIO_DONE scenario=nominal_load result=PASS elapsed_s=<实际耗时>
PLECS_SCENARIO_START scenario=overload
PLECS_SCENARIO_DONE scenario=overload result=PASS elapsed_s=<实际耗时>
Generated chapter 01 PLECS baseline. scenarios=2 pass=2 time_points=601 signals=11 elapsed_s=<总耗时>
```

最后一行出现后，Python 场景脚本已经结束。PLECS 是由用户启动的 XML-RPC 服务，脚本只关闭本章模型，不关闭 PLECS 应用；因此 PLECS 窗口继续存在不表示仿真仍在运行。单次 RPC 调用超过 120 秒时，脚本会以 `PLECS_RPC_TIMEOUT` 退出，不会无限等待。

脚本运行两个场景：

| 场景 | 直流母线 | 电流参考 | 负载转矩 | 预期现象 |
|---|---:|---:|---:|---|
| `nominal_load` | 300 V | 5 A | 3 N m | 电磁转矩跟随负载，转速保持并略有上升 |
| `overload` | 300 V | 5 A | 6 N m | 电流保持受限，可用转矩不足，转速持续下降 |

最近一次运行的关键指标：

| 场景 | 相电流峰值 | 尾段转速 | 尾段电磁转矩 | 结果 |
|---|---:|---:|---:|---|
| `nominal_load` | 5.9941 A | 3490.23 rpm | 2.9936 N m | PASS |
| `overload` | 5.9982 A | 271.99 rpm | 4.0098 N m | PASS |

这里的过载 PASS 表示模型正确复现“电流受限而失速”，不是表示过载时仍满足速度要求。

## 第三步：导出 PLECS Scope 主图

打开：

```text
models/plecs/ch01_bldc_baseline/ch01_bldc_baseline.plecs
```

选择：

```text
Simulation -> Simulation scripts...
-> Export Chapter 01 Scope Evidence
-> Run
```

模型内脚本会用 1800 x 1350 像素导出额定负载和过载 Scope 图。

## 第四步：生成 MATLAB 辅助图

```powershell
matlab -batch "run('scripts/ch01_control_chain_demo.m')"
```

期望输出：

```text
Generated chapter 01 MATLAB post-processing. scenarios=2 pass=2 figures=2
```

MATLAB 不重新模拟电机，只读取 PLECS CSV 做场景比较和局部放大。

`plecs_load_comparison.png` 的上半部分对比两种负载下的转速，下面的柱状图直接比较尾段平均电磁转矩和负载转矩。按“先看柱状图，再看转速”的顺序核对：

| 场景 | 尾段平均电磁转矩 | 负载转矩 | 应观察到的转速趋势 |
|---|---:|---:|---|
| `nominal_load` | 2.9936 N m | 3 N m | 平均净转矩接近 0，转速不再持续变化 |
| `overload` | 4.0098 N m | 6 N m | 平均净转矩约为 -1.99 N m，转速持续下降 |

过载场景的 `271.99 rpm` 是最后 20% 时间窗口内的平均值；最终机械角速度为 `-1.26 rad/s`，表示已经到达零速附近。

## 生成物

| 类型 | 文件 |
|---|---|
| PLECS 模型 | `models/plecs/ch01_bldc_baseline/ch01_bldc_baseline.plecs` |
| PLECS 运行器 | `scripts/ch01_plecs_bldc_baseline.py` |
| MATLAB 后处理 | `scripts/ch01_control_chain_demo.m` |
| 逐点数据 | `waveforms/01-bldc-control-chain/plecs_nominal_load.csv`、`plecs_overload.csv` |
| 汇总数据 | `waveforms/01-bldc-control-chain/plecs_baseline_summary.csv` |
| PLECS trace | `waveforms/01-bldc-control-chain/ch01_bldc_baseline_scope.trace` |
| PLECS 主图 | `assets/01-bldc-control-chain/plecs_scope_nominal_load.png`、`plecs_scope_overload.png` |
| MATLAB 辅助图 | `assets/01-bldc-control-chain/plecs_load_comparison.png`、`plecs_commutation_zoom.png` |
| 测试报告 | `reports/01-bldc-control-chain-test_report.md` |

## 常见失败

| 输出或现象 | 原因 | 处理 |
|---|---|---|
| `PLECS_RPC_NOT_READY` | PLECS 未启动或 XML-RPC 未启用 | 启动 PLECS，检查 Preferences 和 1080 端口 |
| `PLECS_RPC_TIMEOUT` | PLECS 停在对话框、求解器未收敛或 RPC 服务失去响应 | 切回 PLECS 检查前台提示和模型求解状态 |
| `MODEL_MISSING` | 模型路径被移动或文件未拉取 | 检查 `models/plecs/ch01_bldc_baseline` |
| `signal_rows` 不是 11 | 模型顶层 Outport 接口被改动 | 对照模型 README 恢复 5 个 Outport |
| MATLAB 提示缺少输出列 | PLECS CSV 版本与脚本不一致 | 先重新运行 Python 场景脚本，再运行 MATLAB |
| 过载场景速度下降 | 这是预期边界现象 | 对照负载转矩与尾段电磁转矩，不要按速度维持场景解读 |

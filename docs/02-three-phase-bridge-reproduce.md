# 第 02 篇复现说明：真实三相桥电流路径

## 复现目标

验证六个 120 度导通状态和全关状态经过 PLECS 两电平 IGBT 三相桥后，能够产生预期线电压和 BLDC 绕组电流；同时审计六路门极的全部 64 组组合。

## 环境

| 工具 | 要求 | 用途 |
|---|---|---|
| Windows PowerShell | Windows 11 自带 | 执行命令和捕获 PLECS Scope 窗口 |
| Python | 3.10 或更高 | PLECS XML-RPC、CSV 和报告生成 |
| PLECS Standalone | 已验证版本 5.0 | 两电平 IGBT 桥和 BLDC Machine 主仿真 |
| MATLAB | 已验证 R2025b | 读取 PLECS CSV 并生成后处理图 |

PLECS 需要在 Preferences 中启用 XML-RPC，监听 `localhost:1080`。

## 运行命令

```powershell
Set-Location .\BLDC
python .\scripts\build_ch02_plecs_model.py
python .\scripts\ch02_plecs_three_phase_bridge.py
matlab -batch "run('D:/1codex/BLDC/scripts/ch02_three_phase_bridge_tests.m')"
```

## 期望输出

```text
Generated models\plecs\ch02_three_phase_bridge\ch02_three_phase_bridge.plecs
Generated chapter 02 PLECS bridge evidence. scenarios=7 pass=7 time_points=201 signals=14 gate_combinations=64 elapsed_s=<总耗时>
Generated chapter 02 MATLAB post-processing. scenarios=7 pass=7 figures=2
```

## 最新指标

| 场景 | 末值 ia/A | 末值 ib/A | 末值 ic/A | 峰值线电压/V | 结果 |
|---|---:|---:|---:|---:|---|
| `Apos_Bneg` | 14.6509 | -14.6509 | 0 | 48 | PASS |
| `Apos_Cneg` | 14.6509 | 0 | -14.6509 | 48 | PASS |
| `Bpos_Cneg` | 0 | 14.2426 | -14.2426 | 48 | PASS |
| `Bpos_Aneg` | -14.6516 | 14.6516 | 0 | 48 | PASS |
| `Cpos_Aneg` | -14.6516 | 0 | 14.6516 | 48 | PASS |
| `Cpos_Bneg` | 0 | -14.2426 | 14.2426 | 48 | PASS |
| `all_off` | 0 | 0 | 0 | 0 | PASS |

门极审计固定为 64 组：37 组含同桥臂直通请求、6 组是六步有效矢量、21 组是其他无直通状态。

## 生成物

| 类型 | 路径 |
|---|---|
| PLECS 模型 | `models/plecs/ch02_three_phase_bridge/ch02_three_phase_bridge.plecs` |
| 代表场景逐点数据 | `waveforms/02-three-phase-bridge/plecs_Apos_Bneg.csv` |
| 七场景逐点数据 | `waveforms/02-three-phase-bridge/plecs_*.csv` |
| 场景汇总 | `waveforms/02-three-phase-bridge/plecs_bridge_summary.csv` |
| 门极全组合 | `waveforms/02-three-phase-bridge/gate_truth_table.csv` |
| PLECS 原生截图 | `assets/02-three-phase-bridge/plecs_scope_Apos_Bneg.png` |
| MATLAB 路径图 | `assets/02-three-phase-bridge/plecs_bridge_paths.png` |
| MATLAB 门极矩阵 | `assets/02-three-phase-bridge/gate_truth_table_matrix.png` |
| 测试报告 | `reports/02-three-phase-bridge-test_report.md` |

## 常见失败

| 现象 | 检查 |
|---|---|
| `PLECS_RPC_NOT_READY` | PLECS 是否运行，XML-RPC 是否启用，端口是否为 1080 |
| `MODEL_MISSING` | 是否先运行 `build_ch02_plecs_model.py` |
| PLECS 输出不是 14 路 | 模型输出端口是否被手工改动，重新运行模型生成脚本 |
| PLECS 场景出现 FAIL | 先读 `plecs_bridge_summary.csv` 的 `reason`，检查电流方向、悬空相电流、KCL 和线电压 |
| Scope 截图不存在 | PLECS Scope 是否能正常打开，窗口标题是否包含 `ch02_three_phase_bridge/Scope` |
| MATLAB 断言失败 | 确认 Python 场景已经 7/7 PASS，再运行 MATLAB |

## 结果边界

本实验使用真实 PLECS 两电平 IGBT 变流器和 BLDC Machine 绕组，能够证明三值相命令到线电压、相电流的因果链。模型没有加入门极驱动传播延迟、死区、器件损耗和硬件保护锁存。

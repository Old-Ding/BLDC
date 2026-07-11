# BLDC 教程：从三相桥、六步换相到固件与 FOC

这是一套以可复现实验包为主体的 BLDC 技术教程。PLECS/Simulink 负责功率级和电机主证据，MATLAB 负责参数计算、扫参和数据后处理，C 负责可移植控制逻辑。

教程先完成 Hall 六步闭环，再进入嵌入式固件、无感六步和 FOC。完整 00-36 篇路线见 [`docs/series-plan.md`](docs/series-plan.md)。

## 当前状态

| 项目 | 当前结果 |
|---|---|
| 当前阶段 | 阶段 A：功率级与电机物理基础 |
| 最新完成实验 | 第 01 章 PLECS BLDC 基准实验 |
| 最新文章 | [`blog/01-bldc-control-chain.md`](blog/01-bldc-control-chain.md) |
| 复现说明 | [`docs/01-bldc-control-chain-reproduce.md`](docs/01-bldc-control-chain-reproduce.md) |
| 最新模型 | [`models/plecs/ch01_bldc_baseline/ch01_bldc_baseline.plecs`](models/plecs/ch01_bldc_baseline/ch01_bldc_baseline.plecs) |
| 下一章 | 第 02 章真实三相桥开关状态实验 |
| GitHub | https://github.com/Old-Ding/BLDC |

## 工具分工

| 工具 | 职责 |
|---|---|
| PLECS / Simulink | 开关功率级、反电动势、相电流、转矩、转速和完整闭环主图 |
| MATLAB | 读取 PLECS CSV、参数计算、控制器设计、批量扫参与辅助图 |
| C | 换相表、Hall 解码、测速、PI、保护和状态机的唯一职责层 |
| Python / PowerShell | 调用工具、运行场景、导出 CSV/trace、生成报告 |

## 已完成文章

| 篇章 | 标题 | 证据 | 状态 |
|---:|---|---|---|
| 00 | [`BLDC 完整学习路线`](blog/00-bldc-learning-route.md) | 路线和仓库入口 | 路线文章 |
| 01 | [`让 BLDC 在 PLECS 里真正转起来`](blog/01-bldc-control-chain.md) | PLECS 模型、2 个场景、1202 行逐点数据、4 张图、报告 | 三轮复核通过，待同步 GitHub/CSDN |
| 02 | [`三相桥的 6 个开关`](blog/02-three-phase-bridge.md) | 旧 MATLAB 状态图 | 草稿；需重建真实 PLECS 功率桥后再发布 |

## 第 01 章快速复现

PLECS Standalone 需要启用 XML-RPC，端口为 `1080`。

```powershell
git clone https://github.com/Old-Ding/BLDC.git
Set-Location .\BLDC
python .\scripts\ch01_plecs_bldc_baseline.py
matlab -batch "run('scripts/ch01_control_chain_demo.m')"
```

期望输出：

```text
Generated chapter 01 PLECS baseline. scenarios=2 pass=2 time_points=601 signals=11 elapsed_s=<总耗时>
Generated chapter 01 MATLAB post-processing. scenarios=2 pass=2 figures=2
```

最近一次结果：

| 场景 | 负载转矩 | 相电流峰值 | 尾段转速 | 尾段电磁转矩 | 结果 |
|---|---:|---:|---:|---:|---|
| `nominal_load` | 3 N m | 5.9941 A | 3490.23 rpm | 2.9936 N m | PASS |
| `overload` | 6 N m | 5.9982 A | 271.99 rpm | 4.0098 N m | PASS |

过载 PASS 的含义是正确复现“电流受限、转矩不足、转速塌落”，不是表示过载时满足速度要求。

## 第 01 章证据链

```text
models/plecs/ch01_bldc_baseline/ch01_bldc_baseline.plecs
  -> scripts/ch01_plecs_bldc_baseline.py
  -> waveforms/01-bldc-control-chain/plecs_*.csv
  -> reports/01-bldc-control-chain-test_report.md
  -> scripts/ch01_control_chain_demo.m
  -> assets/01-bldc-control-chain/plecs_*.png
  -> blog/01-bldc-control-chain.md
```

PLECS Scope 主图由模型内的 `Export Chapter 01 Scope Evidence` 脚本直接导出。MATLAB 图只读取 PLECS CSV，不重新构造电机响应。

## 目录结构

```text
BLDC/
├── assets/                 # PLECS Scope 和 MATLAB 后处理图
├── blog/                   # GitHub/CSDN 教学正文
├── docs/                   # 总纲和逐章复现说明
├── learning_model/         # 历史信号拆层模型，仅作参考
├── models/plecs/           # 正式 PLECS 实验模型
├── reports/                # 参数、指标和 PASS/FAIL 报告
├── scripts/                # PLECS RPC、MATLAB 和生成脚本
└── waveforms/              # 逐点 CSV、汇总 CSV 和 PLECS trace
```

`learning_model/steps` 中旧的 `Clock -> C-Script -> Scope` 模型不能作为功率级或电机主证据。后续正式模型统一进入 `models/plecs`。

## 发布规则

每个正式章节必须先完成模型、场景、CSV、主图、报告和复现文档，再同步 GitHub。CSDN 使用 GitHub/jsDelivr 可访问图片并默认保存草稿；最终发布按钮需要当前回合单独确认。

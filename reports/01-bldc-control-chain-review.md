# 第 01 章发布前复核记录

本文件记录实际检查对象、发现项和修改结果。复核结论不作为文章正文内容。

## 工程一致性复核

检查对象：

- `models/plecs/ch01_bldc_baseline/ch01_bldc_baseline.plecs`
- `scripts/ch01_plecs_bldc_baseline.py`
- `scripts/ch01_control_chain_demo.m`
- `waveforms/01-bldc-control-chain/plecs_*.csv`
- `reports/01-bldc-control-chain-test_report.md`
- `blog/01-bldc-control-chain.md`

发现与修改：

| 发现 | 风险 | 修改结果 |
|---|---|---|
| 旧 MATLAB 信号演示图和 CSV 仍与正式证据混放 | 读者可能把信号示意误认为 PLECS 电机仿真 | 删除 2 张旧图和 2 份旧 CSV，只保留 PLECS 数据链 |
| 公开命令写死 `D:` 本机路径 | GitHub 读者无法直接复现 | 改为 `git clone`、相对路径和仓库内脚本入口 |
| RPC 异常时缺少可见进度和等待上限 | PLECS 卡在对话框时难以判断脚本状态 | 增加逐场景 START/DONE、120 s RPC 超时和明确退出信息 |
| 第 00 篇仍是旧 00-11 路线 | 仓库入口与 00-36 总纲冲突 | 重写第 00 篇和复现文档，统一五阶段路线 |
| 模型输出与 CSV 列缺少强约束 | Outport 改动后可能错列生成报告 | 固定 5 个 Outport、11 路输出，数量不一致立即失败 |
| 三值相命令被命名为 `gate_a/b/c` | 容易误读为六路 IGBT 门极信号 | 改为 `phase_cmd_a/b/c`，并在正文和模型说明中明确门极展开属于第 02 章 |

一致性结果：

- PLECS 模型包含两电平 IGBT 三相桥、BLDC Machine、三相电流测量、机械负载和转速/转矩探针。
- `nominal_load` 与 `overload` 均由同一模型、同一母线和同一电流参考生成。
- 每个场景 601 行数据、13 个 CSV 字段；汇总报告为 2/2 PASS。
- 正文中的 5.9941 A、5.9982 A、3490.23 rpm、271.99 rpm、2.9936 N m、4.0098 N m 与汇总 CSV 一致。

## 视觉与信息层级复核

检查对象：

| 图 | 尺寸 | 来源 |
|---|---:|---|
| `plecs_scope_nominal_load.png` | 1800 x 1350 | PLECS Scope 直接导出 |
| `plecs_scope_overload.png` | 1800 x 1350 | PLECS Scope 直接导出 |
| `plecs_load_comparison.png` | 1865 x 1454 | MATLAB 读取 PLECS CSV |
| `plecs_commutation_zoom.png` | 1860 x 1486 | MATLAB 读取 PLECS CSV |

发现与修改：

| 发现 | 修改结果 |
|---|---|
| 初版对比图的参考线文字压住曲线 | 将参考线改为图例项，并给转矩/电流纵轴保留余量 |
| PLECS 与 MATLAB 图来源容易混淆 | 正文标题、图前说明和文件名均写明来源；MATLAB 图明确为 PLECS CSV 后处理 |
| 一张图有多行子图但缺少阅读顺序 | 每张图后按子图逐项说明先看什么和能得出什么结论 |
| 换相局部图纵轴写成 `Gate command` | 改为 `Phase command`，避免把三值相命令误读成器件门极电平 |

视觉检查结果：4 张图均非空白，坐标、单位、曲线和图例可辨认，没有文字遮挡正文或图片路径失效。

## 读者理解复核

检查对象：第 00 篇路线、第 01 篇正文、两份复现文档和仓库索引。

发现与修改：

| 检查点 | 修改结果 |
|---|---|
| 第 01 篇是否从读者问题进入 | 以“同样 5 A，3 N m 能维持、6 N m 为什么失速”作为开场现象 |
| 是否先给因果模型再给参数和文件 | 文章顺序调整为现象、物理链、公式、参数、场景、图、边界、复现、文件索引 |
| 文件清单是否过早出现 | 完整文件索引移到文章后半段 |
| 边界是否像作者辩解 | 改为“已观察证据、可得结论、不要误读成”三列表 |
| 结尾是否制造多章任务压力 | 只预告第 02 章的一个问题：三值相命令怎样变成六路门极信号 |
| 路线入口是否与总纲一致 | 第 00 篇改为 00-36 五阶段路线，并明确路线文章不冒充实验章 |

## 验证命令

```powershell
python -m py_compile .\scripts\ch01_plecs_bldc_baseline.py
python .\scripts\ch01_plecs_bldc_baseline.py
matlab -batch "run('scripts/ch01_control_chain_demo.m')"
git diff --check
```

最近一次结果：

```text
Generated chapter 01 PLECS baseline. scenarios=2 pass=2 time_points=601 signals=11 elapsed_s=<总耗时>
Generated chapter 01 MATLAB post-processing. scenarios=2 pass=2 figures=2
```

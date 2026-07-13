# 第 01 章发布前复核记录

复核日期：2026-07-13

本文件记录第 01 章的工程、视觉写作和读者理解检查。复核结论不写入公开教程正文。

## 工程一致性复核

检查对象：

- `models/plecs/ch01_bldc_baseline/ch01_bldc_baseline.plecs`
- `scripts/ch01_plecs_bldc_baseline.py`
- `scripts/ch01_control_chain_demo.m`
- `waveforms/01-bldc-control-chain/plecs_*.csv`
- `reports/01-bldc-control-chain-test_report.md`
- `blog/01-bldc-control-chain.md`

| 检查项 | 证据 | 结果 |
|---|---|---|
| 初始转速换算 | `300 * 60 / (2π) = 2864.79 rpm` | 正文写为约 2865 rpm |
| 额定场景 | 峰值电流 5.9941 A，尾段平均转矩 2.9936 N m，负载 3 N m | 数字和结论一致 |
| 过载场景 | 峰值电流 5.9982 A，尾段平均转矩 4.0098 N m，负载 6 N m | 转矩缺口 1.9902 N m |
| 尾段均值与最终值 | 尾段平均转速 271.99 rpm，最终速度 -1.26 rad/s | 正文明确区分，未把均值写成稳定值 |
| 5 A 参考与约 6 A 峰值 | PLECS 电流控制器 Relay 阈值为 `+1/-1` | 峰值来自滞环范围，不判为失控 |
| 场景单变量 | 两组场景只改变 `load_torque_Nm` | 可以把响应差异归因到负载 |
| 仿真职责 | Python 调用 `plecs.simulate`，MATLAB 仅读取 CSV | 未把 MATLAB 后处理误写成电机仿真 |

本次未修改 PLECS 模型、场景定义和逐点数据，因此没有重写 PLECS 结果。MATLAB 后处理脚本已实际运行，输出为：

```text
Generated chapter 01 MATLAB post-processing. scenarios=2 pass=2 figures=2
```

## 视觉与写作复核

检查了 3 张正文图片及其前后说明：

| 图片 | 尺寸 | 来源 | 正文用途 |
|---|---:|---|---|
| `plecs_load_comparison.png` | 1865 x 1275 | MATLAB 读取 PLECS CSV | 先比较平均转矩与负载，再看转速趋势 |
| `plecs_scope_nominal_load.png` | 1800 x 1350 | PLECS Scope 直接导出 | 核对额定负载尾段原始波形 |
| `plecs_scope_overload.png` | 1800 x 1350 | PLECS Scope 直接导出 | 核对过载尾段原始波形 |

发现与修改：

| 发现 | 修改结果 |
|---|---|
| 原对比图同时堆叠速度、瞬时转矩和电流，首轮阅读信息过密 | 改为两行图：转速曲线 + 平均电磁转矩/负载柱状图 |
| PLECS 原图使用元件原生英文图例 | 增加 `Stator Phase`、`Back EMF`、`Motor`、`Machine` 对照表 |
| 原文要求从四行 Scope 同时推理 | 改为固定读图顺序：速度 -> 转矩 -> 平均值 -> 电流 |
| 换相局部图偏离第 01 章的转矩平衡主线 | 从公开正文移除，文件仍保留供对应换相内容使用 |
| 参数表和完整控制链出现过早 | 移到手算和第一张结论图之后 |

图片均已目视检查，曲线、坐标、图例和柱状图数值可辨认，没有空白图或文字遮挡。

## 读者理解复核

根因检查结论：原文虽然数据完整，但在读者尚未理解净转矩时，同时引入五层控制链、反电动势、`e*i`、三值相命令和 PLECS 元件名，首轮阅读负担过高。

重写后的理解路径：

```text
区分电流、转矩、负载、转速
  -> 手算 Te - TL
  -> 从柱状图比较平均转矩与负载
  -> 从转速曲线验证加减速方向
  -> 回到 PLECS 原始 Scope 核对证据
  -> 用四个问题检查是否能独立复述
```

读者完成第 01 章后应能回答：

1. 为什么 `Te = TL` 时转速不必为 0。
2. 为什么 5 A 不能直接解释成 5 N m。
3. 为什么过载场景中有电流仍会减速。
4. 为什么初始速度 300 rad/s 的实验不能证明静止启动。
5. 遇到掉速时应先比较哪些量。

公开语气检查结果：`check_public_voice.ps1` 对正文返回 0 个命中。正文不包含写作方法比较、复核过程、课程设计辩解或发布操作记录。

## 验证记录

```powershell
python -m py_compile .\scripts\ch01_plecs_bldc_baseline.py
matlab -batch "run('scripts/ch01_control_chain_demo.m')"
& "$env:USERPROFILE\.codex\skills\technical-series-author\scripts\check_public_voice.ps1" -Path .\blog\01-bldc-control-chain.md
git diff --check
```

结果：

- Python 语法检查通过。
- MATLAB 后处理运行通过，2 个场景、2 张图片。
- 公开语气检查通过，0 个命中。
- 正文内 3 个图片链接和 1 个复现文档链接均可解析。
- UTF-8 无 BOM，CRLF 换行。
- `git diff --check` 通过。

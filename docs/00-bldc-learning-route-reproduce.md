# 第 00 篇复现：BLDC 完整课程路线

第 00 篇是路线文章，不运行电机仿真。复现目标是确认 00-36 篇阶段划分、工具职责、正式章节证据门槛和第 01 章入口在仓库中一致。

## 环境

| 项目 | 要求 |
|---|---|
| 系统 | Windows 11 或可运行 Git/Markdown 的其他系统 |
| Shell | 本仓库命令以 PowerShell 为准 |
| 文件编码 | UTF-8 |
| PLECS / MATLAB | 路线检查不需要；从正式实验章开始使用 |

## 获取仓库

```powershell
git clone https://github.com/Old-Ding/BLDC.git
Set-Location .\BLDC
```

## 检查路线入口

```powershell
Get-Content -LiteralPath .\README.md -Encoding UTF8
Get-Content -LiteralPath .\blog\README.md -Encoding UTF8
Get-Content -LiteralPath .\docs\series-plan.md -Encoding UTF8
```

期望能找到：

```text
阶段 A：功率级与电机物理基础
阶段 B：Hall 六步闭环
阶段 C：嵌入式固件工程
阶段 D：无感六步控制
阶段 E：FOC 扩展与路线比较
```

## 检查第 01 章实验入口

```powershell
Test-Path .\models\plecs\ch01_bldc_baseline\ch01_bldc_baseline.plecs
Test-Path .\scripts\ch01_plecs_bldc_baseline.py
Test-Path .\blog\01-bldc-control-chain.md
Test-Path .\docs\01-bldc-control-chain-reproduce.md
```

四条命令都应返回：

```text
True
```

## 检查路线与索引是否仍使用旧篇章

```powershell
rg -n "00-36|06-14|15-22|23-29|30-36" README.md blog\README.md docs\series-plan.md
```

输出应同时覆盖仓库首页、文章索引和实施总纲。

## 历史模型的定位

`learning_model/steps` 中的 Step 01 到 Step 08 是早期信号拆层材料。它们可以帮助查看控制变量，但不包含正式章节要求的完整功率级、电机场景、CSV 和主图。

正式章节采用以下目录：

```text
models/plecs
scripts
waveforms
assets
reports
docs
blog
```

## 路线文章的证据边界

第 00 篇确认学习依赖、工具分工和发布规则。它不会给出某个参数集的电机性能结论；第 01 章开始，每个正式实验章都必须用模型、场景、数据、图和报告回答自己的核心问题。

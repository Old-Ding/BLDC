# 第 01 章 PLECS BLDC 基准模型

## 模型用途

本模型把第 01 章需要观察的完整物理链放在同一张 PLECS 原理图中：

```text
电流参考 + 转子角度
  -> 电流换相控制器
  -> 两电平三相 IGBT 逆变器
  -> 三相电流
  -> BLDC 反电动势与电磁转矩
  -> 转动惯量和负载转矩
  -> 机械转速
```

它回答的是“相电流如何形成电磁转矩，以及负载超过可用转矩时为什么会失速”。Hall 量化、速度 PI、死区和保护状态机不在本模型内。

## 来源与改动

仓库模型由 PLECS Standalone 5.0.2 自带的 `brushless_dc_machine` 示例改造而来。原始示例入口为：

```text
<PLECS 安装目录>/demos/brushless_dc_machine/brushless_dc_machine.plecs
```

仓库版本增加了以下可复现接口：

- 将 `Udc_V`、`load_torque_Nm`、`current_ref_A` 设为集中参数。
- 增加 5 个顶层 Outport，使 RPC 能读取 11 路逐点信号。
- 增加 `Export Chapter 01 Scope Evidence` 仿真脚本，直接导出正式 PLECS Scope 主图。
- 保留 PLECS 标准 `2-Level IGBT Conv.` 和 `BLDC Machine` 元件，不用 MATLAB 信号图替代功率级和电机响应。

## 顶层输出

| Outport | 展开后的列 | 单位 | 用途 |
|---:|---|---|---|
| 1 | `ia_A`、`ib_A`、`ic_A` | A | 三相定子电流 |
| 2 | `ea_V`、`eb_V`、`ec_V` | V | 三相反电动势 |
| 3 | `speed_rad_s` | rad/s | 机械角速度 |
| 4 | `electromagnetic_torque_Nm` | N m | 电磁转矩 |
| 5 | `phase_cmd_a`、`phase_cmd_b`、`phase_cmd_c` | 1 | 三值相命令，`1/0/-1` 表示该桥臂接正母线/悬空/接负母线；不是六路 IGBT 门极信号 |

## 运行入口

先在 PLECS Preferences 中启用 XML-RPC，端口设为 `1080`，再执行：

```powershell
python .\scripts\ch01_plecs_bldc_baseline.py
```

生成正式 Scope 位图时，在 PLECS 中打开模型，选择：

```text
Simulation -> Simulation scripts...
-> Export Chapter 01 Scope Evidence
-> Run
```

脚本会生成：

```text
assets/01-bldc-control-chain/plecs_scope_nominal_load.png
assets/01-bldc-control-chain/plecs_scope_overload.png
```

# BLDC 教程：从六步换相到速度闭环

这个仓库用于编写一套可复现的 BLDC 教程。当前最优主线是先完成六步换相闭环，不提前混入工程保护和 FOC。

## 当前阶段

| 项目 | 状态 |
|---|---|
| 教程主线 | 第一阶段：六步 BLDC 最小闭环 |
| 仿真工具 | PLECS 为主，MATLAB 用于计算、扫参和画图 |
| 控制逻辑 | C 代码表达唯一职责层 |
| 文章入口 | `blog/00-bldc-learning-route.md` |
| 复现说明 | `docs/00-bldc-learning-route-reproduce.md` |
| GitHub 仓库 | https://github.com/Old-Ding/BLDC |

## 工具分工

| 工具 | 职责 |
|---|---|
| PLECS | 电机、三相桥、PWM、负载、Scope 波形和完整系统仿真 |
| MATLAB | 参数计算、公式验证、PI 扫参、数据处理和图表导出 |
| C | 换相表、Hall 解码、速度估算、速度 PI、状态机等控制逻辑原型 |
| Markdown | 教程正文、复现实验、文件映射和发布前检查 |

## 第一阶段教程

| 篇章 | 标题 | 对应材料 |
|---:|---|---|
| 00 | 为什么 BLDC 教程要从最小模型开始 | `blog/00-bldc-learning-route.md` |
| 01 | BLDC 控制链总览 | `learning_model/steps/README.md` |
| 02 | 三相桥的 6 个开关 | `learning_model/steps/step_01_three_phase_bridge` |
| 03 | 电角度、机械角度和极对数 | `learning_model/steps/step_06_speed_estimation` |
| 04 | 六步换相表 | `learning_model/steps/step_02_six_step_table` |
| 05 | 开环换相 | `learning_model/steps/step_03_open_loop_commutation` |
| 06 | 开环为什么会失步 | `learning_model/steps/step_03_open_loop_commutation` |
| 07 | Hall 状态与六步换相 | `learning_model/steps/step_04_hall_commutation` |
| 08 | PWM 占空比 | `learning_model/steps/step_05_pwm_duty` |
| 09 | Hall 边沿测速 | `learning_model/steps/step_06_speed_estimation` |
| 10 | 速度 PI 闭环 | `learning_model/steps/step_07_speed_pi` |
| 11 | 回到 PLECS 完整模型 | `learning_model/steps/step_08_plecs_full_model` |

完整规划见 `docs/series-plan.md`。

## 现有模型入口

```text
learning_model/steps/README.md
```

Step 01 到 Step 07 是信号级 PLECS 教学模型，统一结构是：

```text
Clock -> StepLogic(C-Script) -> Demux -> Scope
```

这些模型用于观察控制变量，不证明真实电机、绕组电流、机械负载和硬件驱动已经可用。Step 08 才进入完整 BLDC 电机模型对照。

## 常用命令

```powershell
Set-Location D:\1codex\BLDC
powershell -ExecutionPolicy Bypass -File .\learning_model\steps\generate_step_plecs.ps1
python .\learning_model\steps\test_step_plecs_models.py
```

运行 `test_step_plecs_models.py` 前需要先启动 PLECS RPC 服务。没有启动时，脚本会报告 `PLECS_RPC_NOT_READY`，这表示仿真服务未连接，不表示教程结构错误。

## 发布边界

CSDN 发布前需要先满足三个条件：

1. 每篇文章有对应模型、代码、截图或数据表作为证据。
2. 图片使用 GitHub/jsDelivr 或 CSDN 可访问链接，不使用本地 Windows 路径。
3. 只保存 CSDN 草稿，最终发布必须单独确认。

## 当前工程状态

当前仓库用于同步教程正文、复现说明和 PLECS 学习模型。CSDN 发布前优先使用 GitHub 公开文件作为配套材料入口。

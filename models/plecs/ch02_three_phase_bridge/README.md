# 第 02 章 PLECS 三相桥模型

`ch02_three_phase_bridge.plecs` 从第 01 章已验证 BLDC 母模型确定性派生，保留直流源、两电平 IGBT 变流器、三相测量和 BLDC Machine。

本章只替换控制器：模型变量 `phase_cmd=[A B C]` 使用 `+1/0/-1` 表示每个桥臂的上桥、全关和下桥状态。

## 输入变量

| 变量 | 默认值 | 单位 | 说明 |
|---|---:|---|---|
| `Udc_V` | 48 | V | 直流母线电压 |
| `phase_cmd` | `[0 0 0]` | - | 三值相命令 |
| `initial_speed_rad_s` | 0 | rad/s | BLDC 初始机械角速度 |
| `load_torque_Nm` | 0 | N m | 机械负载，本章固定为 0 |

## 输出接口

RPC 返回 14 路信号：三相电流、三相反电动势、机械角速度、电磁转矩、三值相命令和三路线电压。

## 生成与运行

```powershell
python .\scripts\build_ch02_plecs_model.py
python .\scripts\ch02_plecs_three_phase_bridge.py
```

生成脚本存在的原因是避免手工复制大型 `.plecs` 文件时遗漏端口或参数；正式模型文件仍随仓库提交，可直接在 PLECS 中打开。

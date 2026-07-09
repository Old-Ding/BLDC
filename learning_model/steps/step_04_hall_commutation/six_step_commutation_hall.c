// PLECS C-Script: BLDC 有霍尔六步换相
//
// 输入:
//   in[0] = Hall A
//   in[1] = Hall B
//   in[2] = Hall C
//
// 输出顺序必须和三相桥 Gate 输入一致:
//   out[0] = A 相上桥臂
//   out[1] = B 相上桥臂
//   out[2] = C 相上桥臂
//   out[3] = A 相下桥臂
//   out[4] = B 相下桥臂
//   out[5] = C 相下桥臂
//
// 为什么只在这里处理非法霍尔状态:
// 换相表是“霍尔状态 -> 桥臂命令”的唯一职责层。0 和 7 不属于
// 三相霍尔的有效扇区，直接关断能避免错误状态继续传到功率级。

int hall = (int)(4.0 * in[2] + 2.0 * in[1] + in[0]);

out[0] = 0.0;
out[1] = 0.0;
out[2] = 0.0;
out[3] = 0.0;
out[4] = 0.0;
out[5] = 0.0;

switch (hall) {
    case 5:  // 101: A+ B-
        out[0] = 1.0;
        out[4] = 1.0;
        break;

    case 1:  // 001: A+ C-
        out[0] = 1.0;
        out[5] = 1.0;
        break;

    case 3:  // 011: B+ C-
        out[1] = 1.0;
        out[5] = 1.0;
        break;

    case 2:  // 010: B+ A-
        out[1] = 1.0;
        out[3] = 1.0;
        break;

    case 6:  // 110: C+ A-
        out[2] = 1.0;
        out[3] = 1.0;
        break;

    case 4:  // 100: C+ B-
        out[2] = 1.0;
        out[4] = 1.0;
        break;

    default:
        break;
}

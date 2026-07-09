// 最小六步换相表。
// 为什么只接收 step：换相表的职责是“电角度扇区 -> 桥臂命令”，
// step 的来源留给开环时序或霍尔解码层处理。

typedef struct {
    int ah;
    int bh;
    int ch;
    int al;
    int bl;
    int cl;
} BridgeGates;

static BridgeGates all_gates_off(void)
{
    BridgeGates gates = {0, 0, 0, 0, 0, 0};
    return gates;
}

BridgeGates six_step_to_gates(int step)
{
    BridgeGates gates = all_gates_off();

    switch (step) {
        case 0:  // A+ B-
            gates.ah = 1;
            gates.bl = 1;
            break;

        case 1:  // A+ C-
            gates.ah = 1;
            gates.cl = 1;
            break;

        case 2:  // B+ C-
            gates.bh = 1;
            gates.cl = 1;
            break;

        case 3:  // B+ A-
            gates.bh = 1;
            gates.al = 1;
            break;

        case 4:  // C+ A-
            gates.ch = 1;
            gates.al = 1;
            break;

        case 5:  // C+ B-
            gates.ch = 1;
            gates.bl = 1;
            break;

        default:
            break;
    }

    return gates;
}

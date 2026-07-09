// 最小三相桥状态模型。
// 为什么先建这个模型：换相、PWM、闭环都要落到 6 个桥臂命令，
// 如果这里没看懂，后面看到 pulses 只会变成一团黑盒。

typedef struct {
    int ah;
    int bh;
    int ch;
    int al;
    int bl;
    int cl;
} BridgeGates;

typedef enum {
    PHASE_FLOAT = 0,
    PHASE_LOW = -1,
    PHASE_HIGH = 1,
    PHASE_FAULT = 2
} PhaseState;

typedef struct {
    PhaseState a;
    PhaseState b;
    PhaseState c;
    int shoot_through;
} BridgeState;

static PhaseState half_bridge_state(int high, int low, int *shoot_through)
{
    if (high && low) {
        *shoot_through = 1;
        return PHASE_FAULT;
    }

    if (high) {
        return PHASE_HIGH;
    }

    if (low) {
        return PHASE_LOW;
    }

    return PHASE_FLOAT;
}

BridgeState bridge_state(BridgeGates gates)
{
    BridgeState state;

    state.shoot_through = 0;
    state.a = half_bridge_state(gates.ah, gates.al, &state.shoot_through);
    state.b = half_bridge_state(gates.bh, gates.bl, &state.shoot_through);
    state.c = half_bridge_state(gates.ch, gates.cl, &state.shoot_through);

    return state;
}

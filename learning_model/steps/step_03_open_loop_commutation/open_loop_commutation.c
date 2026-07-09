// 最小开环换相模型。
// 为什么独立成一层：开环只决定 step 何时前进，
// 不应该同时处理 Hall、速度估算或 PI。

typedef struct {
    int step;
    unsigned int tick_count;
    unsigned int ticks_per_step;
} OpenLoopCommutator;

void open_loop_init(OpenLoopCommutator *commutator, unsigned int ticks_per_step)
{
    commutator->step = 0;
    commutator->tick_count = 0;
    commutator->ticks_per_step = ticks_per_step;
}

int open_loop_update(OpenLoopCommutator *commutator)
{
    commutator->tick_count++;

    if (commutator->tick_count >= commutator->ticks_per_step) {
        commutator->tick_count = 0;
        commutator->step++;

        if (commutator->step >= 6) {
            commutator->step = 0;
        }
    }

    return commutator->step;
}

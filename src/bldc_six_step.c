#include "bldc_six_step.h"

BldcPhaseCommand bldc_six_step_command(unsigned int step, int direction)
{
    static const BldcPhaseCommand forward[6] = {
        { 1, -1,  0},
        { 1,  0, -1},
        { 0,  1, -1},
        {-1,  1,  0},
        {-1,  0,  1},
        { 0, -1,  1},
    };
    unsigned int index = step % 6U;

    /* 反向只改变表的读取顺序，桥臂状态定义保持唯一。 */
    if (direction < 0 && index != 0U) {
        index = 6U - index;
    }
    return forward[index];
}

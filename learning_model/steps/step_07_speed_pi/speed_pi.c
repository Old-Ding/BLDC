// 最小速度 PI 模型。
// 为什么只输出 duty：速度环负责“要多少能量”，PWM 层负责“怎么调制能量”。

typedef struct {
    double kp;
    double ki;
    double dt_s;
    double integral_min;
    double integral_max;
    double duty_min;
    double duty_max;
} SpeedPiParams;

typedef struct {
    double integral;
} SpeedPiState;

static double clamp_value(double value, double min_value, double max_value)
{
    if (value < min_value) {
        return min_value;
    }

    if (value > max_value) {
        return max_value;
    }

    return value;
}

double speed_pi_update(
    SpeedPiState *state,
    const SpeedPiParams *params,
    double target_rpm,
    double actual_rpm)
{
    double error = target_rpm - actual_rpm;
    double output;

    state->integral += error * params->dt_s;
    state->integral = clamp_value(
        state->integral,
        params->integral_min,
        params->integral_max);

    output = params->kp * error + params->ki * state->integral;
    return clamp_value(output, params->duty_min, params->duty_max);
}

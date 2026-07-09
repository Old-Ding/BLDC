// 最小高边 PWM 调制模型。
// 为什么 PWM 层不做 duty 限幅：duty 的合法范围由产生 duty 的层负责，
// 这里重复修正会掩盖上游调参或闭环输出问题。

typedef struct {
    double ah;
    double bh;
    double ch;
    double al;
    double bl;
    double cl;
} GateCommand;

GateCommand apply_high_side_pwm(GateCommand commutation, double duty, double carrier)
{
    GateCommand output = commutation;
    double pwm_on = carrier < duty ? 1.0 : 0.0;

    output.ah = commutation.ah * pwm_on;
    output.bh = commutation.bh * pwm_on;
    output.ch = commutation.ch * pwm_on;

    return output;
}

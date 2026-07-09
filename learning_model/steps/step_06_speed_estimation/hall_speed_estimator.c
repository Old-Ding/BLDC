// 最小 Hall 速度估算模型。
// 为什么用边沿周期：低速时单位时间计数太少，测周期更容易看到变化。

double hall_edge_period_to_rpm(double edge_period_s, int pole_pairs)
{
    double edges_per_mechanical_rev;

    if (edge_period_s <= 0.0 || pole_pairs <= 0) {
        return 0.0;
    }

    edges_per_mechanical_rev = (double)pole_pairs * 6.0;
    return 60.0 / (edge_period_s * edges_per_mechanical_rev);
}

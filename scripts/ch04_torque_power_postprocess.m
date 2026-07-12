% 第 04 章：读取 PLECS 功率核对 CSV，生成逐点能量转换图。

script_dir = fileparts(mfilename('fullpath'));
root_dir = fileparts(script_dir);
waveform_dir = fullfile(root_dir, 'waveforms', '04-torque-power');
asset_dir = fullfile(root_dir, 'assets', '04-torque-power');
if ~exist(asset_dir, 'dir'); mkdir(asset_dir); end

nominal = readtable(fullfile(waveform_dir, 'plecs_power_nominal_load.csv'), 'VariableNamingRule', 'preserve');
overload = readtable(fullfile(waveform_dir, 'plecs_power_overload.csv'), 'VariableNamingRule', 'preserve');
regen = readtable(fullfile(waveform_dir, 'plecs_power_regenerative_braking.csv'), 'VariableNamingRule', 'preserve');
summary = readtable(fullfile(waveform_dir, 'plecs_power_summary.csv'), 'VariableNamingRule', 'preserve');
assert(all(strcmp(summary.result, 'PASS')), '第 04 章功率等式存在未通过场景。');

fig = figure('Color', 'w', 'Position', [100 80 1550 1050]);
layout = tiledlayout(fig, 4, 1, 'TileSpacing', 'compact', 'Padding', 'compact');
title(layout, 'PLECS nominal load: back-EMF power becomes electromagnetic mechanical power');
t_ms = nominal.time_s * 1e3;

nexttile;
plot(t_ms, nominal.ea_V, 'LineWidth', 1.2); hold on;
plot(t_ms, nominal.eb_V, 'LineWidth', 1.2); plot(t_ms, nominal.ec_V, 'LineWidth', 1.2);
ylabel('back EMF / V'); grid on; legend('e_a','e_b','e_c','Location','eastoutside');

nexttile;
plot(t_ms, nominal.ia_A, 'LineWidth', 1.2); hold on;
plot(t_ms, nominal.ib_A, 'LineWidth', 1.2); plot(t_ms, nominal.ic_A, 'LineWidth', 1.2);
ylabel('phase current / A'); grid on; legend('i_a','i_b','i_c','Location','eastoutside');

nexttile;
plot(t_ms, nominal.phase_a_power_W, 'LineWidth', 1.1); hold on;
plot(t_ms, nominal.phase_b_power_W, 'LineWidth', 1.1); plot(t_ms, nominal.phase_c_power_W, 'LineWidth', 1.1);
yline(0, ':'); ylabel('e_k i_k / W'); grid on; legend('e_ai_a','e_bi_b','e_ci_c','Location','eastoutside');

nexttile;
plot(t_ms, nominal.electrical_conversion_power_W, 'LineWidth', 1.5); hold on;
plot(t_ms, nominal.mechanical_power_W, '--', 'LineWidth', 1.5);
ylabel('power / W'); xlabel('time / ms'); grid on;
legend('\Sigma e_k i_k','T_e\omega_m','Location','eastoutside');
exportgraphics(fig, fullfile(asset_dir, 'plecs_ei_to_torque_nominal.png'), 'Resolution', 180);
close(fig);

fig = figure('Color', 'w', 'Position', [120 100 1500 900]);
layout = tiledlayout(fig, 3, 1, 'TileSpacing', 'compact', 'Padding', 'compact');
title(layout, 'Nominal load and overload: power equality remains valid while operating point changes');
nexttile;
plot(nominal.time_s, nominal.electromagnetic_torque_Nm, 'LineWidth', 1.4); hold on;
plot(overload.time_s, overload.electromagnetic_torque_Nm, 'LineWidth', 1.4);
plot(regen.time_s, regen.electromagnetic_torque_Nm, 'LineWidth', 1.4);
ylabel('T_e / N m'); grid on; legend('nominal','overload','regenerative','Location','eastoutside');
nexttile;
plot(nominal.time_s, nominal.speed_rad_s, 'LineWidth', 1.4); hold on;
plot(overload.time_s, overload.speed_rad_s, 'LineWidth', 1.4);
plot(regen.time_s, regen.speed_rad_s, 'LineWidth', 1.4);
ylabel('\omega_m / rad/s'); grid on;
nexttile;
semilogy(nominal.time_s, abs(nominal.power_residual_W) + eps, 'LineWidth', 1.2); hold on;
semilogy(overload.time_s, abs(overload.power_residual_W) + eps, 'LineWidth', 1.2);
semilogy(regen.time_s, abs(regen.power_residual_W) + eps, 'LineWidth', 1.2);
ylabel('|residual| / W'); xlabel('time / s'); grid on;
exportgraphics(fig, fullfile(asset_dir, 'plecs_power_balance_scenarios.png'), 'Resolution', 180);
close(fig);

fprintf('Generated chapter 04 MATLAB post-processing. scenarios=%d pass=%d figures=2\n', ...
    height(summary), sum(strcmp(summary.result, 'PASS')));

clear; clc;

root_dir = fileparts(fileparts(mfilename('fullpath')));
data_dir = fullfile(root_dir, 'waveforms', '01-bldc-control-chain');
asset_dir = fullfile(root_dir, 'assets', '01-bldc-control-chain');
if ~exist(asset_dir, 'dir'); mkdir(asset_dir); end

nominal = readtable(fullfile(data_dir, 'plecs_nominal_load.csv'), ...
    'VariableNamingRule', 'preserve');
overload = readtable(fullfile(data_dir, 'plecs_overload.csv'), ...
    'VariableNamingRule', 'preserve');
summary = readtable(fullfile(data_dir, 'plecs_baseline_summary.csv'), ...
    'VariableNamingRule', 'preserve');

required = ["time_s", "ia_A", "ib_A", "ic_A", "ea_V", "eb_V", "ec_V", ...
    "speed_rpm", "electromagnetic_torque_Nm", ...
    "phase_cmd_a", "phase_cmd_b", "phase_cmd_c"];
require_columns(nominal, required, "nominal_load");
require_columns(overload, required, "overload");

if height(summary) ~= 2 || any(string(summary.result) ~= "PASS")
    error('第 01 章 PLECS 汇总结果不是 2/2 PASS，请先重新运行 PLECS 场景脚本。');
end

plot_load_comparison(nominal, overload, summary, asset_dir);
plot_commutation_zoom(nominal, asset_dir);

fprintf('Generated chapter 01 MATLAB post-processing. scenarios=2 pass=2 figures=2\n');

function require_columns(data, required, scenario_name)
missing = setdiff(required, string(data.Properties.VariableNames));
if ~isempty(missing)
    error('%s 缺少 PLECS 输出列: %s', scenario_name, strjoin(missing, ', '));
end
end

function plot_load_comparison(nominal, overload, summary, asset_dir)
colors = lines(3);
initial_speed_rpm = 300 * 60 / (2 * pi);
scenario_names = string(summary.scenario);
nominal_row = find(scenario_names == "nominal_load", 1);
overload_row = find(scenario_names == "overload", 1);
if isempty(nominal_row) || isempty(overload_row)
    error('第 01 章汇总数据缺少 nominal_load 或 overload 场景。');
end

torque_values = [
    summary.tail_torque_mean_Nm(nominal_row), summary.load_torque_Nm(nominal_row);
    summary.tail_torque_mean_Nm(overload_row), summary.load_torque_Nm(overload_row)
];

f = figure('Visible', 'off', 'Color', 'w', 'Position', [100, 100, 1200, 760]);

subplot(2, 1, 1);
h_nominal_speed = plot(nominal.time_s, nominal.speed_rpm, 'LineWidth', 1.8, ...
    'Color', colors(1, :)); hold on;
h_overload_speed = plot(overload.time_s, overload.speed_rpm, 'LineWidth', 1.8, ...
    'Color', colors(2, :));
h_initial_speed = yline(initial_speed_rpm, ':', 'LineWidth', 1.0, ...
    'Color', [0.35, 0.35, 0.35]);
grid on; ylabel('Speed / rpm');
title('PLECS experiment: torque balance determines the speed trend');
legend([h_nominal_speed, h_overload_speed, h_initial_speed], ...
    {'3 N m load', '6 N m load', 'Initial speed'}, 'Location', 'best');

subplot(2, 1, 2);
b = bar(torque_values, 'grouped');
b(1).FaceColor = colors(1, :);
b(2).FaceColor = [0.35, 0.35, 0.35];
grid on; ylim([0, 6.8]); ylabel('Torque / N m');
xticklabels({'3 N m scenario', '6 N m scenario'});
legend({'Tail mean electromagnetic torque', 'Load torque'}, 'Location', 'northwest');
for series_index = 1:numel(b)
    x_values = b(series_index).XEndPoints;
    y_values = b(series_index).YEndPoints;
    labels = compose('%.2f', b(series_index).YData);
    text(x_values, y_values, labels, 'HorizontalAlignment', 'center', ...
        'VerticalAlignment', 'bottom', 'FontSize', 10);
end
xlabel('Compare electromagnetic torque with load torque before judging speed');

exportgraphics(f, fullfile(asset_dir, 'plecs_load_comparison.png'), 'Resolution', 180);
close(f);
end

function plot_commutation_zoom(nominal, asset_dir)
window = nominal.time_s >= 0.24;
colors = lines(3);

f = figure('Visible', 'off', 'Color', 'w', 'Position', [100, 100, 1200, 900]);

subplot(3, 1, 1);
plot(nominal.time_s(window), nominal.ia_A(window), 'LineWidth', 1.1, 'Color', colors(1, :)); hold on;
plot(nominal.time_s(window), nominal.ib_A(window), 'LineWidth', 1.1, 'Color', colors(2, :));
plot(nominal.time_s(window), nominal.ic_A(window), 'LineWidth', 1.1, 'Color', colors(3, :));
grid on; ylabel('Phase current / A');
title('PLECS nominal-load commutation window');
legend('i_a', 'i_b', 'i_c', 'Location', 'best');

subplot(3, 1, 2);
plot(nominal.time_s(window), nominal.ea_V(window), 'LineWidth', 1.1, 'Color', colors(1, :)); hold on;
plot(nominal.time_s(window), nominal.eb_V(window), 'LineWidth', 1.1, 'Color', colors(2, :));
plot(nominal.time_s(window), nominal.ec_V(window), 'LineWidth', 1.1, 'Color', colors(3, :));
grid on; ylabel('Back EMF / V');
legend('e_a', 'e_b', 'e_c', 'Location', 'best');

subplot(3, 1, 3);
stairs(nominal.time_s(window), nominal.phase_cmd_a(window), 'LineWidth', 1.1, 'Color', colors(1, :)); hold on;
stairs(nominal.time_s(window), nominal.phase_cmd_b(window), 'LineWidth', 1.1, 'Color', colors(2, :));
stairs(nominal.time_s(window), nominal.phase_cmd_c(window), 'LineWidth', 1.1, 'Color', colors(3, :));
grid on; ylim([-1.2, 1.2]); yticks([-1, 0, 1]);
ylabel('Phase command'); xlabel('Time / s');
legend('A phase', 'B phase', 'C phase', 'Location', 'best');

exportgraphics(f, fullfile(asset_dir, 'plecs_commutation_zoom.png'), 'Resolution', 180);
close(f);
end

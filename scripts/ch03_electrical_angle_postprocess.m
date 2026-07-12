% 第 03 章：读取 PLECS 机械角，比较不同极对数下的电角度。

script_dir = fileparts(mfilename('fullpath'));
root_dir = fileparts(script_dir);
waveform_dir = fullfile(root_dir, 'waveforms', '03-electrical-angle');
asset_dir = fullfile(root_dir, 'assets', '03-electrical-angle');
if ~exist(asset_dir, 'dir'); mkdir(asset_dir); end

p1 = readtable(fullfile(waveform_dir, 'plecs_one_pole_pair.csv'), 'VariableNamingRule', 'preserve');
p4 = readtable(fullfile(waveform_dir, 'plecs_four_pole_pairs.csv'), 'VariableNamingRule', 'preserve');
summary = readtable(fullfile(waveform_dir, 'plecs_angle_summary.csv'), 'VariableNamingRule', 'preserve');
assert(all(strcmp(summary.result, 'PASS')), '第 03 章 PLECS 场景未全部通过。');

fig = figure('Color', 'w', 'Position', [100 80 1500 950]);
layout = tiledlayout(fig, 3, 1, 'TileSpacing', 'compact', 'Padding', 'compact');
title(layout, 'Same mechanical motion, different electrical-angle travel');

nexttile;
plot(p1.time_s * 1e3, p1.mechanical_angle_rad, 'LineWidth', 1.5); hold on;
plot(p4.time_s * 1e3, p4.mechanical_angle_rad, '--', 'LineWidth', 1.5);
yline(pi, ':'); yline(-pi, ':');
ylabel('wrapped \theta_m / rad'); grid on; legend('p=1', 'p=4', 'Location', 'eastoutside');

nexttile;
plot(p1.time_s * 1e3, p1.electrical_angle_rad, 'LineWidth', 1.5); hold on;
plot(p4.time_s * 1e3, p4.electrical_angle_rad, 'LineWidth', 1.5);
ylabel('\theta_e / rad'); grid on; legend('p=1', 'p=4', 'Location', 'eastoutside');

nexttile;
stairs(p1.time_s * 1e3, floor(p1.electrical_angle_wrapped_rad / (pi/3)), 'LineWidth', 1.4); hold on;
stairs(p4.time_s * 1e3, floor(p4.electrical_angle_wrapped_rad / (pi/3)), 'LineWidth', 1.4);
ylim([-0.3 5.3]); yticks(0:5); ylabel('60-degree sector'); xlabel('time / ms'); grid on;
legend('p=1', 'p=4', 'Location', 'eastoutside');

exportgraphics(fig, fullfile(asset_dir, 'mechanical_vs_electrical_angle.png'), 'Resolution', 180);
close(fig);
fprintf('Generated chapter 03 MATLAB post-processing. scenarios=%d pass=%d figures=1\n', ...
    height(summary), sum(strcmp(summary.result, 'PASS')));

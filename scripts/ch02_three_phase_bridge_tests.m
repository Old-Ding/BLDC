% 第 02 章：只读取 PLECS CSV，生成场景对比和六路门极审计图。

script_dir = fileparts(mfilename('fullpath'));
root_dir = fileparts(script_dir);
waveform_dir = fullfile(root_dir, 'waveforms', '02-three-phase-bridge');
asset_dir = fullfile(root_dir, 'assets', '02-three-phase-bridge');

if ~exist(asset_dir, 'dir')
    mkdir(asset_dir);
end

summary = readtable(fullfile(waveform_dir, 'plecs_bridge_summary.csv'), ...
    'VariableNamingRule', 'preserve');
representative = readtable(fullfile(waveform_dir, 'plecs_Apos_Bneg.csv'), ...
    'VariableNamingRule', 'preserve');
truth = readtable(fullfile(waveform_dir, 'gate_truth_table.csv'), ...
    'VariableNamingRule', 'preserve');

assert(height(summary) == 7, '第 02 章应包含 7 个 PLECS 场景。');
assert(all(strcmp(summary.result, 'PASS')), '第 02 章存在未通过的 PLECS 场景。');
assert(height(truth) == 64, '六路门极真值表必须覆盖 64 组组合。');

colors = [0.12 0.45 0.78; 0.85 0.25 0.20; 0.18 0.62 0.32];
time_ms = representative.time_s * 1e3;

fig = figure('Color', 'w', 'Position', [100 80 1500 1050]);
layout = tiledlayout(fig, 4, 1, 'TileSpacing', 'compact', 'Padding', 'compact');
title(layout, 'PLECS real bridge: A+ / B- / C floating', 'FontWeight', 'bold');

nexttile;
stairs(time_ms, representative.phase_cmd_a, 'Color', colors(1,:), 'LineWidth', 1.5); hold on;
stairs(time_ms, representative.phase_cmd_b, 'Color', colors(2,:), 'LineWidth', 1.5);
stairs(time_ms, representative.phase_cmd_c, 'Color', colors(3,:), 'LineWidth', 1.5);
yline(0, ':', 'Color', [0.35 0.35 0.35]);
ylim([-1.25 1.25]); ylabel('phase cmd'); grid on;
legend('A', 'B', 'C', 'Location', 'eastoutside');

nexttile;
plot(time_ms, representative.vab_V, 'Color', colors(1,:), 'LineWidth', 1.4); hold on;
plot(time_ms, representative.vbc_V, 'Color', colors(2,:), 'LineWidth', 1.4);
plot(time_ms, representative.vca_V, 'Color', colors(3,:), 'LineWidth', 1.4);
yline(0, ':', 'Color', [0.35 0.35 0.35]);
ylabel('line voltage / V'); grid on;
legend('v_{ab}', 'v_{bc}', 'v_{ca}', 'Location', 'eastoutside');

nexttile;
plot(time_ms, representative.ia_A, 'Color', colors(1,:), 'LineWidth', 1.4); hold on;
plot(time_ms, representative.ib_A, 'Color', colors(2,:), 'LineWidth', 1.4);
plot(time_ms, representative.ic_A, 'Color', colors(3,:), 'LineWidth', 1.4);
yline(0, ':', 'Color', [0.35 0.35 0.35]);
ylabel('phase current / A'); grid on;
legend('i_a', 'i_b', 'i_c', 'Location', 'eastoutside');

nexttile;
final_current = [summary.final_ia_A summary.final_ib_A summary.final_ic_A];
bar(final_current, 'grouped');
yline(0, ':', 'Color', [0.35 0.35 0.35]);
set(gca, 'XTick', 1:height(summary), 'XTickLabel', summary.scenario, ...
    'XTickLabelRotation', 20);
ylabel('current at 2 ms / A'); xlabel('PLECS scenario'); grid on;
legend('i_a', 'i_b', 'i_c', 'Location', 'eastoutside');

exportgraphics(fig, fullfile(asset_dir, 'plecs_bridge_paths.png'), 'Resolution', 180);
close(fig);

high_code = truth.AH * 4 + truth.BH * 2 + truth.CH;
low_code = truth.AL * 4 + truth.BL * 2 + truth.CL;
classification = zeros(8, 8);
for row = 1:height(truth)
    if truth.shoot_through(row) == 1
        value = 2;
    elseif truth.six_step_valid(row) == 1
        value = 1;
    else
        value = 0;
    end
    classification(low_code(row) + 1, high_code(row) + 1) = value;
end

fig = figure('Color', 'w', 'Position', [120 100 1200 900]);
imagesc(0:7, 0:7, classification);
axis image; set(gca, 'YDir', 'normal');
colormap([0.82 0.84 0.86; 0.18 0.62 0.32; 0.85 0.25 0.20]);
cb = colorbar('Ticks', [0 1 2], 'TickLabels', {'other safe', 'six-step', 'shoot-through'});
cb.Label.String = 'classification';
xlabel('high-side code AH BH CH'); ylabel('low-side code AL BL CL');
title('All 64 gate combinations: the same-leg conflict is the fault condition');
grid on;
exportgraphics(fig, fullfile(asset_dir, 'gate_truth_table_matrix.png'), 'Resolution', 180);
close(fig);

fprintf('Generated chapter 02 MATLAB post-processing. scenarios=%d pass=%d figures=2\n', ...
    height(summary), sum(strcmp(summary.result, 'PASS')));

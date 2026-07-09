% 第 02 篇：三相桥 6 个开关状态实验。
% 为什么用场景表而不是连续电机模型：本章只验证桥臂命令到相状态的映射，
% 电机电流、反电动势和机械响应会在后续 PLECS 完整模型里讨论。

clear; clc;

repoRoot = fileparts(fileparts(mfilename("fullpath")));
assetDir = fullfile(repoRoot, "assets", "02-three-phase-bridge");
waveformDir = fullfile(repoRoot, "waveforms", "02-three-phase-bridge");
reportDir = fullfile(repoRoot, "reports");
ensureDir(assetDir);
ensureDir(waveformDir);
ensureDir(reportDir);

dt = 50e-6;
samplesPerScenario = 80;
scenarioDuration = dt * samplesPerScenario;
stateCodeLow = -1;
stateCodeFloat = 0;
stateCodeHigh = 1;
stateCodeFault = 2;

scenarios = [
    scenario("normal_AH_BL", 1, 0, 0, 0, 1, 0, 1, -1, 0, 0, "A 相接正母线，B 相接负母线，C 相悬空")
    scenario("normal_BH_CL", 0, 1, 0, 0, 0, 1, 0, 1, -1, 0, "B 相接正母线，C 相接负母线，A 相悬空")
    scenario("normal_CH_AL", 0, 0, 1, 1, 0, 0, -1, 0, 1, 0, "C 相接正母线，A 相接负母线，B 相悬空")
    scenario("all_off", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "六个桥臂全关，三相都悬空")
    scenario("fault_AH_AL", 1, 0, 0, 1, 0, 0, 2, 0, 0, 1, "A 相上下桥同时导通，进入直通故障")
    scenario("fault_BH_BL", 0, 1, 0, 0, 1, 0, 0, 2, 0, 1, "B 相上下桥同时导通，进入直通故障")
];

scenarioCount = numel(scenarios);
totalSamples = scenarioCount * samplesPerScenario;

t = zeros(totalSamples, 1);
scenarioName = strings(totalSamples, 1);
scenarioIndex = zeros(totalSamples, 1);
ah = zeros(totalSamples, 1); bh = zeros(totalSamples, 1); ch = zeros(totalSamples, 1);
al = zeros(totalSamples, 1); bl = zeros(totalSamples, 1); cl = zeros(totalSamples, 1);
aState = zeros(totalSamples, 1); bState = zeros(totalSamples, 1); cState = zeros(totalSamples, 1);
shootThrough = zeros(totalSamples, 1);

summaryName = strings(scenarioCount, 1);
summaryGates = strings(scenarioCount, 1);
summaryExpected = strings(scenarioCount, 1);
summaryActual = strings(scenarioCount, 1);
summaryShootExpected = zeros(scenarioCount, 1);
summaryShootActual = zeros(scenarioCount, 1);
summaryResult = strings(scenarioCount, 1);
summaryNote = strings(scenarioCount, 1);

for i = 1:scenarioCount
    rowStart = (i - 1) * samplesPerScenario + 1;
    rowEnd = i * samplesPerScenario;
    idx = rowStart:rowEnd;
    s = scenarios(i);

    t(idx) = ((idx.' - 1) * dt);
    scenarioName(idx) = s.name;
    scenarioIndex(idx) = i;
    ah(idx) = s.ah; bh(idx) = s.bh; ch(idx) = s.ch;
    al(idx) = s.al; bl(idx) = s.bl; cl(idx) = s.cl;

    [stateA, stateB, stateC, shoot] = bridgeState(s.ah, s.bh, s.ch, s.al, s.bl, s.cl);
    aState(idx) = stateA;
    bState(idx) = stateB;
    cState(idx) = stateC;
    shootThrough(idx) = shoot;

    passed = stateA == s.expectedA && stateB == s.expectedB && ...
        stateC == s.expectedC && shoot == s.expectedShoot;

    summaryName(i) = s.name;
    summaryGates(i) = sprintf("AH=%d BH=%d CH=%d AL=%d BL=%d CL=%d", ...
        s.ah, s.bh, s.ch, s.al, s.bl, s.cl);
    summaryExpected(i) = sprintf("A=%s B=%s C=%s", ...
        stateLabel(s.expectedA), stateLabel(s.expectedB), stateLabel(s.expectedC));
    summaryActual(i) = sprintf("A=%s B=%s C=%s", ...
        stateLabel(stateA), stateLabel(stateB), stateLabel(stateC));
    summaryShootExpected(i) = s.expectedShoot;
    summaryShootActual(i) = shoot;
    summaryResult(i) = ternary(passed, "PASS", "FAIL");
    summaryNote(i) = s.note;
end

timeseries = table(t, scenarioIndex, scenarioName, ah, bh, ch, al, bl, cl, ...
    aState, bState, cState, shootThrough);
writetable(timeseries, fullfile(waveformDir, "bridge_state_timeseries.csv"));

summary = table(summaryName, summaryGates, summaryExpected, summaryActual, ...
    summaryShootExpected, summaryShootActual, summaryResult, summaryNote, ...
    'VariableNames', {'scenario', 'gates', 'expected_phase_state', 'actual_phase_state', ...
    'expected_shoot_through', 'actual_shoot_through', 'result', 'note'});
writetable(summary, fullfile(waveformDir, "bridge_state_summary.csv"));

fig1 = figure("Color", "w", "Position", [100, 100, 1150, 820]);
tiledlayout(3, 1, "TileSpacing", "compact", "Padding", "compact");

nexttile;
stairs(t, ah + 5, "LineWidth", 1.1); hold on;
stairs(t, bh + 4, "LineWidth", 1.1);
stairs(t, ch + 3, "LineWidth", 1.1);
stairs(t, al + 2, "LineWidth", 1.1);
stairs(t, bl + 1, "LineWidth", 1.1);
stairs(t, cl, "LineWidth", 1.1);
grid on;
ylim([-0.3, 6.4]);
yticks([0 1 2 3 4 5]);
yticklabels(["CL", "BL", "AL", "CH", "BH", "AH"]);
title("Three-phase bridge gate scenarios");
legend("AH", "BH", "CH", "AL", "BL", "CL", "Location", "eastoutside");
drawScenarioLabels(t, scenarioCount, samplesPerScenario, scenarioDuration, scenarios);

nexttile;
stairs(t, aState, "LineWidth", 1.3); hold on;
stairs(t, bState, "LineWidth", 1.3);
stairs(t, cState, "LineWidth", 1.3);
grid on;
ylim([-1.3, 2.3]);
yticks([stateCodeLow stateCodeFloat stateCodeHigh stateCodeFault]);
yticklabels(["LOW", "FLOAT", "HIGH", "FAULT"]);
ylabel("phase state");
legend("A", "B", "C", "Location", "eastoutside");

nexttile;
stairs(t, shootThrough, "LineWidth", 1.4);
grid on;
ylim([-0.1, 1.2]);
yticks([0 1]);
yticklabels(["normal", "shoot-through"]);
ylabel("fault flag");
xlabel("time / s");

exportgraphics(fig1, fullfile(assetDir, "bridge_state_scenarios.png"), "Resolution", 180);

faultRows = find(summaryName == "normal_AH_BL" | summaryName == "fault_AH_AL" | summaryName == "fault_BH_BL");
faultNames = summaryName(faultRows);
faultScenarios = scenarios(faultRows);
faultStateMatrix = [
    [faultScenarios.expectedA]
    [faultScenarios.expectedB]
    [faultScenarios.expectedC]
];
faultShoot = summaryShootActual(faultRows).';

fig2 = figure("Color", "w", "Position", [120, 120, 920, 520]);
tiledlayout(2, 1, "TileSpacing", "compact", "Padding", "compact");

nexttile;
imagesc(faultStateMatrix);
colormap(gca, [0.22 0.45 0.72; 0.86 0.86 0.86; 0.82 0.36 0.28; 0.55 0.25 0.65]);
clim([-1, 2]);
colorbar("Ticks", [-1, 0, 1, 2], "TickLabels", ["LOW", "FLOAT", "HIGH", "FAULT"]);
xticks(1:numel(faultNames));
xticklabels(faultNames);
yticks(1:3);
yticklabels(["A state", "B state", "C state"]);
set(gca, "TickLabelInterpreter", "none");
title("Phase state under normal and shoot-through commands");
for r = 1:size(faultStateMatrix, 1)
    for c = 1:size(faultStateMatrix, 2)
        text(c, r, stateLabel(faultStateMatrix(r, c)), ...
            "HorizontalAlignment", "center", "FontWeight", "bold", "Color", "k");
    end
end

nexttile;
bar(faultShoot, 0.55, "FaceColor", [0.82 0.36 0.28]);
grid on;
ylim([0, 1.2]);
yticks([0 1]);
yticklabels(["normal", "shoot"]);
xticks(1:numel(faultNames));
xticklabels(faultNames);
set(gca, "TickLabelInterpreter", "none");
ylabel("shoot-through");
for c = 1:numel(faultShoot)
    label = ternary(faultShoot(c) == 1, "shoot", "normal");
    text(c, min(faultShoot(c) + 0.08, 1.08), label, ...
        "HorizontalAlignment", "center", "FontWeight", "bold");
end

exportgraphics(fig2, fullfile(assetDir, "bridge_state_fault_matrix.png"), "Resolution", 180);
close(fig1);
close(fig2);

writeReport(fullfile(reportDir, "02-three-phase-bridge-test_report.md"), ...
    scenarios, summary, dt, samplesPerScenario, scenarioDuration);

if any(summaryResult ~= "PASS")
    error("Chapter 02 bridge-state scenario test failed. See bridge_state_summary.csv.");
end

fprintf("Generated chapter 02 three-phase bridge tests. scenarios=%d pass=%d figures=2\n", ...
    scenarioCount, sum(summaryResult == "PASS"));

function ensureDir(path)
    if ~exist(path, "dir")
        mkdir(path);
    end
end

function s = scenario(name, ah, bh, ch, al, bl, cl, expectedA, expectedB, expectedC, expectedShoot, note)
    s = struct("name", string(name), "ah", ah, "bh", bh, "ch", ch, ...
        "al", al, "bl", bl, "cl", cl, "expectedA", expectedA, ...
        "expectedB", expectedB, "expectedC", expectedC, ...
        "expectedShoot", expectedShoot, "note", string(note));
end

function [a, b, c, shoot] = bridgeState(ah, bh, ch, al, bl, cl)
    shoot = 0;
    [a, shoot] = halfBridgeState(ah, al, shoot);
    [b, shoot] = halfBridgeState(bh, bl, shoot);
    [c, shoot] = halfBridgeState(ch, cl, shoot);
end

function [state, shoot] = halfBridgeState(high, low, shoot)
    if high && low
        state = 2;
        shoot = 1;
    elseif high
        state = 1;
    elseif low
        state = -1;
    else
        state = 0;
    end
end

function label = stateLabel(code)
    switch code
        case -1
            label = "LOW";
        case 0
            label = "FLOAT";
        case 1
            label = "HIGH";
        case 2
            label = "FAULT";
        otherwise
            label = "UNKNOWN";
    end
end

function out = ternary(cond, whenTrue, whenFalse)
    if cond
        out = string(whenTrue);
    else
        out = string(whenFalse);
    end
end

function drawScenarioLabels(t, scenarioCount, samplesPerScenario, scenarioDuration, scenarios)
    y = 6.15;
    for i = 1:scenarioCount
        boundary = (i - 1) * scenarioDuration;
        xline(boundary, ":", "Color", [0.5 0.5 0.5], "HandleVisibility", "off");
        midIndex = (i - 1) * samplesPerScenario + round(samplesPerScenario / 2);
        text(t(midIndex), y, scenarios(i).name, "Rotation", 25, ...
            "HorizontalAlignment", "center", "Interpreter", "none", "FontSize", 8);
    end
end

function writeReport(reportPath, scenarios, summary, dt, samplesPerScenario, scenarioDuration)
    fid = fopen(reportPath, "w", "n", "UTF-8");
    cleanup = onCleanup(@() fclose(fid));

    fprintf(fid, "# 第 02 篇测试报告：三相桥状态模型\n\n");
    fprintf(fid, "生成时间：%s\n\n", string(datetime("now", "Format", "yyyy-MM-dd HH:mm:ss")));

    fprintf(fid, "## 参数摘要\n\n");
    fprintf(fid, "- 采样周期：%.0f us\n", dt * 1e6);
    fprintf(fid, "- 每个场景采样点：%d\n", samplesPerScenario);
    fprintf(fid, "- 单场景持续时间：%.3f ms\n", scenarioDuration * 1e3);
    fprintf(fid, "- 状态编码：HIGH=1，LOW=-1，FLOAT=0，FAULT=2\n");
    fprintf(fid, "- 源码参照：`learning_model/steps/step_01_three_phase_bridge/bridge_state.c`\n");
    fprintf(fid, "- 生成脚本：`scripts/ch02_three_phase_bridge_tests.m`\n\n");

    fprintf(fid, "## 测试结果\n\n");
    fprintf(fid, "| 场景 | Gates | 期望状态 | 实际状态 | 期望直通 | 实际直通 | 结果 | 说明 |\n");
    fprintf(fid, "|---|---|---|---|---:|---:|---|---|\n");
    for i = 1:height(summary)
        fprintf(fid, "| `%s` | %s | %s | %s | %d | %d | %s | %s |\n", ...
            summary.scenario(i), summary.gates(i), summary.expected_phase_state(i), ...
            summary.actual_phase_state(i), summary.expected_shoot_through(i), ...
            summary.actual_shoot_through(i), summary.result(i), summary.note(i));
    end

    fprintf(fid, "\n## 曲线文件\n\n");
    fprintf(fid, "| 文件 | 作用 |\n");
    fprintf(fid, "|---|---|\n");
    fprintf(fid, "| `assets/02-three-phase-bridge/bridge_state_scenarios.png` | 六个 gate、三相状态和直通标志的场景时序 |\n");
    fprintf(fid, "| `assets/02-three-phase-bridge/bridge_state_fault_matrix.png` | 正常导通与直通故障的状态矩阵对比 |\n");
    fprintf(fid, "| `waveforms/02-three-phase-bridge/bridge_state_timeseries.csv` | 图 1 背后的逐点数据 |\n");
    fprintf(fid, "| `waveforms/02-three-phase-bridge/bridge_state_summary.csv` | 场景级 PASS/FAIL 汇总 |\n\n");

    fprintf(fid, "## 边界说明\n\n");
    fprintf(fid, "本报告只验证 6 路桥臂命令到 A/B/C 相状态和直通标志的映射。");
    fprintf(fid, "它不验证死区时间、驱动芯片保护、电流变化、电机反电动势或机械负载响应。\n");
end

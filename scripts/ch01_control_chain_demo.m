% 第 01 篇：BLDC 控制链信号级仿真。
% 为什么本脚本不用完整电机方程：本章目标是看清 target、duty、PWM、gates、
% Hall 和 speed feedback 的数据流，不证明电机参数或硬件控制性能。

clear; clc;

repoRoot = fileparts(fileparts(mfilename("fullpath")));
assetDir = fullfile(repoRoot, "assets", "01-bldc-control-chain");
waveformDir = fullfile(repoRoot, "waveforms", "01-bldc-control-chain");
reportDir = fullfile(repoRoot, "reports");
if ~exist(assetDir, "dir")
    mkdir(assetDir);
end
if ~exist(waveformDir, "dir")
    mkdir(waveformDir);
end
if ~exist(reportDir, "dir")
    mkdir(reportDir);
end

dt = 1e-4;
tEnd = 0.45;
t = (0:dt:tEnd).';
n = numel(t);

polePairs = 4;
pwmFreq = 500;
targetRpm = zeros(n, 1);
targetRpm(t >= 0.025) = 1200;
loadRpmEquivalent = zeros(n, 1);
loadRpmEquivalent(t >= 0.28) = 260;

actualRpm = zeros(n, 1);
feedbackRpm = zeros(n, 1);
duty = zeros(n, 1);
carrier = zeros(n, 1);
pwmOn = zeros(n, 1);
electricalStep = zeros(n, 1);
hallState = zeros(n, 1);
ahBase = zeros(n, 1); bhBase = zeros(n, 1); chBase = zeros(n, 1);
alBase = zeros(n, 1); blBase = zeros(n, 1); clBase = zeros(n, 1);
ahPwm = zeros(n, 1); bhPwm = zeros(n, 1); chPwm = zeros(n, 1);
alPwm = zeros(n, 1); blPwm = zeros(n, 1); clPwm = zeros(n, 1);

electricalEdgeCount = 0;
lastEdgeTime = NaN;
lastStep = NaN;
mechanicalRev = 0;
integralView = 0;
feedbackHold = 0;
tau = 0.040;

for k = 1:n
    if k > 1
        % 为什么用一阶响应：只给总览章节制造可追踪现象，不引入真实电机参数辨识。
        motorNoLoadRpm = 2600 * duty(k - 1);
        speedTargetByDuty = max(0, motorNoLoadRpm - loadRpmEquivalent(k));
        actualRpm(k) = actualRpm(k - 1) + dt / tau * (speedTargetByDuty - actualRpm(k - 1));
        mechanicalRev = mechanicalRev + actualRpm(k) / 60 * dt;
    end

    rawStep = floor(mechanicalRev * polePairs * 6);
    stepNow = mod(rawStep, 6);
    electricalStep(k) = stepNow;

    if isnan(lastStep)
        lastStep = stepNow;
    elseif stepNow ~= lastStep
        electricalEdgeCount = electricalEdgeCount + 1;
        if ~isnan(lastEdgeTime)
            edgePeriod = t(k) - lastEdgeTime;
            if edgePeriod > 0
                feedbackHold = 60 / (edgePeriod * polePairs * 6);
            end
        end
        lastEdgeTime = t(k);
        lastStep = stepNow;
    end
    feedbackRpm(k) = feedbackHold;

    error = targetRpm(k) - feedbackRpm(k);
    integralView = min(max(integralView + error * dt, 0), 220);
    duty(k) = min(max(0.12 + 0.00030 * error + 0.0020 * integralView, 0), 0.82);

    carrier(k) = mod(t(k) * pwmFreq, 1);
    pwmOn(k) = carrier(k) < duty(k);

    [ahBase(k), bhBase(k), chBase(k), alBase(k), blBase(k), clBase(k)] = sixStepGates(stepNow);
    hallState(k) = hallForStep(stepNow);

    ahPwm(k) = ahBase(k) * pwmOn(k);
    bhPwm(k) = bhBase(k) * pwmOn(k);
    chPwm(k) = chBase(k) * pwmOn(k);
    alPwm(k) = alBase(k);
    blPwm(k) = blBase(k);
    clPwm(k) = clBase(k);
end

T = table(t, targetRpm, actualRpm, feedbackRpm, duty, carrier, pwmOn, ...
    electricalStep, hallState, ahBase, bhBase, chBase, alBase, blBase, clBase, ...
    ahPwm, bhPwm, chPwm, alPwm, blPwm, clPwm);
writetable(T, fullfile(waveformDir, "control_chain_demo.csv"));

summary = array2table([ ...
    targetRpm(end), actualRpm(end), feedbackRpm(end), max(duty), ...
    sum(abs(diff(electricalStep)) > 0), electricalEdgeCount], ...
    "VariableNames", ["target_rpm_final", "actual_rpm_final", "feedback_rpm_final", ...
    "duty_max", "step_change_count", "hall_edge_count"]);
writetable(summary, fullfile(waveformDir, "control_chain_summary.csv"));
writeReport(fullfile(reportDir, "01-bldc-control-chain-test_report.md"), ...
    targetRpm, actualRpm, feedbackRpm, duty, electricalStep, electricalEdgeCount, dt, tEnd, polePairs, pwmFreq);

fig1 = figure("Color", "w", "Position", [100, 100, 1100, 800]);
tiledlayout(4, 1, "TileSpacing", "compact", "Padding", "compact");

nexttile;
plot(t, targetRpm, "LineWidth", 1.4); hold on;
plot(t, actualRpm, "LineWidth", 1.4);
stairs(t, feedbackRpm, "LineWidth", 1.0);
grid on;
ylabel("rpm");
legend("target", "actual", "Hall feedback", "Location", "southeast");
title("BLDC control-chain signal demo");

nexttile;
plot(t, duty, "LineWidth", 1.4); hold on;
plot(t, loadRpmEquivalent / 1000, "--", "LineWidth", 1.0);
grid on;
ylabel("duty / load");
legend("duty", "load equivalent / 1000", "Location", "southeast");

nexttile;
stairs(t, electricalStep, "LineWidth", 1.2); hold on;
stairs(t, hallState, "LineWidth", 1.0);
grid on;
ylabel("step / Hall");
legend("electrical step", "Hall state", "Location", "southeast");

nexttile;
stairs(t, ahPwm, "LineWidth", 1.0); hold on;
stairs(t, bhPwm + 1.2, "LineWidth", 1.0);
stairs(t, chPwm + 2.4, "LineWidth", 1.0);
grid on;
ylabel("high gates");
xlabel("time / s");
legend("AH pwm", "BH pwm + 1.2", "CH pwm + 2.4", "Location", "southeast");

exportgraphics(fig1, fullfile(assetDir, "control_chain_waveforms.png"), "Resolution", 180);

zoomMask = t >= 0.105 & t <= 0.125;
fig2 = figure("Color", "w", "Position", [120, 120, 1100, 620]);
tiledlayout(3, 1, "TileSpacing", "compact", "Padding", "compact");

nexttile;
stairs(t(zoomMask), electricalStep(zoomMask), "LineWidth", 1.2); hold on;
stairs(t(zoomMask), hallState(zoomMask), "LineWidth", 1.0);
grid on;
ylabel("step / Hall");
legend("step", "Hall", "Location", "eastoutside");
title("Gate-level zoom: PWM changes energy, not commutation order");

nexttile;
stairs(t(zoomMask), ahBase(zoomMask), "LineWidth", 1.0); hold on;
stairs(t(zoomMask), ahPwm(zoomMask) + 1.2, "LineWidth", 1.0);
grid on;
ylabel("A high");
legend("AH base", "AH pwm + 1.2", "Location", "eastoutside");

nexttile;
stairs(t(zoomMask), ahPwm(zoomMask), "LineWidth", 1.0); hold on;
stairs(t(zoomMask), bhPwm(zoomMask) + 1.2, "LineWidth", 1.0);
stairs(t(zoomMask), chPwm(zoomMask) + 2.4, "LineWidth", 1.0);
stairs(t(zoomMask), alPwm(zoomMask) + 3.6, "LineWidth", 1.0);
stairs(t(zoomMask), blPwm(zoomMask) + 4.8, "LineWidth", 1.0);
stairs(t(zoomMask), clPwm(zoomMask) + 6.0, "LineWidth", 1.0);
grid on;
ylabel("gates");
xlabel("time / s");
legend("AH", "BH+1.2", "CH+2.4", "AL+3.6", "BL+4.8", "CL+6.0", "Location", "eastoutside");

exportgraphics(fig2, fullfile(assetDir, "control_chain_gate_zoom.png"), "Resolution", 180);

close(fig1);
close(fig2);

fprintf("Generated chapter 01 control-chain demo. final_actual_rpm=%.1f duty_max=%.3f hall_edges=%d\n", ...
    actualRpm(end), max(duty), electricalEdgeCount);

function [ah, bh, ch, al, bl, cl] = sixStepGates(step)
    ah = 0; bh = 0; ch = 0; al = 0; bl = 0; cl = 0;
    switch step
        case 0
            ah = 1; bl = 1;
        case 1
            ah = 1; cl = 1;
        case 2
            bh = 1; cl = 1;
        case 3
            bh = 1; al = 1;
        case 4
            ch = 1; al = 1;
        case 5
            ch = 1; bl = 1;
    end
end

function hall = hallForStep(step)
    hallSeq = [5, 1, 3, 2, 6, 4];
    hall = hallSeq(step + 1);
end

function writeReport(reportPath, targetRpm, actualRpm, feedbackRpm, duty, electricalStep, electricalEdgeCount, dt, tEnd, polePairs, pwmFreq)
    fid = fopen(reportPath, "w", "n", "UTF-8");
    cleanup = onCleanup(@() fclose(fid));

    fprintf(fid, "# 第 01 篇测试报告：BLDC 控制链信号级仿真\n\n");
    fprintf(fid, "生成时间：%s\n\n", string(datetime("now", "Format", "yyyy-MM-dd HH:mm:ss")));

    fprintf(fid, "## 参数摘要\n\n");
    fprintf(fid, "- 采样周期：%.0f us\n", dt * 1e6);
    fprintf(fid, "- 仿真时长：%.3f s\n", tEnd);
    fprintf(fid, "- 极对数：%d\n", polePairs);
    fprintf(fid, "- PWM 频率：%.0f Hz\n", pwmFreq);
    fprintf(fid, "- 脚本：`scripts/ch01_control_chain_demo.m`\n\n");

    fprintf(fid, "## 指标摘要\n\n");
    fprintf(fid, "| 指标 | 数值 |\n");
    fprintf(fid, "|---|---:|\n");
    fprintf(fid, "| 最终目标速度 / rpm | %.1f |\n", targetRpm(end));
    fprintf(fid, "| 最终实际速度 / rpm | %.1f |\n", actualRpm(end));
    fprintf(fid, "| 最终 Hall 反馈速度 / rpm | %.1f |\n", feedbackRpm(end));
    fprintf(fid, "| 最大 duty | %.3f |\n", max(duty));
    fprintf(fid, "| step 变化次数 | %d |\n", sum(abs(diff(electricalStep)) > 0));
    fprintf(fid, "| Hall 边沿计数 | %d |\n\n", electricalEdgeCount);

    fprintf(fid, "## 结果解释\n\n");
    fprintf(fid, "本报告是信号级教学仿真，用于确认 target、feedback、duty、step、Hall 和 PWM gates 的先后关系。");
    fprintf(fid, "它不评价电机参数、机械负载、驱动器死区或硬件控制性能。\n");
end

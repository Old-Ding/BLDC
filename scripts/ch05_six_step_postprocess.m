% 第 05 章：读取 PLECS 六步 CSV，展示命令、电流和转矩。
script_dir=fileparts(mfilename('fullpath')); root_dir=fileparts(script_dir);
wave_dir=fullfile(root_dir,'waveforms','05-six-step-sequence'); asset_dir=fullfile(root_dir,'assets','05-six-step-sequence');
if ~exist(asset_dir,'dir'); mkdir(asset_dir); end
forward=readtable(fullfile(wave_dir,'plecs_forward.csv'),'VariableNamingRule','preserve');
reverse=readtable(fullfile(wave_dir,'plecs_reverse.csv'),'VariableNamingRule','preserve');
summary=readtable(fullfile(wave_dir,'plecs_six_step_summary.csv'),'Delimiter',',','VariableNamingRule','preserve');
assert(all(strcmp(summary.result,'PASS')),'第 05 章场景未全部通过。');

fig=figure('Color','w','Position',[100 80 1500 1000]); layout=tiledlayout(fig,3,1,'TileSpacing','compact','Padding','compact');
title(layout,'PLECS forward six-step sequence drives the real bridge and BLDC windings'); t=forward.time_s*1e3;
nexttile; stairs(t,forward.cmd_a,'LineWidth',1.3); hold on; stairs(t,forward.cmd_b,'LineWidth',1.3); stairs(t,forward.cmd_c,'LineWidth',1.3);
ylim([-1.3 1.3]); ylabel('phase cmd'); grid on; legend('A','B','C','Location','eastoutside');
nexttile; plot(t,forward.ia_A,'LineWidth',1.2); hold on; plot(t,forward.ib_A,'LineWidth',1.2); plot(t,forward.ic_A,'LineWidth',1.2);
ylabel('phase current / A'); grid on; legend('i_a','i_b','i_c','Location','eastoutside');
nexttile; plot(t,forward.torque_Nm,'LineWidth',1.3); yline(0,':'); ylabel('T_e / N m'); xlabel('time / ms'); grid on;
exportgraphics(fig,fullfile(asset_dir,'plecs_forward_six_step.png'),'Resolution',180); close(fig);

fig=figure('Color','w','Position',[120 100 1500 800]); layout=tiledlayout(fig,2,1,'TileSpacing','compact','Padding','compact');
title(layout,'Reversing the table order reverses the rotating-state sequence');
nexttile; stairs(forward.time_s*1e3,forward.cmd_a,'LineWidth',1.2); hold on; stairs(forward.time_s*1e3,forward.cmd_b,'LineWidth',1.2); stairs(forward.time_s*1e3,forward.cmd_c,'LineWidth',1.2); ylabel('forward cmd'); grid on;
nexttile; stairs(reverse.time_s*1e3,reverse.cmd_a,'LineWidth',1.2); hold on; stairs(reverse.time_s*1e3,reverse.cmd_b,'LineWidth',1.2); stairs(reverse.time_s*1e3,reverse.cmd_c,'LineWidth',1.2); ylabel('reverse cmd'); xlabel('time / ms'); grid on;
exportgraphics(fig,fullfile(asset_dir,'forward_reverse_sequence.png'),'Resolution',180); close(fig);
fprintf('Generated chapter 05 MATLAB post-processing. scenarios=%d pass=%d figures=2\n',height(summary),sum(strcmp(summary.result,'PASS')));

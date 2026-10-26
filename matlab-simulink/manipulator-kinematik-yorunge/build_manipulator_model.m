% build_manipulator_model.m
% 6-DOF Manipülatör kinematik ve spline yörünge Simulink modelini kurar.
% Model: 'model/robot_yorunge_denetimi.slx'
% Hakan OĞUZ - Elektrik Elektronik Mühendisi

robot_parametreleri;

mdl = 'robot_yorunge_denetimi';
if bdIsLoaded(mdl)
    close_system(mdl, 0);
end

new_system(mdl);
set_param(mdl, 'Solver', 'ode4', 'FixedStep', num2str(traj.dt), 'StopTime', num2str(traj.t_total));

% 1. Zaman Kaynağı (Ramp / Clock)
add_block('simulink/Sources/Clock', [mdl '/Zaman_Sayaci']);
set_param([mdl '/Zaman_Sayaci'], 'Position', [40, 95, 70, 125]);

% 2. 5. Derece Spline Enterpolatörü Alt Sistemi (Quintic Interpolator)
sub_traj = [mdl '/Spline_Enterpolator'];
add_block('simulink/Ports & Subsystems/Subsystem', sub_traj);
set_param(sub_traj, 'Position', [140, 60, 290, 160]);
Simulink.SubSystem.deleteContents(sub_traj);

add_block('simulink/Ports & Subsystems/In1', [sub_traj '/t_in'], 'Position', [30, 65, 60, 80]);

% MATLAB Function Bloğu ile C2 Sürekli Yörünge Fonksiyonu
fun_blk = [sub_traj '/Quintic_Profile_Gen'];
add_block('simulink/User-Defined Functions/MATLAB Function', fun_blk);
set_param(fun_blk, 'Position', [120, 40, 260, 105]);

% Blok içi kodunu ayarla
config = Simulink.ConfigSet;
matlabFunctionBlock = find(slroot, '-isa', 'Stateflow.EMChart', 'Path', fun_blk);
matlabFunctionBlock.Script = sprintf([...
    'function [q, qd, qdd] = Quintic_Profile_Gen(t)\n', ...
    '%% 5. derece polinom enterpolasyonu\n', ...
    'tf = %.4f;\n', ...
    'q0 = [%.6f; %.6f; %.6f; %.6f; %.6f; %.6f];\n', ...
    'qf = [%.6f; %.6f; %.6f; %.6f; %.6f; %.6f];\n', ...
    'tau = min(max(t / tf, 0), 1);\n', ...
    's   = 10*tau^3 - 15*tau^4 + 6*tau^5;\n', ...
    'sd  = (30*tau^2 - 60*tau^3 + 30*tau^4) / tf;\n', ...
    'sdd = (60*tau - 180*tau^2 + 120*tau^3) / (tf^2);\n', ...
    'q   = q0 + (qf - q0) * s;\n', ...
    'qd  = (qf - q0) * sd;\n', ...
    'qdd = (qf - q0) * sdd;\n'], ...
    traj.t_total, ...
    traj.q_start(1), traj.q_start(2), traj.q_start(3), traj.q_start(4), traj.q_start(5), traj.q_start(6), ...
    traj.q_goal(1), traj.q_goal(2), traj.q_goal(3), traj.q_goal(4), traj.q_goal(5), traj.q_goal(6));

add_block('simulink/Ports & Subsystems/Out1', [sub_traj '/q_out'],   'Position', [330, 45, 360, 60]);
add_block('simulink/Ports & Subsystems/Out1', [sub_traj '/qd_out'],  'Position', [330, 75, 360, 90]);
add_block('simulink/Ports & Subsystems/Out1', [sub_traj '/qdd_out'], 'Position', [330, 105, 360, 120]);

add_line(sub_traj, 't_in/1', 'Quintic_Profile_Gen/1');
add_line(sub_traj, 'Quintic_Profile_Gen/1', 'q_out/1');
add_line(sub_traj, 'Quintic_Profile_Gen/2', 'qd_out/1');
add_line(sub_traj, 'Quintic_Profile_Gen/3', 'qdd_out/1');

% 3. İleri Kinematik ve Uç Nokta Konum İzleme Alt Sistemi
sub_fk = [mdl '/Manipulator_Kinematics'];
add_block('simulink/Ports & Subsystems/Subsystem', sub_fk);
set_param(sub_fk, 'Position', [360, 60, 520, 160]);
Simulink.SubSystem.deleteContents(sub_fk);

add_block('simulink/Ports & Subsystems/In1', [sub_fk '/q_act'], 'Position', [30, 55, 60, 70]);

fk_blk = [sub_fk '/DH_Forward_Kinematics'];
add_block('simulink/User-Defined Functions/MATLAB Function', fk_blk);
set_param(fk_blk, 'Position', [120, 40, 270, 90]);

fk_chart = find(slroot, '-isa', 'Stateflow.EMChart', 'Path', fk_blk);
fk_chart.Script = sprintf([...
    'function p_xyz = DH_Forward_Kinematics(q)\n', ...
    '%% DH parametreleri ile uç nokta kartezyen konumu hesabı\n', ...
    'a = [%.4f, %.4f, %.4f, %.4f, %.4f, %.4f];\n', ...
    'alpha = [%.4f, %.4f, %.4f, %.4f, %.4f, %.4f];\n', ...
    'd = [%.4f, %.4f, %.4f, %.4f, %.4f, %.4f];\n', ...
    'T = eye(4);\n', ...
    'for i = 1:6\n', ...
    '    ct = cos(q(i)); st = sin(q(i)); ca = cos(alpha(i)); sa = sin(alpha(i));\n', ...
    '    A = [ct, -st*ca,  st*sa, a(i)*ct;\n', ...
    '         st,  ct*ca, -ct*sa, a(i)*st;\n', ...
    '          0,     sa,     ca,    d(i);\n', ...
    '          0,      0,      0,      1];\n', ...
    '    T = T * A;\n', ...
    'end\n', ...
    'p_xyz = T(1:3, 4);\n'], ...
    robot.a(1), robot.a(2), robot.a(3), robot.a(4), robot.a(5), robot.a(6), ...
    robot.alpha(1), robot.alpha(2), robot.alpha(3), robot.alpha(4), robot.alpha(5), robot.alpha(6), ...
    robot.d(1), robot.d(2), robot.d(3), robot.d(4), robot.d(5), robot.d(6));

add_block('simulink/Ports & Subsystems/Out1', [sub_fk '/p_end_effector'], 'Position', [330, 55, 360, 70]);
add_line(sub_fk, 'q_act/1', 'DH_Forward_Kinematics/1');
add_line(sub_fk, 'DH_Forward_Kinematics/1', 'p_end_effector/1');

% 4. Ana Model Hatları
add_line(mdl, 'Zaman_Sayaci/1', 'Spline_Enterpolator/1');
add_line(mdl, 'Spline_Enterpolator/1', 'Manipulator_Kinematics/1');

% Loglama blokları (Workspace kayıtları)
add_block('simulink/Sinks/To Workspace', [mdl '/Log_q']);
set_param([mdl '/Log_q'], 'VariableName', 'sim_q', 'SaveFormat', 'Timeseries', 'Position', [360, 15, 430, 40]);
add_line(mdl, 'Spline_Enterpolator/1', 'Log_q/1');

add_block('simulink/Sinks/To Workspace', [mdl '/Log_qd']);
set_param([mdl '/Log_qd'], 'VariableName', 'sim_qd', 'SaveFormat', 'Timeseries', 'Position', [360, 180, 430, 205]);
add_line(mdl, 'Spline_Enterpolator/2', 'Log_qd/1');

add_block('simulink/Sinks/To Workspace', [mdl '/Log_p_xyz']);
set_param([mdl '/Log_p_xyz'], 'VariableName', 'sim_p', 'SaveFormat', 'Timeseries', 'Position', [590, 95, 660, 125]);
add_line(mdl, 'Manipulator_Kinematics/1', 'Log_p_xyz/1');

% Modeli kaydet
model_path = fullfile(fileparts(mfilename('fullpath')), 'model', 'robot_yorunge_denetimi.slx');
save_system(mdl, model_path);
close_system(mdl);

fprintf('Manipülatör Simulink modeli başarıyla oluşturuldu: %s\n', model_path);

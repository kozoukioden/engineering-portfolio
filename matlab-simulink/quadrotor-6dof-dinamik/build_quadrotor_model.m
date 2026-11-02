% build_quadrotor_model.m
% 6-DOF Quadrotor Uçuş Dinamiği ve Kaskad Kontrol Modeli
% Hakan OĞUZ - Elektrik Elektronik Mühendisi

clear; clc;
quadrotor_parametreleri;

mdl = 'quadrotor_6dof_flight';
if bdIsLoaded(mdl)
    close_system(mdl, 0);
end

new_system(mdl);
set_param(mdl, 'Solver', 'ode4', 'FixedStep', '1e-3', 'StopTime', '10.0');

% 1. Yükseklik Kanalı (Z)
add_block('simulink/Sources/Step', [mdl '/Step_Z']);
set_param([mdl '/Step_Z'], 'Time', '0.5', 'Before', '0', 'After', '5', 'Position', [40, 60, 80, 90]);

add_block('simulink/Math Operations/Sum', [mdl '/Sum_Z'], 'Inputs', '+-', 'Position', [120, 65, 140, 95]);
add_line(mdl, 'Step_Z/1', 'Sum_Z/1');

% Z PID Transfer Fonksiyonu: C_z(s) = Kp + Ki/s + Kd*s/(0.01*s + 1)
% Pay: (Kp*0.01 + Kd)*s^2 + (Kp + Ki*0.01)*s + Ki
% Payda: 0.01*s^2 + s
num_z = [ctrl.Kp_z*0.01 + ctrl.Kd_z, ctrl.Kp_z + ctrl.Ki_z*0.01, ctrl.Ki_z];
den_z = [0.01, 1, 0];
add_block('simulink/Continuous/Transfer Fcn', [mdl '/PID_TF_Z']);
set_param([mdl '/PID_TF_Z'], 'Numerator', mat2str(num_z), 'Denominator', mat2str(den_z), 'Position', [180, 60, 280, 100]);
add_line(mdl, 'Sum_Z/1', 'PID_TF_Z/1');

% Hover Thrust (m*g)
add_block('simulink/Sources/Constant', [mdl '/Hover_Thrust'], 'Value', num2str(quad.hover_thrust), 'Position', [220, 130, 260, 155]);
add_block('simulink/Math Operations/Sum', [mdl '/Sum_Thrust'], 'Inputs', '++', 'Position', [320, 75, 340, 105]);
add_line(mdl, 'PID_TF_Z/1', 'Sum_Thrust/1');
add_line(mdl, 'Hover_Thrust/1', 'Sum_Thrust/2');

% İtki Doyumu (0 - 36 N)
add_block('simulink/Discontinuities/Saturation', [mdl '/Sat_Thrust'], 'UpperLimit', num2str(quad.F_max_total), 'LowerLimit', '0', 'Position', [370, 75, 400, 105]);
add_line(mdl, 'Sum_Thrust/1', 'Sat_Thrust/1');

% Z Dinamiği: 1 / (m * s^2)
add_block('simulink/Math Operations/Sum', [mdl '/Sum_Net_Fz'], 'Inputs', '+-', 'Position', [430, 75, 450, 105]);
add_line(mdl, 'Sat_Thrust/1', 'Sum_Net_Fz/1');
add_line(mdl, 'Hover_Thrust/1', 'Sum_Net_Fz/2');

add_block('simulink/Continuous/Transfer Fcn', [mdl '/TF_Z_Plant']);
set_param([mdl '/TF_Z_Plant'], 'Numerator', '[1]', 'Denominator', sprintf('[%f 0 0]', quad.m), 'Position', [480, 70, 560, 110]);
add_line(mdl, 'Sum_Net_Fz/1', 'TF_Z_Plant/1');

% Geri besleme Z
add_line(mdl, 'TF_Z_Plant/1', 'Sum_Z/2');

% 2. Yatay Konum Kanalı (X)
add_block('simulink/Sources/Step', [mdl '/Step_X'], 'Time', '2.0', 'Before', '0', 'After', '3', 'Position', [40, 200, 80, 230]);
add_block('simulink/Math Operations/Sum', [mdl '/Sum_X'], 'Inputs', '+-', 'Position', [120, 205, 140, 235]);
add_line(mdl, 'Step_X/1', 'Sum_X/1');

% X PD Denetleyici: Kp + Kd*s / (0.02*s + 1) -> Hedef Pitch (theta_ref)
num_x = [ctrl.Kp_pos*0.02 + ctrl.Kd_pos, ctrl.Kp_pos];
den_x = [0.02, 1];
add_block('simulink/Continuous/Transfer Fcn', [mdl '/PD_TF_X']);
set_param([mdl '/PD_TF_X'], 'Numerator', mat2str(num_x), 'Denominator', mat2str(den_x), 'Position', [180, 200, 270, 240]);
add_line(mdl, 'Sum_X/1', 'PD_TF_X/1');

% Pitch Saturation (+-0.35 rad)
add_block('simulink/Discontinuities/Saturation', [mdl '/Sat_Pitch'], 'UpperLimit', '0.35', 'LowerLimit', '-0.35', 'Position', [300, 205, 330, 235]);
add_line(mdl, 'PD_TF_X/1', 'Sat_Pitch/1');

% Kapalı Çevrim Pitch Tutum Dinamiği: 100 / (s^2 + 16*s + 100)
add_block('simulink/Continuous/Transfer Fcn', [mdl '/TF_Pitch']);
set_param([mdl '/TF_Pitch'], 'Numerator', '[100]', 'Denominator', '[1 16 100]', 'Position', [360, 200, 440, 240]);
add_line(mdl, 'Sat_Pitch/1', 'TF_Pitch/1');

% İvme Ax = g * theta + F_wind/m
add_block('simulink/Math Operations/Gain', [mdl '/Gain_g'], 'Gain', num2str(quad.g), 'Position', [470, 205, 510, 235]);
add_line(mdl, 'TF_Pitch/1', 'Gain_g/1');

% Rüzgâr Bozucusu (t=5s de -0.8 m/s^2)
add_block('simulink/Sources/Step', [mdl '/Wind_Step'], 'Time', '5.0', 'Before', '0', 'After', '-0.8', 'Position', [460, 270, 500, 300]);

add_block('simulink/Math Operations/Sum', [mdl '/Sum_Ax'], 'Inputs', '++', 'Position', [540, 210, 560, 240]);
add_line(mdl, 'Gain_g/1', 'Sum_Ax/1');
add_line(mdl, 'Wind_Step/1', 'Sum_Ax/2');

% X Öteleme Dinamiği: 1 / s^2
add_block('simulink/Continuous/Transfer Fcn', [mdl '/TF_X_Plant']);
set_param([mdl '/TF_X_Plant'], 'Numerator', '[1]', 'Denominator', '[1 0 0]', 'Position', [590, 205, 660, 245]);
add_line(mdl, 'Sum_Ax/1', 'TF_X_Plant/1');

% Geri besleme X
add_line(mdl, 'TF_X_Plant/1', 'Sum_X/2');

% Loglama Blokları (To Workspace)
add_block('simulink/Sinks/To Workspace', [mdl '/Log_Z'], 'VariableName', 'sim_z', 'SaveFormat', 'Array', 'Position', [600, 80, 650, 100]);
add_line(mdl, 'TF_Z_Plant/1', 'Log_Z/1');

add_block('simulink/Sinks/To Workspace', [mdl '/Log_X'], 'VariableName', 'sim_x', 'SaveFormat', 'Array', 'Position', [700, 215, 750, 235]);
add_line(mdl, 'TF_X_Plant/1', 'Log_X/1');

add_block('simulink/Sinks/To Workspace', [mdl '/Log_Pitch'], 'VariableName', 'sim_pitch', 'SaveFormat', 'Array', 'Position', [480, 160, 530, 180]);
add_line(mdl, 'TF_Pitch/1', 'Log_Pitch/1');

add_block('simulink/Sinks/To Workspace', [mdl '/Log_Thrust'], 'VariableName', 'sim_thrust', 'SaveFormat', 'Array', 'Position', [430, 30, 480, 50]);
add_line(mdl, 'Sat_Thrust/1', 'Log_Thrust/1');

% Modeli Kaydet
model_dir = fullfile(fileparts(mfilename('fullpath')), 'model');
if ~exist(model_dir, 'dir'), mkdir(model_dir); end
model_path = fullfile(model_dir, 'quadrotor_6dof_flight.slx');
save_system(mdl, model_path);
fprintf('Simulink modeli kaydedildi: %s\n', model_path);

% Simülasyonu Koştur
fprintf('Simülasyon koşturuluyor...\n');
simOut = sim(mdl);
fprintf('Simülasyon tamamlandı.\n');

% CSV olarak dışa aktar
sim_t = simOut.tout;
sim_z = simOut.sim_z;
sim_x = simOut.sim_x;
sim_pitch = simOut.sim_pitch * (180/pi);
sim_thrust = simOut.sim_thrust;

T = table(sim_t, sim_x, sim_z, sim_pitch, sim_thrust, ...
          'VariableNames', {'time_s', 'pos_x', 'pos_z', 'pitch_deg', 'thrust_n'});
csv_path = fullfile(fileparts(mfilename('fullpath')), 'sim_results.csv');
writetable(T, csv_path);
fprintf('Simülasyon sonuçları CSV olarak kaydedildi: %s\n', csv_path);

close_system(mdl);

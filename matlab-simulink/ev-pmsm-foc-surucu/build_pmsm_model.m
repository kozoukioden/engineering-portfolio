% build_pmsm_model.m
% Temel Simulink bloklarıyla (lisans/toolbox bağımsız) EV PMSM FOC modeli kurar,
% koşturur ve sonuçları dışa aktarır.
% Hakan OĞUZ - Elektrik Elektronik Mühendisi

clear; clc;
pmsm_parametreleri;

mdl = 'ev_pmsm_foc_drive';
if bdIsLoaded(mdl)
    close_system(mdl, 0);
end

new_system(mdl);
set_param(mdl, 'Solver', 'ode4', 'FixedStep', '1e-4', 'StopTime', '0.25');

% 1. Hız Referansı (Step: 0.02s de 1500 rpm)
add_block('simulink/Sources/Step', [mdl '/Speed_Ref_Step']);
set_param([mdl '/Speed_Ref_Step'], 'Time', '0.02', 'Before', '0', 'After', '1500', 'Position', [40, 80, 80, 110]);

% rpm to rad/s
add_block('simulink/Math Operations/Gain', [mdl '/rpm2rad'], 'Gain', num2str(2*pi/60), 'Position', [120, 80, 160, 110]);
add_line(mdl, 'Speed_Ref_Step/1', 'rpm2rad/1');

% Hız Hatası: e_w = w_ref - w_fb
add_block('simulink/Math Operations/Sum', [mdl '/Sum_w'], 'Inputs', '+-', 'Position', [200, 85, 220, 115]);
add_line(mdl, 'rpm2rad/1', 'Sum_w/1');

% Hız PI Denetleyici (Temel bloklarla: Kp + Ki/s)
add_block('simulink/Math Operations/Gain', [mdl '/Kp_w'], 'Gain', num2str(foc.Kp_w), 'Position', [260, 65, 300, 95]);
add_block('simulink/Math Operations/Gain', [mdl '/Ki_w'], 'Gain', num2str(foc.Ki_w), 'Position', [260, 115, 300, 145]);
add_block('simulink/Continuous/Integrator', [mdl '/Int_w'], 'Position', [330, 120, 360, 140]);
add_block('simulink/Math Operations/Sum', [mdl '/Sum_PI_w'], 'Inputs', '++', 'Position', [390, 85, 410, 115]);

add_line(mdl, 'Sum_w/1', 'Kp_w/1');
add_line(mdl, 'Sum_w/1', 'Ki_w/1');
add_line(mdl, 'Ki_w/1', 'Int_w/1');
add_line(mdl, 'Kp_w/1', 'Sum_PI_w/1');
add_line(mdl, 'Int_w/1', 'Sum_PI_w/2');

% Doyurma (Saturasyon - Iq_max = 250 A)
add_block('simulink/Discontinuities/Saturation', [mdl '/Sat_Iq'], 'UpperLimit', '250', 'LowerLimit', '-250', 'Position', [440, 85, 470, 115]);
add_line(mdl, 'Sum_PI_w/1', 'Sat_Iq/1');

% Iq Akım Hatası: e_iq = Iq_ref - Iq_fb
add_block('simulink/Math Operations/Sum', [mdl '/Sum_Iq'], 'Inputs', '+-', 'Position', [510, 90, 530, 120]);
add_line(mdl, 'Sat_Iq/1', 'Sum_Iq/1');

% Iq PI Denetleyici -> Vq
add_block('simulink/Math Operations/Gain', [mdl '/Kp_iq'], 'Gain', num2str(foc.Kp_q), 'Position', [560, 75, 600, 105]);
add_block('simulink/Math Operations/Gain', [mdl '/Ki_iq'], 'Gain', num2str(foc.Ki_q), 'Position', [560, 125, 600, 155]);
add_block('simulink/Continuous/Integrator', [mdl '/Int_iq'], 'Position', [630, 130, 660, 150]);
add_block('simulink/Math Operations/Sum', [mdl '/Sum_PI_iq'], 'Inputs', '++', 'Position', [690, 95, 710, 125]);

add_line(mdl, 'Sum_Iq/1', 'Kp_iq/1');
add_line(mdl, 'Sum_Iq/1', 'Ki_iq/1');
add_line(mdl, 'Ki_iq/1', 'Int_iq/1');
add_line(mdl, 'Kp_iq/1', 'Sum_PI_iq/1');
add_line(mdl, 'Int_iq/1', 'Sum_PI_iq/2');

% PMSM q-ekseni transfer fonksiyonu: Iq = Vq / (Lq*s + Rs)
add_block('simulink/Continuous/Transfer Fcn', [mdl '/TF_Iq'], 'Numerator', '[1]', 'Denominator', sprintf('[%f %f]', motor.Lq, motor.Rs), 'Position', [750, 95, 830, 135]);
add_line(mdl, 'Sum_PI_iq/1', 'TF_Iq/1');

% Geri besleme: Iq
add_line(mdl, 'TF_Iq/1', 'Sum_Iq/2');

% Tork Sabiti: Te = 1.5 * p * psi_pm * Iq
kT = 1.5 * motor.p * motor.psi_pm;
add_block('simulink/Math Operations/Gain', [mdl '/Gain_kT'], 'Gain', num2str(kT), 'Position', [870, 100, 910, 130]);
add_line(mdl, 'TF_Iq/1', 'Gain_kT/1');

% Mekanik Dinamik: w = Te / (J*s + B)
add_block('simulink/Continuous/Transfer Fcn', [mdl '/TF_Mech'], 'Numerator', '[1]', 'Denominator', sprintf('[%f %f]', motor.J, motor.B), 'Position', [950, 95, 1030, 135]);
add_line(mdl, 'Gain_kT/1', 'TF_Mech/1');

% Mekanik Hız Geri Beslemesi
add_line(mdl, 'TF_Mech/1', 'Sum_w/2');

% Rad/s to RPM
add_block('simulink/Math Operations/Gain', [mdl '/rad2rpm'], 'Gain', num2str(60/(2*pi)), 'Position', [1060, 100, 1100, 130]);
add_line(mdl, 'TF_Mech/1', 'rad2rpm/1');

% Loglama Blokları (To Workspace)
add_block('simulink/Sinks/To Workspace', [mdl '/ToWks_w'], 'VariableName', 'sim_rpm', 'SaveFormat', 'Array', 'Position', [1140, 100, 1190, 130]);
add_line(mdl, 'rad2rpm/1', 'ToWks_w/1');

add_block('simulink/Sinks/To Workspace', [mdl '/ToWks_Te'], 'VariableName', 'sim_Te', 'SaveFormat', 'Array', 'Position', [950, 170, 1000, 200]);
add_line(mdl, 'Gain_kT/1', 'ToWks_Te/1');

add_block('simulink/Sinks/To Workspace', [mdl '/ToWks_Iq'], 'VariableName', 'sim_Iq', 'SaveFormat', 'Array', 'Position', [870, 40, 920, 70]);
add_line(mdl, 'TF_Iq/1', 'ToWks_Iq/1');

add_block('simulink/Sinks/To Workspace', [mdl '/ToWks_Time'], 'VariableName', 'sim_time', 'SaveFormat', 'Array', 'Position', [1140, 170, 1190, 200]);
add_block('simulink/Sources/Clock', [mdl '/Clock'], 'Position', [1060, 170, 1090, 190]);
add_line(mdl, 'Clock/1', 'ToWks_Time/1');

% Modeli Kaydet
model_dir = fullfile(fileparts(mfilename('fullpath')), 'model');
if ~exist(model_dir, 'dir')
    mkdir(model_dir);
end
model_path = fullfile(model_dir, 'ev_pmsm_foc_drive.slx');
save_system(mdl, model_path);
fprintf('Simulink modeli kaydedildi: %s\n', model_path);

% Simülasyonu Koştur
fprintf('Simulink simülasyonu başlatılıyor...\n');
simOut = sim(mdl);
fprintf('Simülasyon tamamlandı.\n');

% Sonuçları CSV olarak kaydet
sim_time = simOut.tout;
sim_rpm = simOut.sim_rpm;
sim_Te = simOut.sim_Te;
sim_Iq = simOut.sim_Iq;
T = table(sim_time, sim_rpm, sim_Te, sim_Iq, 'VariableNames', {'time_s', 'rpm', 'torque_nm', 'iq_a'});
csv_path = fullfile(fileparts(mfilename('fullpath')), 'sim_results.csv');
writetable(T, csv_path);
fprintf('Simülasyon sonuçları CSV olarak kaydedildi: %s\n', csv_path);

close_system(mdl);

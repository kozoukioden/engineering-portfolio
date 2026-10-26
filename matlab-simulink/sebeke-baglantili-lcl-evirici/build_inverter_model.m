% build_inverter_model.m
% Simulink modelini programatik olarak kurar ve 'model/inverter_lcl_control.slx' olarak kaydeder.
% Hakan OĞUZ - Elektrik Elektronik Mühendisi

parametreler;

mdl = 'inverter_lcl_control';
if bdIsLoaded(mdl)
    close_system(mdl, 0);
end

new_system(mdl);
set_param(mdl, 'Solver', 'ode4', 'FixedStep', num2str(Ts), 'StopTime', '0.15');

% 1. dq Referans Kaynakları (Adım yanıtı ve reaktif test)
% Id_ref: 0 -> 0.05 s arası 10 A, 0.05 s sonrası 20 A
add_block('simulink/Sources/Step', [mdl '/Id_Step']);
set_param([mdl '/Id_Step'], 'Time', '0.05', 'Before', '10', 'After', '20', 'Position', [40, 60, 80, 90]);

% Iq_ref: 0 -> 0.10 s arası 0 A, 0.10 s sonrası -8 A (kapasitif reaktif)
add_block('simulink/Sources/Step', [mdl '/Iq_Step']);
set_param([mdl '/Iq_Step'], 'Time', '0.10', 'Before', '0', 'After', '-8', 'Position', [40, 140, 80, 170]);

% 2. dq Akım Denetleyicisi Alt Sistemi (PI + Çapraz Kuplaj Açma)
sub_ctrl = [mdl '/Current_Controller_dq'];
add_block('simulink/Ports & Subsystems/Subsystem', sub_ctrl);
set_param(sub_ctrl, 'Position', [150, 45, 300, 185]);

% Alt sistem içi portları temizle/ayarla
Simulink.SubSystem.deleteContents(sub_ctrl);
add_block('simulink/Ports & Subsystems/In1', [sub_ctrl '/Id_ref'], 'Position', [30, 40, 60, 55]);
add_block('simulink/Ports & Subsystems/In1', [sub_ctrl '/Iq_ref'], 'Position', [30, 140, 60, 155]);
add_block('simulink/Ports & Subsystems/In1', [sub_ctrl '/Id_fb'],  'Position', [30, 80, 60, 95]);
add_block('simulink/Ports & Subsystems/In1', [sub_ctrl '/Iq_fb'],  'Position', [30, 180, 60, 195]);
add_block('simulink/Ports & Subsystems/In1', [sub_ctrl '/Vd_grid'], 'Position', [30, 230, 60, 245]);

% Hata hesapları
add_block('simulink/Math Operations/Sum', [sub_ctrl '/Sum_d'], 'Inputs', '+-', 'Position', [100, 40, 120, 65]);
add_block('simulink/Math Operations/Sum', [sub_ctrl '/Sum_q'], 'Inputs', '+-', 'Position', [100, 140, 120, 165]);
add_line(sub_ctrl, 'Id_ref/1', 'Sum_d/1');
add_line(sub_ctrl, 'Id_fb/1',  'Sum_d/2');
add_line(sub_ctrl, 'Iq_ref/1', 'Sum_q/1');
add_line(sub_ctrl, 'Iq_fb/1',  'Sum_q/2');

% PI d-ekseni
add_block('simulink/Continuous/PID Controller', [sub_ctrl '/PI_d']);
set_param([sub_ctrl '/PI_d'], 'P', num2str(Kp_i), 'I', num2str(Ki_i), 'Position', [160, 35, 210, 75]);
add_line(sub_ctrl, 'Sum_d/1', 'PI_d/1');

% PI q-ekseni
add_block('simulink/Continuous/PID Controller', [sub_ctrl '/PI_q']);
set_param([sub_ctrl '/PI_q'], 'P', num2str(Kp_i), 'I', num2str(Ki_i), 'Position', [160, 135, 210, 175]);
add_line(sub_ctrl, 'Sum_q/1', 'PI_q/1');

% Kuplaj açma kazancı w*(L1+L2)
wL = w_grid * (L1 + L2);
add_block('simulink/Math Operations/Gain', [sub_ctrl '/Gain_wL_d'], 'Gain', num2str(wL), 'Position', [160, 90, 210, 120]);
add_block('simulink/Math Operations/Gain', [sub_ctrl '/Gain_wL_q'], 'Gain', num2str(wL), 'Position', [160, 190, 210, 220]);
add_line(sub_ctrl, 'Iq_fb/1', 'Gain_wL_d/1');
add_line(sub_ctrl, 'Id_fb/1', 'Gain_wL_q/1');

% Voltaj toplamları
add_block('simulink/Math Operations/Sum', [sub_ctrl '/Sum_Vd'], 'Inputs', '++-', 'Position', [260, 45, 280, 85]);
add_line(sub_ctrl, 'PI_d/1', 'Sum_Vd/1');
add_line(sub_ctrl, 'Vd_grid/1', 'Sum_Vd/2');
add_line(sub_ctrl, 'Gain_wL_d/1', 'Sum_Vd/3');

add_block('simulink/Math Operations/Sum', [sub_ctrl '/Sum_Vq'], 'Inputs', '++', 'Position', [260, 145, 280, 185]);
add_line(sub_ctrl, 'PI_q/1', 'Sum_Vq/1');
add_line(sub_ctrl, 'Gain_wL_q/1', 'Sum_Vq/2');

% Çıkış portları
add_block('simulink/Ports & Subsystems/Out1', [sub_ctrl '/Vd_inv'], 'Position', [330, 55, 360, 70]);
add_block('simulink/Ports & Subsystems/Out1', [sub_ctrl '/Vq_inv'], 'Position', [330, 155, 360, 170]);
add_line(sub_ctrl, 'Sum_Vd/1', 'Vd_inv/1');
add_line(sub_ctrl, 'Sum_Vq/1', 'Vq_inv/1');

% 3. LCL Filtre ve Şebeke Dinamik Modeli Alt Sistemi
sub_plant = [mdl '/LCL_Plant_and_Grid'];
add_block('simulink/Ports & Subsystems/Subsystem', sub_plant);
set_param(sub_plant, 'Position', [370, 45, 520, 185]);
Simulink.SubSystem.deleteContents(sub_plant);

add_block('simulink/Ports & Subsystems/In1', [sub_plant '/Vd_inv'], 'Position', [30, 45, 60, 60]);
add_block('simulink/Ports & Subsystems/In1', [sub_plant '/Vq_inv'], 'Position', [30, 145, 60, 160]);

% Birinci dereceden eşdeğer şebeke enjeksiyon dinamiği: G(s) = 1 / ((L1+L2)*s + (R1+R2))
L_tot = L1 + L2;
R_tot = R1 + R2;

add_block('simulink/Continuous/Transfer Fcn', [sub_plant '/TF_d']);
set_param([sub_plant '/TF_d'], 'Numerator', '[1]', 'Denominator', sprintf('[%f %f]', L_tot, R_tot), 'Position', [120, 40, 200, 80]);
add_line(sub_plant, 'Vd_inv/1', 'TF_d/1');

add_block('simulink/Continuous/Transfer Fcn', [sub_plant '/TF_q']);
set_param([sub_plant '/TF_q'], 'Numerator', '[1]', 'Denominator', sprintf('[%f %f]', L_tot, R_tot), 'Position', [120, 140, 200, 180]);
add_line(sub_plant, 'Vq_inv/1', 'TF_q/1');

add_block('simulink/Ports & Subsystems/Out1', [sub_plant '/Id_meas'], 'Position', [250, 50, 280, 65]);
add_block('simulink/Ports & Subsystems/Out1', [sub_plant '/Iq_meas'], 'Position', [250, 150, 280, 165]);
add_line(sub_plant, 'TF_d/1', 'Id_meas/1');
add_line(sub_plant, 'TF_q/1', 'Iq_meas/1');

% 4. Sabit Şebeke Gerilimi Vd = V_pk
add_block('simulink/Sources/Constant', [mdl '/Vd_grid_const']);
set_param([mdl '/Vd_grid_const'], 'Value', num2str(V_pk), 'Position', [40, 210, 80, 235]);

% 5. Ana Blok Bağlantıları
add_line(mdl, 'Id_Step/1', 'Current_Controller_dq/1');
add_line(mdl, 'Iq_Step/1', 'Current_Controller_dq/2');
add_line(mdl, 'Vd_grid_const/1', 'Current_Controller_dq/5');

add_line(mdl, 'Current_Controller_dq/1', 'LCL_Plant_and_Grid/1');
add_line(mdl, 'Current_Controller_dq/2', 'LCL_Plant_and_Grid/2');

% Geri besleme hatları
add_line(mdl, 'LCL_Plant_and_Grid/1', 'Current_Controller_dq/3');
add_line(mdl, 'LCL_Plant_and_Grid/2', 'Current_Controller_dq/4');

% 6. Çıkış Loglama ve Scope
add_block('simulink/Sinks/To Workspace', [mdl '/To_Workspace_Id']);
set_param([mdl '/To_Workspace_Id'], 'VariableName', 'sim_Id', 'SaveFormat', 'Timeseries', 'Position', [590, 50, 660, 75]);
add_line(mdl, 'LCL_Plant_and_Grid/1', 'To_Workspace_Id/1');

add_block('simulink/Sinks/To Workspace', [mdl '/To_Workspace_Iq']);
set_param([mdl '/To_Workspace_Iq'], 'VariableName', 'sim_Iq', 'SaveFormat', 'Timeseries', 'Position', [590, 150, 660, 175]);
add_line(mdl, 'LCL_Plant_and_Grid/2', 'To_Workspace_Iq/1');

% Model dosyasını kaydet
model_path = fullfile(fileparts(mfilename('fullpath')), 'model', 'inverter_lcl_control.slx');
save_system(mdl, model_path);
close_system(mdl);

fprintf('Simulink modeli başarıyla oluşturuldu: %s\n', model_path);

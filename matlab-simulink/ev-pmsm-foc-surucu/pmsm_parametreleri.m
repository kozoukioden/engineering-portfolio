% Hakan OĞUZ - Elektrik Elektronik Mühendisi
clear; clc;


motor.P_nom      = 60e3;
motor.V_dc       = 400.0;
motor.p          = 4;
motor.Rs         = 0.035;
motor.Ld         = 0.28e-3;
motor.Lq         = 0.56e-3;
motor.psi_pm     = 0.095;
motor.J          = 0.045;
motor.B          = 0.005;


motor.n_base_rpm = 3500;
motor.n_max_rpm  = 7000;
motor.I_max      = 220.0;


wc_i = 2 * pi * 1000;
foc.Kp_d = wc_i * motor.Ld;
foc.Ki_d = wc_i * motor.Rs;
foc.Kp_q = wc_i * motor.Lq;
foc.Ki_q = wc_i * motor.Rs;


wc_w = 2 * pi * 30;
foc.Kp_w = (wc_w * motor.J) / (1.5 * motor.p * motor.psi_pm);
foc.Ki_w = foc.Kp_w * (wc_w / 5);

fprintf('EV PMSM parametreleri yüklendi: %d kW, Ld=%.2f mH, Lq=%.2f mH\n', ...
        int32(motor.P_nom/1e3), motor.Ld*1e3, motor.Lq*1e3);

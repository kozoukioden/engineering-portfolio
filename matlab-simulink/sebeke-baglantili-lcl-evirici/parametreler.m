% Hakan OĞUZ - Elektrik Elektronik Mühendisi
clear; clc;


P_nom   = 10e3;
V_grid  = 400;
V_ph    = V_grid / sqrt(3);
V_pk    = V_ph * sqrt(2);
f_grid  = 50;
w_grid  = 2 * pi * f_grid;
V_dc    = 700;
f_sw    = 10e3;
Ts      = 50e-6;


L1   = 3.2e-3;
R1   = 0.12;
C    = 9.4e-6;
L2   = 1.6e-3;
R2   = 0.08;
Rd   = 1.2;


f_res = (1 / (2*pi)) * sqrt((L1 + L2) / (L1 * L2 * C));
fprintf('LCL rezonans frekansı: %.1f Hz\n', f_res);


w_c = (2 * pi * f_sw) / 10;
Kp_i = w_c * L1;
Ki_i = w_c * R1;

fprintf('Akım PI kazançları -> Kp: %.3f, Ki: %.2f\n', Kp_i, Ki_i);

% Hakan OĞUZ - Elektrik Elektronik Mühendisi
clear; clc;

quad.m = 1.25;
quad.g = 9.81;
quad.L = 0.225;
quad.Ixx = 0.0145;
quad.Iyy = 0.0145;
quad.Izz = 0.0275;


quad.F_max_total = 36.0;
quad.hover_thrust = quad.m * quad.g;


ctrl.Kp_z = 25.0;
ctrl.Ki_z = 5.0;
ctrl.Kd_z = 12.0;


ctrl.Kp_pos = 0.35;
ctrl.Kd_pos = 0.45;


ctrl.Kp_att = 8.5;
ctrl.Kd_att = 1.8;


ctrl.Kp_yaw = 4.0;
ctrl.Kd_yaw = 1.2;

fprintf('Quadrotor parametreleri yüklendi: m=%.2f kg, Hover Thrust=%.2f N\n', quad.m, quad.hover_thrust);

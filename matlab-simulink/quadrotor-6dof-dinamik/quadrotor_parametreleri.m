% quadrotor_parametreleri.m
% 6-DOF Quadrotor Dinamik ve Kaskad Kontrolör Parametreleri
% Hakan OĞUZ - Elektrik Elektronik Mühendisi

clear; clc;

quad.m = 1.25;         % Toplam Kütle (kg)
quad.g = 9.81;         % Yerçekimi İvmesi (m/s^2)
quad.L = 0.225;        % Kol Uzunluğu (m)
quad.Ixx = 0.0145;     % kg*m^2
quad.Iyy = 0.0145;     % kg*m^2
quad.Izz = 0.0275;     % kg*m^2

% Motor Sınırları ve Doyum
quad.F_max_total = 36.0; % N (4 motor maksimum itkisi, T/W ~ 2.9)
quad.hover_thrust = quad.m * quad.g; % 12.26 N

% Kaskad PID Kazançları
% 1. Yükseklik (Z Ekseni) PID
ctrl.Kp_z = 25.0;
ctrl.Ki_z = 5.0;
ctrl.Kd_z = 12.0;

% 2. Yatay Konum (X ve Y Ekseni) -> Hedef Pitch ve Roll Açıları
ctrl.Kp_pos = 0.35;
ctrl.Kd_pos = 0.45;

% 3. Tutum / Açı (Roll ve Pitch) PD
ctrl.Kp_att = 8.5;
ctrl.Kd_att = 1.8;

% 4. Sapma (Yaw) PD
ctrl.Kp_yaw = 4.0;
ctrl.Kd_yaw = 1.2;

fprintf('Quadrotor parametreleri yüklendi: m=%.2f kg, Hover Thrust=%.2f N\n', quad.m, quad.hover_thrust);

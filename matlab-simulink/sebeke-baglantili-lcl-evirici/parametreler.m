% Parametreler ve çalısma noktası - 10 kW LCL filtreli üç faz şebeke eviricisi
% Hakan OĞUZ - Elektrik Elektronik Mühendisi

clear; clc;

% Şebeke ve evirici temel değerleri
P_nom   = 10e3;             % [W]
V_grid  = 400;              % [V] hat-hat RMS
V_ph    = V_grid / sqrt(3); % [V] faz-nötr RMS (~230.9 V)
V_pk    = V_ph * sqrt(2);   % [V] tepe değeri (~326.6 V)
f_grid  = 50;               % [Hz]
w_grid  = 2 * pi * f_grid;  % [rad/s]
V_dc    = 700;              % [V] DC bara
f_sw    = 10e3;             % [Hz] PWM anahtarlama frekansı
Ts      = 50e-6;            % [s] kontrol periyodu (20 kHz örnekleme / çift güncelleme)

% LCL filtre parametreleri
% f_res kriteri: 10*f_grid < f_res < 0.5*f_sw (500 Hz < f_res < 5000 Hz)
L1   = 3.2e-3;              % [H] evirici tarafı bobini
R1   = 0.12;                % [Ohm] iç direnç
C    = 9.4e-6;              % [F] yıldız bağlı filtre kondansatörü (Q_cap < %5 P_nom)
L2   = 1.6e-3;              % [H] şebeke tarafı bobini
R2   = 0.08;                % [Ohm] iç direnç
Rd   = 1.2;                 % [Ohm] kondansatör seri sönümleme direnci

% Rezonans hesabı
f_res = (1 / (2*pi)) * sqrt((L1 + L2) / (L1 * L2 * C));
fprintf('LCL rezonans frekansı: %.1f Hz\n', f_res);

% dq akım denetleyicisi tasarımı
% Modül optimum kriteri: açık çevrim kesim frekansı w_c ~= w_sw / 10
w_c = (2 * pi * f_sw) / 10;
Kp_i = w_c * L1;
Ki_i = w_c * R1;

fprintf('Akım PI kazançları -> Kp: %.3f, Ki: %.2f\n', Kp_i, Ki_i);

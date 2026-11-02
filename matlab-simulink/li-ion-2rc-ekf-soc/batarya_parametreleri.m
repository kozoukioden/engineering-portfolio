% batarya_parametreleri.m
% 18650 Li-ion NMC Hücresi (3.0 Ah, 3.7 V) 2RC Eşdeğer Devre Modeli
% Hakan OĞUZ - Elektrik Elektronik Mühendisi

clear; clc;

% Hücre temel değerleri
bat.C_nom_Ah = 3.0;                  % Nominal kapasite [Ah]
bat.Q_coulomb = bat.C_nom_Ah * 3600;  % [As] (10800 Coulomb)
bat.V_nom     = 3.7;                 % Nominal gerilim [V]
bat.V_max     = 4.2;                 % Şarj kesme gerilimi [V]
bat.V_min     = 3.0;                 % Deşarj kesme gerilimi [V]

% 2RC Model Parametreleri (25°C referans)
bat.R0  = 0.025;   % Ohmik iç direnç [Ohm]
bat.R1  = 0.018;   % 1. RC (hızlı elektrokimyasal polarizasyon) direnci [Ohm]
bat.C1  = 1200.0;  % 1. RC kapasitesi [F] (tau1 = R1*C1 = 21.6 s)
bat.R2  = 0.022;   % 2. RC (yavaş konsantrasyon polarizasyonu) direnci [Ohm]
bat.C2  = 4500.0;  % 2. RC kapasitesi [F] (tau2 = R2*C2 = 99.0 s)

% OCV-SOC Polinom Katsayıları (Li-ion NMC için tipik 5. derece eğri)
% OCV(SOC) = p5*z^5 + p4*z^4 + p3*z^3 + p2*z^2 + p1*z + p0
bat.ocv_poly = [-3.85, 11.2, -12.1, 6.35, 0.42, 3.15];

fprintf('Li-ion 2RC batarya parametreleri yüklendi: Q = %.1f Ah, R0 = %.3f Ohm\n', bat.C_nom_Ah, bat.R0);

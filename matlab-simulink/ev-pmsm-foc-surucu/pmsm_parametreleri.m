% pmsm_parametreleri.m
% Elektrikli Araç (EV) PMSM Çekiş Motoru ve FOC Denetleyici Parametreleri
% Hakan OĞUZ - Elektrik Elektronik Mühendisi

clear; clc;

% 60 kW EV PMSM Motor Temel Parametreleri
motor.P_nom      = 60e3;             % Nominal Güç [W]
motor.V_dc       = 400.0;            % EV Batarya DC Bara Gerilimi [V]
motor.p          = 4;                % Kutup çifti sayısı (8 kutuplu)
motor.Rs         = 0.035;            % Stator faz direnci [Ohm]
motor.Ld         = 0.28e-3;          % d-ekseni endüktansı [H]
motor.Lq         = 0.56e-3;          % q-ekseni endüktansı [H] (Çıkıntılı kutup / Saliency: Lq > Ld)
motor.psi_pm     = 0.095;            % Kalıcı mıknatıs akı bağı [Wb]
motor.J          = 0.045;            % Rotor eylemsizlik momenti [kg.m^2]
motor.B          = 0.005;            % Viskoz sürtünme katsayısı [N.m.s]

% Sürüş ve Hız Sınırları
motor.n_base_rpm = 3500;             % Temel hız (Nominal tork bölgesi sınırı) [d/d]
motor.n_max_rpm  = 7000;             % Maksimum alan zayıflatma hızı [d/d]
motor.I_max      = 220.0;            % Tepe faz akımı [A]

% dq Akım PI Kazançları (Modüler Optimum: Kesim frekansı = 1 kHz)
wc_i = 2 * pi * 1000;
foc.Kp_d = wc_i * motor.Ld;
foc.Ki_d = wc_i * motor.Rs;
foc.Kp_q = wc_i * motor.Lq;
foc.Ki_q = wc_i * motor.Rs;

% Hız PI Kazancı
wc_w = 2 * pi * 30; % Hız çevrimi kesim frekansı = 30 Hz
foc.Kp_w = (wc_w * motor.J) / (1.5 * motor.p * motor.psi_pm);
foc.Ki_w = foc.Kp_w * (wc_w / 5);

fprintf('EV PMSM parametreleri yüklendi: %d kW, Ld=%.2f mH, Lq=%.2f mH\n', ...
        int32(motor.P_nom/1e3), motor.Ld*1e3, motor.Lq*1e3);

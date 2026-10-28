% simule_et.m
% HPPC darbe akımı altında 2RC hücre simülasyonu ve EKF SOC kestirimi
% Hakan OĞUZ - Elektrik Elektronik Mühendisi

clear; clc; close all;
cd(fileparts(mfilename('fullpath')));

batarya_parametreleri;

% 1. Zaman ve Akım Profili
dt = 0.5;                % Örnekleme adımı [s]
t_end = 3600;            % 1 saatlik test
t = (0:dt:t_end)';
N = length(t);

% Akım Profili: Deşarj pozitif kabul edilir [A]
I_load = zeros(N, 1);
for k = 1:N
    tk = t(k);
    if (mod(tk, 600) >= 60 && mod(tk, 600) <= 180)
        I_load(k) = 3.0;  % 1C Deşarj (3 A)
    elseif (mod(tk, 600) >= 300 && mod(tk, 600) <= 360)
        I_load(k) = -1.5; % 0.5C Şarj / Rejenerasyon (-1.5 A)
    else
        I_load(k) = 0.0;  % Dinlenme
    end
end

% 2. Gerçek Hücre Dinamiği Simülasyonu
true_soc = zeros(N, 1);
true_v1  = zeros(N, 1);
true_v2  = zeros(N, 1);
true_vt  = zeros(N, 1);

true_soc(1) = 0.90; % %90 başlangıç SOC
true_v1(1)  = 0.0;
true_v2(1)  = 0.0;

exp1 = exp(-dt / (bat.R1 * bat.C1));
exp2 = exp(-dt / (bat.R2 * bat.C2));

for k = 1:N-1
    ik = I_load(k);
    true_soc(k+1) = true_soc(k) - (ik * dt) / bat.Q_coulomb;
    true_v1(k+1) = true_v1(k) * exp1 + bat.R1 * (1.0 - exp1) * ik;
    true_v2(k+1) = true_v2(k) * exp2 + bat.R2 * (1.0 - exp2) * ik;
    ocv_k = ocv_hesapla(true_soc(k), bat.ocv_poly);
    true_vt(k) = ocv_k - true_v1(k) - true_v2(k) - ik * bat.R0;
end
true_vt(N) = ocv_hesapla(true_soc(N), bat.ocv_poly) - true_v1(N) - true_v2(N) - I_load(N) * bat.R0;

% Gürültülü Gerilim Ölçümü
rng(42);
v_meas = true_vt + 0.005 * randn(N, 1);

% 3. Genişletilmiş Kalman Filtresi (EKF)
x_est = zeros(3, N);
x_est(:, 1) = [0.70; 0.0; 0.0]; % %70 yanlış başlangıç tahmini

P = diag([0.05, 0.001, 0.001]);
Q = diag([1e-6, 1e-5, 1e-5]);
R_cov = 0.005^2;

F = diag([1.0, exp1, exp2]);
B = [-dt / bat.Q_coulomb; bat.R1 * (1.0 - exp1); bat.R2 * (1.0 - exp2)];

for k = 1:N-1
    ik = I_load(k);
    
    x_prior = F * x_est(:, k) + B * ik;
    P_prior = F * P * F' + Q;
    
    [ocv_prior, d_ocv] = ocv_hesapla(x_prior(1), bat.ocv_poly);
    v_pred = ocv_prior - x_prior(2) - x_prior(3) - ik * bat.R0;
    
    C_k = [d_ocv, -1.0, -1.0];
    S_k = C_k * P_prior * C_k' + R_cov;
    K_gain = (P_prior * C_k') / S_k;
    
    y_residual = v_meas(k+1) - v_pred;
    x_est(:, k+1) = x_prior + K_gain * y_residual;
    P = (eye(3) - K_gain * C_k) * P_prior;
    x_est(1, k+1) = min(max(x_est(1, k+1), 0.0), 1.0);
end

soc_est = x_est(1, :)';
soc_error = abs(true_soc - soc_est) * 100.0;

fprintf('EKF Analizi Tamamlandı: Ortalama Mutlak Hata (MAE) = %%.2f, Son Hata = %%.2f\n', ...
        mean(soc_error(500:end)), soc_error(end));

% Çıktı verilerini CSV olarak kaydet (Python ile temiz çizim için)
T_data = table(t, I_load, true_vt, v_meas, true_soc, soc_est, soc_error);
writetable(T_data, 'sim_results.csv');
fprintf('Simülasyon sonuçları sim_results.csv olarak kaydedildi.\n');

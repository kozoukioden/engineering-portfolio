% ula_huzme_yonlendirme.m
% 8 Elemanlı ULA Dizi Faktörü, Dolph-Chebyshev ve MVDR Sıfır Atma Analizi
% Hakan OĞUZ - Elektrik Elektronik Mühendisi

clear; clc;

N = 8;             % Anten Eleman Sayısı
f0 = 2.45e9;       % Frekans (2.45 GHz)
c = 3e8;
lambda = c / f0;   % Dalga Boyu (12.24 cm)
d = lambda / 2;    % Elemanlar Arası Mesafe (d = lambda/2)
k = 2 * pi / lambda;

fprintf('====================================================\n');
fprintf('ULA Akıllı Anten Huzme Yönlendirme ve MVDR Analizi\n');
fprintf('====================================================\n');

% Açı Vektörü (-90 ile +90 derece arası)
theta_deg = linspace(-90, 90, 721);
theta_rad = deg2rad(theta_deg);

% Yönlendirme Vektörü Fonksiyonu: a(theta) = [1, e^(j*k*d*sin(theta)), ...]^T
steering_vec = @(th) exp(1j * k * d * (0:N-1)' * sin(th));

% Hedef ve Girişim Yönleri
theta_des = deg2rad(15.0);   % Hedef Kullanıcı: +15 derece
theta_jam1 = deg2rad(-35.0); % Girişim Kaynağı 1 (Jammer): -35 derece
theta_jam2 = deg2rad(45.0);  % Girişim Kaynağı 2 (Jammer): +45 derece

% 1. Tekdüze (Uniform) Dizi Ağırlığı
% w_uniform = a(theta_des) / N
w_uniform = steering_vec(theta_des) / N;

% 2. Dolph-Chebyshev Dizi Ağırlığı (SLL = -26 dB)
% Chebyshev penceresi ile yan kulakçık bastırma
R_sll_db = 26.0;
cheb_win = chebwin(N, R_sll_db);
w_cheb = (cheb_win / sum(cheb_win)) .* steering_vec(theta_des);

% 3. MVDR (Minimum Variance Distortionless Response / Capon) Huzme Oluşturucu
% Kovaryans Matrisi R_xx = R_interference + R_noise
INR1 = 10^(30.0 / 10); % 30 dB Girişim / Gürültü Oranı
INR2 = 10^(25.0 / 10); % 25 dB
a_j1 = steering_vec(theta_jam1);
a_j2 = steering_vec(theta_jam2);
a_des = steering_vec(theta_des);

sigma_n_sq = 1.0; % Gürültü gücü
R_interf = INR1 * (a_j1 * a_j1') + INR2 * (a_j2 * a_j2') + sigma_n_sq * eye(N);

% MVDR Optimal Ağırlığı: w_mvdr = (R^-1 * a_des) / (a_des^H * R^-1 * a_des)
R_inv = inv(R_interf);
w_mvdr = (R_inv * a_des) / (a_des' * R_inv * a_des);

% 4. Dizi Faktörlerinin Hesaplanması (Array Factor)
AF_uniform = zeros(size(theta_rad));
AF_cheb = zeros(size(theta_rad));
AF_mvdr = zeros(size(theta_rad));

for idx = 1:length(theta_rad)
    a_th = steering_vec(theta_rad(idx));
    AF_uniform(idx) = abs(w_uniform' * a_th);
    AF_cheb(idx)    = abs(w_cheb' * a_th);
    AF_mvdr(idx)    = abs(w_mvdr' * a_th);
end

% Normalize dB Dönüşümü
AF_uniform_db = 20 * log10(AF_uniform / max(AF_uniform));
AF_cheb_db    = 20 * log10(AF_cheb / max(AF_cheb));
AF_mvdr_db    = 20 * log10(AF_mvdr / max(AF_mvdr));

% Eşikleme (-60 dB taban sınırı)
AF_uniform_db = max(AF_uniform_db, -60.0);
AF_cheb_db    = max(AF_cheb_db, -60.0);
AF_mvdr_db    = max(AF_mvdr_db, -60.0);

% Girişim Yönlerindeki Zayıflatmalar
idx_j1 = find(theta_deg >= -35.0, 1);
idx_j2 = find(theta_deg >= 45.0, 1);
fprintf('Girişim 1 (-35°) MVDR Zayıflatması: %.1f dB (Uniform: %.1f dB)\n', ...
        AF_mvdr_db(idx_j1), AF_uniform_db(idx_j1));
fprintf('Girişim 2 (+45°) MVDR Zayıflatması: %.1f dB (Uniform: %.1f dB)\n', ...
        AF_mvdr_db(idx_j2), AF_uniform_db(idx_j2));
fprintf('====================================================\n');

% 5. Sonuçları CSV olarak Kaydet
base_dir = fileparts(mfilename('fullpath'));
T_patterns = table(theta_deg', AF_uniform_db', AF_cheb_db', AF_mvdr_db', ...
                   'VariableNames', {'theta_deg', 'AF_uniform_dB', 'AF_cheb_dB', 'AF_mvdr_dB'});
writetable(T_patterns, fullfile(base_dir, 'beamforming_patterns.csv'));
fprintf('Huzme desenleri CSV olarak kaydedildi.\n');

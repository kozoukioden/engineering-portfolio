% Hakan OĞUZ - Elektrik Elektronik Mühendisi
clear; clc;

N = 8;
f0 = 2.45e9;
c = 3e8;
lambda = c / f0;
d = lambda / 2;
k = 2 * pi / lambda;

fprintf('====================================================\n');
fprintf('ULA Akıllı Anten Huzme Yönlendirme ve MVDR Analizi\n');
fprintf('====================================================\n');


theta_deg = linspace(-90, 90, 721);
theta_rad = deg2rad(theta_deg);


steering_vec = @(th) exp(1j * k * d * (0:N-1)' * sin(th));


theta_des = deg2rad(15.0);
theta_jam1 = deg2rad(-35.0);
theta_jam2 = deg2rad(45.0);


w_uniform = steering_vec(theta_des) / N;


R_sll_db = 26.0;
cheb_win = chebwin(N, R_sll_db);
w_cheb = (cheb_win / sum(cheb_win)) .* steering_vec(theta_des);


INR1 = 10^(30.0 / 10);
INR2 = 10^(25.0 / 10);
a_j1 = steering_vec(theta_jam1);
a_j2 = steering_vec(theta_jam2);
a_des = steering_vec(theta_des);

sigma_n_sq = 1.0;
R_interf = INR1 * (a_j1 * a_j1') + INR2 * (a_j2 * a_j2') + sigma_n_sq * eye(N);


R_inv = inv(R_interf);
w_mvdr = (R_inv * a_des) / (a_des' * R_inv * a_des);


AF_uniform = zeros(size(theta_rad));
AF_cheb = zeros(size(theta_rad));
AF_mvdr = zeros(size(theta_rad));

for idx = 1:length(theta_rad)
    a_th = steering_vec(theta_rad(idx));
    AF_uniform(idx) = abs(w_uniform' * a_th);
    AF_cheb(idx)    = abs(w_cheb' * a_th);
    AF_mvdr(idx)    = abs(w_mvdr' * a_th);
end


AF_uniform_db = 20 * log10(AF_uniform / max(AF_uniform));
AF_cheb_db    = 20 * log10(AF_cheb / max(AF_cheb));
AF_mvdr_db    = 20 * log10(AF_mvdr / max(AF_mvdr));


AF_uniform_db = max(AF_uniform_db, -60.0);
AF_cheb_db    = max(AF_cheb_db, -60.0);
AF_mvdr_db    = max(AF_mvdr_db, -60.0);


idx_j1 = find(theta_deg >= -35.0, 1);
idx_j2 = find(theta_deg >= 45.0, 1);
fprintf('Girişim 1 (-35°) MVDR Zayıflatması: %.1f dB (Uniform: %.1f dB)\n', ...
        AF_mvdr_db(idx_j1), AF_uniform_db(idx_j1));
fprintf('Girişim 2 (+45°) MVDR Zayıflatması: %.1f dB (Uniform: %.1f dB)\n', ...
        AF_mvdr_db(idx_j2), AF_uniform_db(idx_j2));
fprintf('====================================================\n');


base_dir = fileparts(mfilename('fullpath'));
T_patterns = table(theta_deg', AF_uniform_db', AF_cheb_db', AF_mvdr_db', ...
                   'VariableNames', {'theta_deg', 'AF_uniform_dB', 'AF_cheb_dB', 'AF_mvdr_dB'});
writetable(T_patterns, fullfile(base_dir, 'beamforming_patterns.csv'));
fprintf('Huzme desenleri CSV olarak kaydedildi.\n');

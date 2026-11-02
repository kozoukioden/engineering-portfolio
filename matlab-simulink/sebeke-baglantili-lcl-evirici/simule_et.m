% simule_et.m
% Simulink modelini çalıştırır, sonuçları çeker ve grafikleri üretir.
% Hakan OĞUZ - Elektrik Elektronik Mühendisi

clear; clc; close all;

% Çalışma dizini
cd(fileparts(mfilename('fullpath')));

% Parametreleri yükle
parametreler;

% 1. LCL Filtre Bode Eğrisi (Rezonans Zirvesi ve Sönümleme İncelemesi)
% s-domeninde transfer fonksiyonları:
% I_grid(s) / V_inv(s)
f_vec = logspace(1, 4.5, 1000);
w_vec = 2 * pi * f_vec;
s = 1j * w_vec;

% Sönümsüz (Rd = 0)
Y_undamped = 1 ./ ( (L1*L2*C)*(s.^3) + (R1*L2 + R2*L1)*C*(s.^2) + (L1+L2)*s + (R1+R2) );

% Pasif seri sönümleme (Rd = 1.2 Ohm)
Y_damped   = (C*Rd*s + 1) ./ ( (L1*L2*C)*(s.^3) + (L1*L2 + C*Rd*(L1+L2))*(s.^2) + (L1+L2 + C*Rd*(R1+R2))*s + (R1+R2) );

mag_undamped = 20 * log10(abs(Y_undamped));
mag_damped   = 20 * log10(abs(Y_damped));
phase_damped = unwrap(angle(Y_damped)) * 180 / pi;

% Grafik 1: LCL Frekans Yanıtı
fig1 = figure('Name', 'LCL Filtre Frekans Cevabı', 'Position', [100, 100, 800, 600], 'Visible', 'off');

subplot(2, 1, 1);
semilogx(f_vec, mag_undamped, 'r--', 'LineWidth', 1.5, 'DisplayName', 'Sönümsüz'); hold on;
semilogx(f_vec, mag_damped, 'b-', 'LineWidth', 1.8, 'DisplayName', sprintf('Pasif Sönümlü (R_d = %.1f \\Omega)', Rd));
xline(f_res, 'k:', 'LineWidth', 1.4, 'DisplayName', sprintf('f_{res} = %.0f Hz', f_res));
xline(f_sw, 'm-.', 'LineWidth', 1.4, 'DisplayName', sprintf('f_{sw} = %.0f Hz', f_sw));
grid on;
ylabel('Genlik [dB]');
title('LCL Filtre Frekans Cevabı (Rezonans ve Pasif Sönümleme)');
legend('Location', 'southwest');

subplot(2, 1, 2);
semilogx(f_vec, phase_damped, 'b-', 'LineWidth', 1.8); hold on;
xline(f_res, 'k:', 'LineWidth', 1.4);
xline(f_sw, 'm-.', 'LineWidth', 1.4);
grid on;
xlabel('Frekans [Hz]');
ylabel('Faz [derece]');

saveas(fig1, fullfile('sekiller', 'bode_rezonans.png'));
close(fig1);

% 2. Simulink Modelini Çalıştır
fprintf('Simulink modeli (inverter_lcl_control.slx) koşturuluyor...\n');
sim_out = sim('model/inverter_lcl_control.slx');

t_out = sim_out.sim_Id.Time;
Id_out = sim_out.sim_Id.Data;
Iq_out = sim_out.sim_Iq.Data;

% Aktif ve reaktif güç: P = 1.5 * Vd * Id, Q = -1.5 * Vd * Iq
P_out = 1.5 * V_pk * Id_out;
Q_out = -1.5 * V_pk * Iq_out;

% Grafik 2: dq Akım ve Güç Basamak Yanıtı
fig2 = figure('Name', 'dq Akım ve Güç Yanıtı', 'Position', [100, 100, 850, 650], 'Visible', 'off');

subplot(2, 1, 1);
plot(t_out * 1e3, Id_out, 'b-', 'LineWidth', 1.8, 'DisplayName', 'i_d (Aktif Bileşen)'); hold on;
plot(t_out * 1e3, Iq_out, 'r-', 'LineWidth', 1.8, 'DisplayName', 'i_q (Reaktif Bileşen)');
grid on;
ylabel('Akım [A]');
title('Senkron dq Çerçevesinde Akım Basamak Yanıtı (Simulink)');
legend('Location', 'east');

subplot(2, 1, 2);
plot(t_out * 1e3, P_out / 1e3, 'b-', 'LineWidth', 1.8, 'DisplayName', 'Aktif Güç P [kW]'); hold on;
plot(t_out * 1e3, Q_out / 1e3, 'r-', 'LineWidth', 1.8, 'DisplayName', 'Reaktif Güç Q [kVAR]');
grid on;
xlabel('Zaman [ms]');
ylabel('Güç');
title('Şebekeye Aktarılan Anlık Güçler');
legend('Location', 'east');

saveas(fig2, fullfile('sekiller', 'dq_akim_guc.png'));
close(fig2);

% 3. Üç Faz Şebeke Akımları (Ters Park/Clarke ile)
theta_grid = mod(w_grid * t_out, 2*pi);

% Ters Park
I_alpha = cos(theta_grid) .* Id_out - sin(theta_grid) .* Iq_out;
I_beta  = sin(theta_grid) .* Id_out + cos(theta_grid) .* Iq_out;

% Ters Clarke
Ia = I_alpha;
Ib = -0.5 * I_alpha + (sqrt(3)/2) * I_beta;
Ic = -0.5 * I_alpha - (sqrt(3)/2) * I_beta;
Va = V_pk * cos(theta_grid);

% Grafik 3: Üç Faz Şebeke Akım ve Gerilim Dalga Biçimleri
fig3 = figure('Name', 'Şebeke Akım ve Gerilimleri', 'Position', [100, 100, 850, 600], 'Visible', 'off');

% Son 3 periyot incelemesi (90 - 150 ms)
idx = t_out >= 0.08 & t_out <= 0.14;
t_ms = t_out(idx) * 1e3;

subplot(2, 1, 1);
plot(t_ms, Va(idx) / 10, 'k--', 'LineWidth', 1.3, 'DisplayName', 'v_{a} / 10 [V]'); hold on;
plot(t_ms, Ia(idx), 'b-', 'LineWidth', 1.8, 'DisplayName', 'i_{a} [A]');
grid on;
ylabel('Genlik');
title('Faz A Gerilim ve Akım Faz Hizalaması (Birim Güç Faktörü -> Reaktif Enjeksiyon)');
legend('Location', 'northeast');

subplot(2, 1, 2);
plot(t_ms, Ia(idx), 'b-', 'LineWidth', 1.6, 'DisplayName', 'i_a'); hold on;
plot(t_ms, Ib(idx), 'g-', 'LineWidth', 1.6, 'DisplayName', 'i_b');
plot(t_ms, Ic(idx), 'r-', 'LineWidth', 1.6, 'DisplayName', 'i_c');
grid on;
xlabel('Zaman [ms]');
ylabel('Akım [A]');
title('Üç Faz Şebeke Enjeksiyon Akımları');
legend('Location', 'northeast');

saveas(fig3, fullfile('sekiller', 'sebeke_dalga_sekilleri.png'));
close(fig3);

fprintf('Tüm analizler ve Simulink simülasyonu başarıyla tamamlandı. Şekiller kaydedildi.\n');

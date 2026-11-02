% simule_ber_ve_link.m
% LoRa Benzeri CSS Modem BER-SNR ve Kentsel Link Bütçesi Simülasyonu
% Hakan OĞUZ - Elektrik Elektronik Mühendisi

clear; clc;
BW = 125e3; % 125 kHz
Fs = BW;    % Nyquist örnekleme

fprintf('LoRa CSS Modem Simülasyonu Başlatılıyor...\n');

% 1. SF=7 Modülasyon / Demodülasyon Temel Testi
SF = 7;
modem7 = lora_css_modem(SF, BW, Fs);
test_sym = 42;
tx_sig = modem7.modulate(test_sym);
rx_sym = modem7.demodulate(tx_sig);
fprintf('Temel Test: Gönderilen Sembol: %d, Alınan Sembol: %d -> %s\n', ...
        test_sym, rx_sym, string(test_sym == rx_sym));

% 2. BER vs SNR Monte Carlo Simülasyonu (SF=7)
snr_db_vec = -22:2:2;
n_packets = 200; % Her SNR için test sembol sayısı
ber_sf7 = zeros(size(snr_db_vec));

for s_idx = 1:length(snr_db_vec)
    snr_db = snr_db_vec(s_idx);
    snr_lin = 10^(snr_db / 10);
    err_bits = 0;
    total_bits = n_packets * SF;
    
    for p = 1:n_packets
        sym = randi([0, modem7.M - 1]);
        tx = modem7.modulate(sym);
        
        % AWGN Gürültü Ekleme
        sig_pow = mean(abs(tx).^2);
        noise_pow = sig_pow / snr_lin;
        noise = sqrt(noise_pow / 2) * (randn(size(tx)) + 1j * randn(size(tx)));
        rx = tx + noise;
        
        est_sym = modem7.demodulate(rx);
        
        % Bit Hata Hesabı (Sembol -> Bit)
        b_tx = bitget(sym, 1:SF);
        b_rx = bitget(est_sym, 1:SF);
        err_bits = err_bits + sum(b_tx ~= b_rx);
    end
    
    ber_sf7(s_idx) = err_bits / total_bits;
    fprintf('  SNR = %4.1f dB | BER = %.4e\n', snr_db, ber_sf7(s_idx));
end

% 3. LoRa Link Bütçesi ve Kentsel Kapsama Hesabı (SF7 - SF12)
sf_list = (7:12)';
snr_req_list = [-7.5; -10.0; -12.5; -15.0; -17.5; -20.0]; % dB gerekli SNR
P_tx = 14.0; % dBm (+14 dBm = 25 mW)
NF = 6.0;    % dB Alıcı Gürültü Katsayısı
kT = -174.0; % dBm/Hz termal gürültü yoğunluğu
N_floor = kT + 10 * log10(BW) + NF; % dBm gürültü tabanı (-117 dBm)

Sensitivity = N_floor + snr_req_list; % dBm Alıcı Hassasiyeti
Max_Path_Loss = P_tx - Sensitivity;    % dB İzin Verilen Maksimum Yol Kaybı

% Kentsel Okumura-Hata Modeli (f = 868 MHz, hb = 30m baz istasyonu, hm = 1.5m mobil anten)
% PL = 69.55 + 26.16*log10(f) - 13.82*log10(hb) - a(hm) + (44.9 - 6.55*log10(hb))*log10(d)
f_mhz = 868.0;
hb = 30.0;
hm = 1.5;
a_hm = (1.1 * log10(f_mhz) - 0.7) * hm - (1.56 * log10(f_mhz) - 0.8);
A = 69.55 + 26.16 * log10(f_mhz) - 13.82 * log10(hb) - a_hm;
B = 44.9 - 6.55 * log10(hb);

% d = 10^((Max_PL - A) / B) [km]
Max_Range_km = 10.^((Max_Path_Loss - A) / B);

fprintf('====================================================\n');
fprintf('LoRa Link Bütçesi ve Kapsama Sonuçları:\n');
for i = 1:length(sf_list)
    fprintf('  SF%2d | Hassasiyet: %6.1f dBm | Max PL: %5.1f dB | Menzil: %5.2f km\n', ...
            sf_list(i), Sensitivity(i), Max_Path_Loss(i), Max_Range_km(i));
end
fprintf('====================================================\n');

% 4. Sonuçları CSV olarak Kaydet
base_dir = fileparts(mfilename('fullpath'));

T_ber = table(snr_db_vec', ber_sf7', 'VariableNames', {'SNR_dB', 'BER_SF7'});
writetable(T_ber, fullfile(base_dir, 'ber_results.csv'));

T_link = table(sf_list, snr_req_list, Sensitivity, Max_Path_Loss, Max_Range_km, ...
               'VariableNames', {'SF', 'SNR_Req_dB', 'Sensitivity_dBm', 'Max_PL_dB', 'Range_km'});
writetable(T_link, fullfile(base_dir, 'link_budget.csv'));
fprintf('CSV verileri başarıyla kaydedildi.\n');

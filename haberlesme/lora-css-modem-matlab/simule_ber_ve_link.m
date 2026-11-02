% Hakan OĞUZ - Elektrik Elektronik Mühendisi
clear; clc;
BW = 125e3;
Fs = BW;

fprintf('LoRa CSS Modem Simülasyonu Başlatılıyor...\n');


SF = 7;
modem7 = lora_css_modem(SF, BW, Fs);
test_sym = 42;
tx_sig = modem7.modulate(test_sym);
rx_sym = modem7.demodulate(tx_sig);
fprintf('Temel Test: Gönderilen Sembol: %d, Alınan Sembol: %d -> %s\n', ...
        test_sym, rx_sym, string(test_sym == rx_sym));


snr_db_vec = -22:2:2;
n_packets = 200;
ber_sf7 = zeros(size(snr_db_vec));

for s_idx = 1:length(snr_db_vec)
    snr_db = snr_db_vec(s_idx);
    snr_lin = 10^(snr_db / 10);
    err_bits = 0;
    total_bits = n_packets * SF;

    for p = 1:n_packets
        sym = randi([0, modem7.M - 1]);
        tx = modem7.modulate(sym);


        sig_pow = mean(abs(tx).^2);
        noise_pow = sig_pow / snr_lin;
        noise = sqrt(noise_pow / 2) * (randn(size(tx)) + 1j * randn(size(tx)));
        rx = tx + noise;

        est_sym = modem7.demodulate(rx);


        b_tx = bitget(sym, 1:SF);
        b_rx = bitget(est_sym, 1:SF);
        err_bits = err_bits + sum(b_tx ~= b_rx);
    end

    ber_sf7(s_idx) = err_bits / total_bits;
    fprintf('  SNR = %4.1f dB | BER = %.4e\n', snr_db, ber_sf7(s_idx));
end


sf_list = (7:12)';
snr_req_list = [-7.5; -10.0; -12.5; -15.0; -17.5; -20.0];
P_tx = 14.0;
NF = 6.0;
kT = -174.0;
N_floor = kT + 10 * log10(BW) + NF;

Sensitivity = N_floor + snr_req_list;
Max_Path_Loss = P_tx - Sensitivity;


f_mhz = 868.0;
hb = 30.0;
hm = 1.5;
a_hm = (1.1 * log10(f_mhz) - 0.7) * hm - (1.56 * log10(f_mhz) - 0.8);
A = 69.55 + 26.16 * log10(f_mhz) - 13.82 * log10(hb) - a_hm;
B = 44.9 - 6.55 * log10(hb);


Max_Range_km = 10.^((Max_Path_Loss - A) / B);

fprintf('====================================================\n');
fprintf('LoRa Link Bütçesi ve Kapsama Sonuçları:\n');
for i = 1:length(sf_list)
    fprintf('  SF%2d | Hassasiyet: %6.1f dBm | Max PL: %5.1f dB | Menzil: %5.2f km\n', ...
            sf_list(i), Sensitivity(i), Max_Path_Loss(i), Max_Range_km(i));
end
fprintf('====================================================\n');


base_dir = fileparts(mfilename('fullpath'));

T_ber = table(snr_db_vec', ber_sf7', 'VariableNames', {'SNR_dB', 'BER_SF7'});
writetable(T_ber, fullfile(base_dir, 'ber_results.csv'));

T_link = table(sf_list, snr_req_list, Sensitivity, Max_Path_Loss, Max_Range_km, ...
               'VariableNames', {'SF', 'SNR_Req_dB', 'Sensitivity_dBm', 'Max_PL_dB', 'Range_km'});
writetable(T_link, fullfile(base_dir, 'link_budget.csv'));
fprintf('CSV verileri başarıyla kaydedildi.\n');

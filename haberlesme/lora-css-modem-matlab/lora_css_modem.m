% lora_css_modem.m
% Chirp Spread Spectrum (CSS) Modülatör ve Dechirp+FFT Demodülatör Fonksiyonları
% Hakan OĞUZ - Elektrik Elektronik Mühendisi

function modem = lora_css_modem(SF, BW, Fs)
    % SF: Spreading Factor (7..12)
    % BW: Bant Genişliği (örn: 125e3 Hz)
    % Fs: Örnekleme Frekansı (örn: 1e6 Hz veya BW katı)
    if nargin < 3, Fs = BW; end
    if nargin < 2, BW = 125e3; end
    if nargin < 1, SF = 7; end

    modem.SF = SF;
    modem.BW = BW;
    modem.Fs = Fs;
    modem.M = 2^SF;              % Sembol alfabesi büyüklüğü
    modem.Ts = modem.M / BW;     % Sembol süresi (s)
    modem.N = round(modem.Ts * Fs); % Sembol başına örnek sayısı
    
    t = (0:modem.N-1) / Fs;
    modem.t = t;
    
    % Temel Referans Up-Chirp (0 -> BW)
    % Anlık frekans f(t) = -BW/2 + (BW/Ts)*t
    % Faz phi(t) = 2*pi * integral(f(t) dt) = 2*pi * (-BW/2*t + 0.5*(BW/Ts)*t^2)
    mu = BW / modem.Ts; % Chirp hızı (Hz/s)
    phi_base = 2 * pi * (-BW/2 * t + 0.5 * mu * t.^2);
    modem.base_upchirp = exp(1j * phi_base);
    
    % Temel Referans Down-Chirp (Eşlenik dechirp işareti)
    modem.base_downchirp = conj(modem.base_upchirp);
    
    % Fonksiyon Tutucuları (Handles)
    modem.modulate = @(symbol) modulate_symbol(modem, symbol);
    modem.demodulate = @(signal) demodulate_symbol(modem, signal);
end

function tx_signal = modulate_symbol(modem, symbol)
    % symbol: 0 .. M-1 arası tamsayı
    symbol = mod(symbol, modem.M);
    
    % Sembol ötelemesi (Cyclic shift)
    % shift_samples = round(symbol / M * N)
    shift_samples = round(symbol * (modem.Fs / modem.BW));
    
    % Döngüsel kaydırılmış chirp üretimi
    tx_signal = circshift(modem.base_upchirp, shift_samples);
end

function est_symbol = demodulate_symbol(modem, rx_signal)
    % 1. Dechirp: Alınan işareti temel down-chirp ile çarp
    dechirped = rx_signal .* modem.base_downchirp;
    
    % 2. FFT: Ayrık Fourier Dönüşümü ile frekans tepesini bul
    % N-noktalı FFT
    fft_res = abs(fft(dechirped, modem.M));
    
    % 3. En büyük genliğe sahip frekans bin'ini seç
    [~, max_idx] = max(fft_res);
    est_symbol = max_idx - 1; % 0-tabanlı sembol
end

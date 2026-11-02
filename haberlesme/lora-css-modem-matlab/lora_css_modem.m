% Hakan OĞUZ - Elektrik Elektronik Mühendisi
function modem = lora_css_modem(SF, BW, Fs)


    if nargin < 3, Fs = BW; end
    if nargin < 2, BW = 125e3; end
    if nargin < 1, SF = 7; end

    modem.SF = SF;
    modem.BW = BW;
    modem.Fs = Fs;
    modem.M = 2^SF;
    modem.Ts = modem.M / BW;
    modem.N = round(modem.Ts * Fs);

    t = (0:modem.N-1) / Fs;
    modem.t = t;


    mu = BW / modem.Ts;
    phi_base = 2 * pi * (-BW/2 * t + 0.5 * mu * t.^2);
    modem.base_upchirp = exp(1j * phi_base);


    modem.base_downchirp = conj(modem.base_upchirp);


    modem.modulate = @(symbol) modulate_symbol(modem, symbol);
    modem.demodulate = @(signal) demodulate_symbol(modem, signal);
end

function tx_signal = modulate_symbol(modem, symbol)

    symbol = mod(symbol, modem.M);


    shift_samples = round(symbol * (modem.Fs / modem.BW));


    tx_signal = circshift(modem.base_upchirp, shift_samples);
end

function est_symbol = demodulate_symbol(modem, rx_signal)

    dechirped = rx_signal .* modem.base_downchirp;


    fft_res = abs(fft(dechirped, modem.M));


    [~, max_idx] = max(fft_res);
    est_symbol = max_idx - 1;
end

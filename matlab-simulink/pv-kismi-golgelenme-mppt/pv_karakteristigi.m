% pv_karakteristigi.m
% Kısmi Gölgelenme Durumunda 4 Seri Modüllü PV Dizisi Matematiksel Modeli
% Hakan OĞUZ - Elektrik Elektronik Mühendisi

function [V_vec, I_vec, P_vec] = pv_karakteristigi(G_vec, T_c)
    % G_vec: 4 modülün ışınımı [W/m^2], örn: [1000, 750, 450, 200]
    % T_c: Hücre sıcaklığı [C], varsayılan 25 C
    if nargin < 2, T_c = 25; end
    if nargin < 1, G_vec = [1000, 750, 450, 200]; end

    % Modül Parametreleri (Standart 60 hücreli mono-Si modül)
    % STC: G0 = 1000 W/m2, T0 = 25 C
    Isc_stc = 9.50;  % A
    Voc_stc = 37.5;  % V
    Vmp_stc = 30.5;  % V
    Imp_stc = 8.85;  % A
    Pmp_stc = 270;   % W

    q = 1.602e-19;
    k = 1.38e-23;
    T_k = 273.15 + T_c;
    Vt = k * T_k / q * 60; % 60 hücre termal voltajı ~ 1.55 V
    a = 1.3; % İdeallik faktörü

    num_modules = length(G_vec);
    
    % Akım vektörü: 0 A'den maksimum Isc'ye kadar
    max_Isc = max(G_vec) / 1000 * Isc_stc;
    I_vec = linspace(0, max_Isc * 0.999, 400);
    V_vec = zeros(size(I_vec));

    for i = 1:num_modules
        G_i = G_vec(i);
        Iph_i = (G_i / 1000) * Isc_stc;
        I0_i = 1e-9 * (T_k / 298.15)^3;
        
        % Modül gerilimi: V = a*Vt * ln((Iph - I)/I0 + 1)
        % Eğer I > Iph ise bypass diyotu iletime geçer (V_diode = -0.7 V)
        V_mod = zeros(size(I_vec));
        for idx = 1:length(I_vec)
            I = I_vec(idx);
            if I < Iph_i
                V_mod(idx) = a * Vt * log(max((Iph_i - I) / I0_i + 1, 1));
            else
                % Bypass diyotu iletimde
                V_mod(idx) = -0.7;
            end
        end
        V_vec = V_vec + V_mod;
    end

    % Negatif gerilimleri sıfırla
    valid_idx = V_vec >= 0;
    V_vec = V_vec(valid_idx);
    I_vec = I_vec(valid_idx);
    P_vec = V_vec .* I_vec;
end

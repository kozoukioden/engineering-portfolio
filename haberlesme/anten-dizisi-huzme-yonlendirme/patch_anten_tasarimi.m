% patch_anten_tasarimi.m
% 2.45 GHz ISM Bandı Dikdörtgen Mikroşerit Yama (Patch) Anten Analitik Tasarımı
% Hakan OĞUZ - Elektrik Elektronik Mühendisi

clear; clc;

% Tasarım Girdileri
f0 = 2.45e9;       % Rezonans Frekansı: 2.45 GHz
c = 3e8;           % Işık Hızı (m/s)
er = 4.4;          % FR4 Bağıl Dielektrik Sabiti
h = 1.6e-3;        % Substrat Kalınlığı (1.6 mm)
Z0 = 50.0;         % Karakteristik Besleme Empedansı (50 Ohm)

fprintf('====================================================\n');
fprintf('Mikroşerit Yama Anten Tasarım Hesapları (f0 = 2.45 GHz)\n');
fprintf('====================================================\n');

% 1. Yama Genişliği (W)
% W = (c / (2 * f0)) * sqrt(2 / (er + 1))
W = (c / (2 * f0)) * sqrt(2 / (er + 1));
fprintf('1. Yama Genişliği (W): %.2f mm\n', W * 1e3);

% 2. Efektif Dielektrik Sabiti (er_eff)
% er_eff = (er + 1)/2 + ((er - 1)/2) * (1 + 12*(h/W))^(-0.5)
er_eff = (er + 1) / 2 + ((er - 1) / 2) * (1 + 12 * (h / W))^(-0.5);
fprintf('2. Efektif Dielektrik Sabiti (er_eff): %.4f\n', er_eff);

% 3. Saçaklanma Uzunluk Farkı (dL)
% dL = 0.412 * h * ((er_eff + 0.3)*(W/h + 0.264)) / ((er_eff - 0.258)*(W/h + 0.8))
dL = 0.412 * h * ((er_eff + 0.3) * (W / h + 0.264)) / ((er_eff - 0.258) * (W / h + 0.8));
fprintf('3. Saçaklanma Boyu (dL): %.3f mm\n', dL * 1e3);

% 4. Efektif Uzunluk (L_eff) ve Gerçek Uzunluk (L)
% L_eff = c / (2 * f0 * sqrt(er_eff))
L_eff = c / (2 * f0 * sqrt(er_eff));
L = L_eff - 2 * dL;
fprintf('4. Efektif Uzunluk (L_eff): %.2f mm\n', L_eff * 1e3);
fprintf('5. Gerçek Yama Boyu (L):    %.2f mm\n', L * 1e3);

% 5. 50 Ohm Giriş Empedansı İçin Inset Besleme Derinliği (y0)
% Kenar Giriş Direnci: Rin ~= 90 * (er^2 / (er - 1)) * (L/W)^2
R_edge = 90 * (er^2 / (er - 1)) * (L / W)^2;
% R_in(y0) = R_edge * cos^2(pi * y0 / L) = 50 Ohm
y0 = (L / pi) * acos(sqrt(Z0 / R_edge));
fprintf('6. Kenar Giriş Direnci (R_edge): %.1f Ohm\n', R_edge);
fprintf('7. Inset Besleme Derinliği (y0): %.2f mm\n', y0 * 1e3);

% 6. Toprak Düzlemi Boyutları (Ground Plane)
Wg = W + 6 * h;
Lg = L + 6 * h;
fprintf('8. Toprak Düzlemi Boyutları: %.1f mm x %.1f mm\n', Wg * 1e3, Lg * 1e3);
fprintf('====================================================\n');

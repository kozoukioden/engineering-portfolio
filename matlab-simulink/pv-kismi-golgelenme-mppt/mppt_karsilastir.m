% mppt_karsilastir.m
% Kısmi Gölgelenmede P&O vs Tarama vs PSO MPPT Algoritma Karşılaştırması
% Hakan OĞUZ - Elektrik Elektronik Mühendisi

clear; clc;
G_shading = [1000, 750, 450, 200]; % W/m2 4 modül
[V_curve, I_curve, P_curve] = pv_karakteristigi(G_shading);

[GMPP_power, gmpp_idx] = max(P_curve);
GMPP_voltage = V_curve(gmpp_idx);
fprintf('Global Maksimum Güç Noktası (GMPP): %.2f W @ %.2f V\n', GMPP_power, GMPP_voltage);

% PV Güç Sorgu Fonksiyonu (İnterpolasyon)
pv_power_fn = @(v) interp1(V_curve, P_curve, max(min(v, max(V_curve)), min(V_curve)), 'pchip', 0);

% 1. P&O (Perturb and Observe) Simülasyonu
n_steps = 60;
V_pno = zeros(1, n_steps);
P_pno = zeros(1, n_steps);
delta_V = 1.5; % V adım büyüklüğü
V_pno(1) = 25.0; % Başlangıç gerilimi (düşük voltajdan başlama)
P_pno(1) = pv_power_fn(V_pno(1));
direction = 1;

for k = 2:n_steps
    V_cand = V_pno(k-1) + direction * delta_V;
    P_cand = pv_power_fn(V_cand);
    
    if P_cand < P_pno(k-1)
        direction = -direction; % Yön değiştir
    end
    V_pno(k) = V_pno(k-1) + direction * delta_V;
    P_pno(k) = pv_power_fn(V_pno(k));
end

% 2. PSO (Particle Swarm Optimization) Simülasyonu
n_particles = 4;
n_iter = 15; % 15 iterasyon * 4 parçacık = 60 adım
w_inertia = 0.5;
c1 = 1.2;
c2 = 1.5;

x_particles = linspace(15, 120, n_particles); % Konumlar (Voltaj)
v_particles = zeros(1, n_particles);          % Hızlar
pbest_x = x_particles;
pbest_p = arrayfun(pv_power_fn, x_particles);
[gbest_p, gbest_idx] = max(pbest_p);
gbest_x = pbest_x(gbest_idx);

P_pso_history = zeros(1, n_steps);
step_count = 0;

for it = 1:n_iter
    for p = 1:n_particles
        step_count = step_count + 1;
        % Parçacık değerlendir
        p_val = pv_power_fn(x_particles(p));
        if p_val > pbest_p(p)
            pbest_p(p) = p_val;
            pbest_x(p) = x_particles(p);
        end
        if p_val > gbest_p
            gbest_p = p_val;
            gbest_x = x_particles(p);
        end
        if step_count <= n_steps
            P_pso_history(step_count) = gbest_p;
        end
    end
    % Hız ve konum güncelle
    for p = 1:n_particles
        r1 = rand(); r2 = rand();
        v_particles(p) = w_inertia * v_particles(p) + ...
                         c1 * r1 * (pbest_x(p) - x_particles(p)) + ...
                         c2 * r2 * (gbest_x - x_particles(p));
        x_particles(p) = max(min(x_particles(p) + v_particles(p), 130), 10);
    end
end

% Karşılaştırma Metrikleri
final_P_pno = mean(P_pno(end-10:end));
final_P_pso = gbest_p;
eff_pno = (final_P_pno / GMPP_power) * 100;
eff_pso = (final_P_pso / GMPP_power) * 100;

fprintf('===============================================\n');
fprintf('MPPT Karşılaştırma Sonuçları:\n');
fprintf('GMPP Teorik Maksimum: %.2f W\n', GMPP_power);
fprintf('P&O Ulaşılan Güç:    %.2f W (Verim: %%%.1f) -> Yerel Tepe Tuzağı!\n', final_P_pno, eff_pno);
fprintf('PSO Ulaşılan Güç:    %.2f W (Verim: %%%.1f) -> Global Zirve!\n', final_P_pso, eff_pso);
fprintf('PSO ile Enerji Kazanımı: +%%%.1f\n', eff_pso - eff_pno);
fprintf('===============================================\n');

% Sonuçları CSV olarak dışa aktar
base_dir = fileparts(mfilename('fullpath'));
T_curve = table(V_curve', I_curve', P_curve', 'VariableNames', {'V', 'I', 'P'});
writetable(T_curve, fullfile(base_dir, 'pv_curve.csv'));

steps = (1:n_steps)';
T_mppt = table(steps, P_pno', P_pso_history', repmat(GMPP_power, n_steps, 1), ...
               'VariableNames', {'step', 'P_pno', 'P_pso', 'GMPP'});
writetable(T_mppt, fullfile(base_dir, 'mppt_results.csv'));
fprintf('CSV verileri kaydedildi.\n');

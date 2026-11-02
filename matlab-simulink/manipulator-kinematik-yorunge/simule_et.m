% simule_et.m
% 6-DOF Manipülatör Simulink modelini koşturur, kinematik ve tekillik analizini çıkartır.
% Hakan OĞUZ - Elektrik Elektronik Mühendisi

clear; clc; close all;

cd(fileparts(mfilename('fullpath')));

% Parametreleri yükle
robot_parametreleri;

% 1. Simulink Modelini Koştur
fprintf('Simulink modeli (robot_yorunge_denetimi.slx) koşturuluyor...\n');
sim_out = sim('model/robot_yorunge_denetimi.slx');

t_out  = sim_out.sim_q.Time;
q_out  = squeeze(sim_out.sim_q.Data);
qd_out = squeeze(sim_out.sim_qd.Data);
p_out  = squeeze(sim_out.sim_p.Data);

N_samples = length(t_out);

% 2. Geometrik Jakobiyen ve Yoshikawa Manipulability İndeksi Hesabı
manipulability = zeros(1, N_samples);

for k = 1:N_samples
    qk = q_out(:, k);
    
    % İleri kinematik ara çerçeveler
    T_curr = eye(4);
    z_axes = zeros(3, 6);
    p_origins = zeros(3, 7);
    
    for i = 1:6
        ct = cos(qk(i)); st = sin(qk(i)); ca = cos(robot.alpha(i)); sa = sin(robot.alpha(i));
        A = [ct, -st*ca,  st*sa, robot.a(i)*ct;
             st,  ct*ca, -ct*sa, robot.a(i)*st;
              0,     sa,     ca,    robot.d(i);
              0,      0,      0,             1];
        T_curr = T_curr * A;
        z_axes(:, i) = T_curr(1:3, 3);
        p_origins(:, i+1) = T_curr(1:3, 4);
    end
    
    p_ee = T_curr(1:3, 4);
    
    % Jakobiyen sütunları
    J = zeros(6, 6);
    for i = 1:6
        if i == 1
            z_prev = [0; 0; 1];
            p_prev = [0; 0; 0];
        else
            z_prev = z_axes(:, i-1);
            p_prev = p_origins(:, i);
        end
        J(:, i) = [cross(z_prev, (p_ee - p_prev)); z_prev];
    end
    
    % Yoshikawa indeksi: w = sqrt(det(J * J'))
    manipulability(k) = sqrt(max(0, det(J * J')));
end

fprintf('Simülasyon tamamlandı. Minimum Manipulability: %.4e\n', min(manipulability));

% 3. Grafik 1: 3B Manipülatör İskeleti ve Uç Nokta İlerlemesi
fig1 = figure('Name', '3B Manipülatör İskeleti ve Yörünge', 'Position', [100, 100, 800, 600], 'Visible', 'off');
hold on; grid on; axis equal;
view(40, 25);

% Başlangıç ve bitiş duruş iskeletleri
q_init = traj.q_start;
q_end  = traj.q_goal;

function pts = get_robot_points(q, rob)
    pts = zeros(3, 7);
    T = eye(4);
    for j = 1:6
        ct = cos(q(j)); st = sin(q(j)); ca = cos(rob.alpha(j)); sa = sin(rob.alpha(j));
        A = [ct, -st*ca, st*sa, rob.a(j)*ct; st, ct*ca, -ct*sa, rob.a(j)*st; 0, sa, ca, rob.d(j); 0, 0, 0, 1];
        T = T * A;
        pts(:, j+1) = T(1:3, 4);
    end
end

pts_start = get_robot_points(q_init, robot);
pts_end   = get_robot_points(q_end, robot);

plot3(pts_start(1,:), pts_start(2,:), pts_start(3,:), 'b--o', 'LineWidth', 1.5, 'DisplayName', 'Başlangıç Duruşu');
plot3(pts_end(1,:), pts_end(2,:), pts_end(3,:), 'g--s', 'LineWidth', 1.5, 'DisplayName', 'Hedef Duruşu');
plot3(p_out(1,:), p_out(2,:), p_out(3,:), 'r-', 'LineWidth', 2.2, 'DisplayName', 'Uç Nokta Yolu');
plot3(p_out(1,1), p_out(2,1), p_out(3,1), 'kp', 'MarkerSize', 11, 'MarkerFaceColor', 'y', 'DisplayName', 'Başlangıç');
plot3(p_out(1,end), p_out(2,end), p_out(3,end), 'rp', 'MarkerSize', 11, 'MarkerFaceColor', 'm', 'DisplayName', 'Hedef');

xlabel('X [m]'); ylabel('Y [m]'); zlabel('Z [m]');
title('6-DOF Manipülatör 3B Konfigürasyonu ve Yörünge');
legend('Location', 'northeast');

saveas(fig1, fullfile('sekiller', 'robot_3b_yorunge.png'));
close(fig1);

% 4. Grafik 2: Eklem Açıları ve Hızları (C2 Sürekli)
fig2 = figure('Name', 'Eklem Profilleri', 'Position', [100, 100, 850, 650], 'Visible', 'off');

subplot(2, 1, 1);
plot(t_out, rad2deg(q_out), 'LineWidth', 1.5);
grid on;
ylabel('Açı [derece]');
title('5. Derece Spline Eklem Profilleri (Simulink)');
legend('q_1', 'q_2', 'q_3', 'q_4', 'q_5', 'q_6', 'Location', 'eastoutside');

subplot(2, 1, 2);
plot(t_out, rad2deg(qd_out), 'LineWidth', 1.5);
grid on;
xlabel('Zaman [s]');
ylabel('Hız [deg/s]');
title('Eklem Hız Profilleri (Sıfır Başlangıç/Bitiş Hızı)');
legend('dq_1/dt', 'dq_2/dt', 'dq_3/dt', 'dq_4/dt', 'dq_5/dt', 'dq_6/dt', 'Location', 'eastoutside');

saveas(fig2, fullfile('sekiller', 'eklem_profilleri.png'));
close(fig2);

% 5. Grafik 3: Kartezyen İlerleme ve Yoshikawa İndeksi
fig3 = figure('Name', 'Kartezyen ve Manipulability', 'Position', [100, 100, 850, 500], 'Visible', 'off');

subplot(2, 1, 1);
plot(t_out, p_out(1,:), 'r-', 'LineWidth', 1.6, 'DisplayName', 'X'); hold on;
plot(t_out, p_out(2,:), 'g-', 'LineWidth', 1.6, 'DisplayName', 'Y');
plot(t_out, p_out(3,:), 'b-', 'LineWidth', 1.6, 'DisplayName', 'Z');
grid on;
ylabel('Konum [m]');
title('Uç Nokta Kartezyen Koordinatları');
legend('Location', 'best');

subplot(2, 1, 2);
plot(t_out, manipulability, 'm-', 'LineWidth', 1.8);
grid on;
xlabel('Zaman [s]');
ylabel('w [-]');
title('Yoshikawa Manipulability İndeksi w = \surd(det(J J^T))');

saveas(fig3, fullfile('sekiller', 'kartezyen_tekillik.png'));
close(fig3);

fprintf('Manipülatör simülasyon grafikleri sekiller/ dizinine kaydedildi.\n');

% Hakan OĞUZ - Elektrik Elektronik Mühendisi
clear; clc;


robot.a     = [0,      0.4318, -0.0203, 0,      0,      0     ];
robot.alpha = [pi/2,   0,      -pi/2,   pi/2,  -pi/2,   0     ];
robot.d     = [0.6720, 0,       0.1500, 0.4318, 0,      0.0565];


robot.q_min = deg2rad([-160, -225, -45, -110, -100, -266]);
robot.q_max = deg2rad([ 160,   45, 225,  170,  100,  266]);


traj.t_total = 3.0;
traj.dt      = 0.01;
traj.t       = 0:traj.dt:traj.t_total;


traj.q_start = [0; -pi/4; pi/3; 0; pi/6; 0];
traj.q_goal  = [pi/3; -pi/6; pi/4; pi/4; -pi/4; pi/2];

fprintf('6-DOF manipülatör parametreleri yüklendi. Yörünge süresi: %.1f s\n', traj.t_total);

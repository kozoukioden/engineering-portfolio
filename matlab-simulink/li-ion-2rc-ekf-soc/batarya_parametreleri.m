% Hakan OĞUZ - Elektrik Elektronik Mühendisi
clear; clc;


bat.C_nom_Ah = 3.0;
bat.Q_coulomb = bat.C_nom_Ah * 3600;
bat.V_nom     = 3.7;
bat.V_max     = 4.2;
bat.V_min     = 3.0;


bat.R0  = 0.025;
bat.R1  = 0.018;
bat.C1  = 1200.0;
bat.R2  = 0.022;
bat.C2  = 4500.0;


bat.ocv_poly = [-3.85, 11.2, -12.1, 6.35, 0.42, 3.15];

fprintf('Li-ion 2RC batarya parametreleri yüklendi: Q = %.1f Ah, R0 = %.3f Ohm\n', bat.C_nom_Ah, bat.R0);

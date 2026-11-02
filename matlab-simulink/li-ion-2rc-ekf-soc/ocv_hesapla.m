% ocv_hesapla.m
% SOC değerine bağlı Açık Devre Gerilimi (OCV) ve türevi (dOCV/dSOC)
% Hakan OĞUZ - Elektrik Elektronik Mühendisi

function [ocv, d_ocv] = ocv_hesapla(soc, p)
    % soc: 0.0 ... 1.0
    soc = min(max(soc, 0.0), 1.0);
    
    % OCV = p(1)*s^5 + p(2)*s^4 + p(3)*s^3 + p(4)*s^2 + p(5)*s + p(6)
    ocv = polyval(p, soc);
    
    % Türev: d_ocv = 5*p(1)*s^4 + 4*p(2)*s^3 + 3*p(3)*s^2 + 2*p(4)*s + p(5)
    p_der = polyder(p);
    d_ocv = polyval(p_der, soc);
end

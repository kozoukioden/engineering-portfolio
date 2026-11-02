% Hakan OĞUZ - Elektrik Elektronik Mühendisi
function [ocv, d_ocv] = ocv_hesapla(soc, p)

    soc = min(max(soc, 0.0), 1.0);


    ocv = polyval(p, soc);


    p_der = polyder(p);
    d_ocv = polyval(p_der, soc);
end

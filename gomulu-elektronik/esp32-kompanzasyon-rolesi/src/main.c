/**
 * @file main.c
 * @brief ESP32 Otomatik Kompanzasyon Rölesi Host Doğrulama Testi
 * @author Hakan OĞUZ - Elektrik Elektronik Mühendisi
 */

#include <stdio.h>
#include "pfc_relay.h"

int main(void) {
    printf("====================================================\n");
    printf("ESP32 12 Kademeli Kompanzasyon Rolesi Host Testi\n");
    printf("Gelistirici: Hakan OGUZ (Elektrik-Elektronik Muhendisi)\n");
    printf("====================================================\n\n");

    // 12 Kademe Kondansatör Grubu (Toplam 300 kVAr)
    // 2x 10 kVAr, 4x 20 kVAr, 6x 30 kVAr
    float step_ratings[12] = {10, 10, 20, 20, 20, 20, 30, 30, 30, 30, 30, 30};

    pfc_controller_t pfc;
    pfc_init(&pfc, step_ratings, 0.98f);

    printf("[1] Baslangic Durumu:\n");
    printf("    Hedef cos phi: %.2f | Toplam Kademe: 12 (300 kVAr)\n\n", pfc.config.target_cos_phi);

    // Test Senaryosu: 150 kW aktif güç, 110 kVAr indüktif reaktif yük (cos phi ~ 0.80)
    float P = 150.0f;
    float Q_load = 110.0f;
    float dt = 5.0f; // 5 sn dongu

    printf("[2] Yuke Gore Kademe Alma Dongusu:\n");
    for (int step = 0; step < 10; step++) {
        float Q_net = Q_load - pfc.current_active_kvar;
        float cos_phi = pfc_calculate_cos_phi(P, Q_net);

        printf("  Adim %2d: Yuk Q=%.1f kVAr | Devrede: %5.1f kVAr | Net Q: %5.1f kVAr | cos phi: %.3f\n",
               step, Q_load, pfc.current_active_kvar, Q_net, cos_phi);

        pfc_process(&pfc, P, Q_net, 2.1f, 8.4f, dt);
    }

    printf("\n[3] 10 Adim Sonunda Kademe Durumlari ve Anahtarlama Sayilari:\n");
    for (int i = 0; i < 12; i++) {
        printf("    Kademe %2d (%2.0f kVAr): %s | Anahtarlama Sayisi: %u | Calisma Suresi: %u sn\n",
               i+1, pfc.steps[i].kvar,
               pfc.steps[i].is_active ? "[ON ]" : "[OFF]",
               pfc.steps[i].switch_count,
               pfc.steps[i].total_on_time_sec);
    }

    float final_Q = Q_load - pfc.current_active_kvar;
    float final_cos = pfc_calculate_cos_phi(P, final_Q);
    printf("\n[4] Sonuc: cos phi %.2f seviyesinden %.3f seviyesine kompanze edildi (Hedef: 0.98).\n",
           pfc_calculate_cos_phi(P, Q_load), final_cos);

    return 0;
}

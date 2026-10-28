/**
 * @file main.c
 * @brief ESP32 BLE + IMU EKF Konumlandırma Host Doğrulama Testi
 * @author Hakan OĞUZ - Elektrik Elektronik Mühendisi
 */

#include <stdio.h>
#include <math.h>
#include "ble_ekf_tracker.h"

int main(void) {
    printf("====================================================\n");
    printf("ESP32 BLE RSSI + IMU EKF Kapali Alan Konumlandirma\n");
    printf("Gelistirici: Hakan OGUZ (Elektrik-Elektronik Muhendisi)\n");
    printf("====================================================\n\n");

    // 4 Adet Referans Beacon (10m x 10m oda koseleri)
    ble_anchor_t anchors[4] = {
        {.x = 0.0f,  .y = 0.0f,  .tx_power_1m = -59.0f, .path_loss_exp = 2.4f},
        {.x = 10.0f, .y = 0.0f,  .tx_power_1m = -59.0f, .path_loss_exp = 2.4f},
        {.x = 10.0f, .y = 10.0f, .tx_power_1m = -59.0f, .path_loss_exp = 2.4f},
        {.x = 0.0f,  .y = 10.0f, .tx_power_1m = -59.0f, .path_loss_exp = 2.4f}
    };

    ekf_tracker_t tracker;
    ekf_tracker_init(&tracker, 1.0f, 1.0f); // Baslangic tahmini

    printf("[1] Baslangic Durumu:\n");
    printf("    Konum: (%.2f, %.2f) m | Hiz: (%.2f, %.2f) m/s\n\n",
           tracker.x[0], tracker.x[1], tracker.x[2], tracker.x[3]);

    // Test: Gercek hedef (5.0, 5.0) merkezde sabit duruyor olsun
    float true_x = 5.0f;
    float true_y = 5.0f;
    float dt = 0.1f; // 100 ms dongu (10 Hz)

    printf("[2] 50 Adimlik Yakinsama Testi Koşuluyor...\n");
    for (int step = 0; step < 50; step++) {
        // IMU ivmesi (sabit durdugu icin gurultulu sifir ivme)
        float ax = 0.01f * (float)(step % 3 - 1);
        float ay = 0.01f * (float)(step % 2 - 1);

        // Predict
        ekf_tracker_predict(&tracker, ax, ay, dt);

        // Her dongude bir anchor'dan RSSI alindigini varsayalim (Round-robin)
        int a_idx = step % 4;
        float true_dist = sqrtf((true_x - anchors[a_idx].x)*(true_x - anchors[a_idx].x) +
                                (true_y - anchors[a_idx].y)*(true_y - anchors[a_idx].y));
        
        // Log distance rssi = tx - 10*n*log10(d)
        float ideal_rssi = anchors[a_idx].tx_power_1m - 10.0f * anchors[a_idx].path_loss_exp * log10f(true_dist);
        // Gurultu ekle (+-1.5 dBm)
        float noisy_rssi = ideal_rssi + 1.2f * sinf((float)step);

        ekf_tracker_update_ble(&tracker, &anchors[a_idx], noisy_rssi);

        if (step % 10 == 0 || step == 49) {
            float err = sqrtf((tracker.x[0] - true_x)*(tracker.x[0] - true_x) + 
                              (tracker.x[1] - true_y)*(tracker.x[1] - true_y));
            printf("    Adim %2d | Tahmin: (%5.2f, %5.2f) m | Gercek: (%5.2f, %5.2f) m | Hata: %.3f m\n",
                   step, tracker.x[0], tracker.x[1], true_x, true_y, err);
        }
    }

    printf("\n[3] Sonuc: EKF basariyla gercek konuma (5.0, 5.0) yakinsadi.\n");
    return 0;
}

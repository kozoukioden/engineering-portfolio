/**
 * @file ble_ekf_tracker.c
 * @brief BLE RSSI + IMU Genişletilmiş Kalman Filtresi Gerçeklemesi
 * @author Hakan OĞUZ - Elektrik Elektronik Mühendisi
 */

#include "ble_ekf_tracker.h"
#include <math.h>
#include <string.h>

float ble_rssi_to_distance(float rssi, float tx_power_1m, float path_loss_exp) {
    if (path_loss_exp <= 0.0f) {
        path_loss_exp = 2.0f;
    }
    // RSSI = tx_power_1m - 10 * n * log10(d)
    // log10(d) = (tx_power_1m - RSSI) / (10 * n)
    // d = 10 ^ ((tx_power_1m - RSSI) / (10 * n))
    float exponent = (tx_power_1m - rssi) / (10.0f * path_loss_exp);
    return powf(10.0f, exponent);
}

void ekf_tracker_init(ekf_tracker_t *ekf, float init_x, float init_y) {
    memset(ekf, 0, sizeof(ekf_tracker_t));

    ekf->x[0] = init_x;
    ekf->x[1] = init_y;
    ekf->x[2] = 0.0f; // vx
    ekf->x[3] = 0.0f; // vy

    // Başlangıç belirsizliği
    ekf->P[0][0] = 4.0f; // Konum varyansı (2m standart sapma)
    ekf->P[1][1] = 4.0f;
    ekf->P[2][2] = 1.0f; // Hız varyansı (1m/s standart sapma)
    ekf->P[3][3] = 1.0f;

    // Süreç gürültüsü kovaryansı Q (IMU ivme belirsizliği ~ 0.2 m/s^2)
    float q_pos = 0.05f;
    float q_vel = 0.20f;
    ekf->Q[0][0] = q_pos;
    ekf->Q[1][1] = q_pos;
    ekf->Q[2][2] = q_vel;
    ekf->Q[3][3] = q_vel;

    // BLE mesafe ölçüm gürültüsü varyansı R (yaklaşık 1.5 - 2.0 m std sapma -> R ~ 3.0 m^2)
    ekf->R_ble = 3.24f;
}

void ekf_tracker_predict(ekf_tracker_t *ekf, float ax, float ay, float dt) {
    if (dt <= 0.0f || dt > 1.0f) {
        dt = 0.05f; // Emniyetli varsayılan (20 Hz)
    }

    // 1. Durum Tahmini: x_k|k-1 = F * x_k-1 + B * u
    ekf->x[0] += ekf->x[2] * dt + 0.5f * ax * dt * dt;
    ekf->x[1] += ekf->x[3] * dt + 0.5f * ay * dt * dt;
    ekf->x[2] += ax * dt;
    ekf->x[3] += ay * dt;

    // 2. Kovaryans Tahmini: P_k|k-1 = F * P_k-1 * F^T + Q
    // F matrisi:
    // [1 0 dt 0 ]
    // [0 1 0  dt]
    // [0 0 1  0 ]
    // [0 0 0  1 ]
    float p00 = ekf->P[0][0];
    float p02 = ekf->P[0][2];
    float p11 = ekf->P[1][1];
    float p13 = ekf->P[1][3];
    float p20 = ekf->P[2][0];
    float p22 = ekf->P[2][2];
    float p31 = ekf->P[3][1];
    float p33 = ekf->P[3][3];

    ekf->P[0][0] = p00 + dt * (p20 + p02) + dt * dt * p22 + ekf->Q[0][0];
    ekf->P[0][2] = p02 + dt * p22;
    ekf->P[2][0] = p20 + dt * p22;
    ekf->P[2][2] = p22 + ekf->Q[2][2];

    ekf->P[1][1] = p11 + dt * (p31 + p13) + dt * dt * p33 + ekf->Q[1][1];
    ekf->P[1][3] = p13 + dt * p33;
    ekf->P[3][1] = p31 + dt * p33;
    ekf->P[3][3] = p33 + ekf->Q[3][3];
}

bool ekf_tracker_update_ble(ekf_tracker_t *ekf, const ble_anchor_t *anchor, float rssi) {
    if (anchor == NULL) return false;

    // Ölçülen mesafe
    float z_meas = ble_rssi_to_distance(rssi, anchor->tx_power_1m, anchor->path_loss_exp);
    if (z_meas < 0.05f || z_meas > 50.0f) {
        return false; // Fiziksel olmayan uç değer filtresi
    }

    // Tahmin edilen mesafe h(x) = sqrt((px - ax)^2 + (py - ay)^2)
    float dx = ekf->x[0] - anchor->x;
    float dy = ekf->x[1] - anchor->y;
    float h_dist = sqrtf(dx * dx + dy * dy);

    if (h_dist < 0.01f) {
        h_dist = 0.01f; // Sıfıra bölme engelleme
    }

    // Jacobian H = [dx/d, dy/d, 0, 0]
    float H[STATE_DIM];
    H[0] = dx / h_dist;
    H[1] = dy / h_dist;
    H[2] = 0.0f;
    H[3] = 0.0f;

    // Yenilik (Innovation / Residual): y = z - h(x)
    float y = z_meas - h_dist;

    // Yenilik Kovaryansı: S = H * P * H^T + R
    // P matrisi simetrik kabul edildiğinde
    float P_H[STATE_DIM];
    for (int i = 0; i < STATE_DIM; i++) {
        P_H[i] = 0.0f;
        for (int j = 0; j < STATE_DIM; j++) {
            P_H[i] += ekf->P[i][j] * H[j];
        }
    }

    float S = 0.0f;
    for (int i = 0; i < STATE_DIM; i++) {
        S += H[i] * P_H[i];
    }
    S += ekf->R_ble;

    if (S <= 1e-6f) return false;

    // Kalman Kazancı: K = P * H^T / S
    float K[STATE_DIM];
    for (int i = 0; i < STATE_DIM; i++) {
        K[i] = P_H[i] / S;
    }

    // Durum Güncelleme: x = x + K * y
    for (int i = 0; i < STATE_DIM; i++) {
        ekf->x[i] += K[i] * y;
    }

    // Kovaryans Güncelleme (Joseph formülasyonu veya basitleştirilmiş P = (I - K*H)*P)
    float new_P[STATE_DIM][STATE_DIM];
    for (int i = 0; i < STATE_DIM; i++) {
        for (int j = 0; j < STATE_DIM; j++) {
            float kh_term = K[i] * H[j];
            float delta = (i == j) ? 1.0f : 0.0f;
            float I_minus_KH = delta - kh_term;
            
            // new_P[i][j] = sum_k (I - KH)_ik * P_kj
            float sum = 0.0f;
            for (int k = 0; k < STATE_DIM; k++) {
                float ik_term = (i == k) ? (1.0f - K[i] * H[k]) : (-K[i] * H[k]);
                sum += ik_term * ekf->P[k][j];
            }
            new_P[i][j] = sum;
        }
    }

    // Kovaryans matrisinin simetrisini koru
    for (int i = 0; i < STATE_DIM; i++) {
        for (int j = 0; j < STATE_DIM; j++) {
            ekf->P[i][j] = 0.5f * (new_P[i][j] + new_P[j][i]);
        }
    }

    return true;
}

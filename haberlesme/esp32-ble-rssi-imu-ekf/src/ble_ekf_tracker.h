/**
 * @file ble_ekf_tracker.h
 * @brief BLE RSSI ve IMU Füzyonlu Genişletilmiş Kalman Filtresi (EKF) Kapalı Alan Konumlandırma
 * @author Hakan OĞUZ - Elektrik Elektronik Mühendisi
 */

#ifndef BLE_EKF_TRACKER_H
#define BLE_EKF_TRACKER_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define MAX_BEACONS 6
#define STATE_DIM   4 // [px, py, vx, vy]

/**
 * @brief Sabit BLE Referans İstasyonu (Beacon / Anchor) Yapısı
 */
typedef struct {
    uint8_t mac[6];
    float x;             // m
    float y;             // m
    float tx_power_1m;   // -59 dBm (1 metre referans gücü)
    float path_loss_exp; // n (2.0 - 3.5 tipik kapalı ortam)
} ble_anchor_t;

/**
 * @brief EKF Durum Vektörü ve Kovaryans Matrisi
 */
typedef struct {
    float x[STATE_DIM];                 // [px, py, vx, vy]
    float P[STATE_DIM][STATE_DIM];     // Hata kovaryansı
    float Q[STATE_DIM][STATE_DIM];     // Süreç gürültüsü kovaryansı
    float R_ble;                       // BLE mesafe ölçüm varyansı (m^2)
    float last_timestamp_s;
} ekf_tracker_t;

/**
 * @brief EKF İzleyiciyi başlatır
 */
void ekf_tracker_init(ekf_tracker_t *ekf, float init_x, float init_y);

/**
 * @brief IMU ivme verisi ile durum tahmini (Prediction Step)
 * @param ax X ekseni gövde/dünya ivmesi (m/s^2)
 * @param ay Y ekseni gövde/dünya ivmesi (m/s^2)
 * @param dt Örnekleme periyodu (s)
 */
void ekf_tracker_predict(ekf_tracker_t *ekf, float ax, float ay, float dt);

/**
 * @brief BLE RSSI ölçümü ile durum güncellemesi (Measurement Update Step)
 * @param anchor İlgili çapanın koordinatları ve parametreleri
 * @param rssi Ölçülen anlık veya filtrelenmiş RSSI (dBm)
 * @return Güncelleme başarılı ise true
 */
bool ekf_tracker_update_ble(ekf_tracker_t *ekf, const ble_anchor_t *anchor, float rssi);

/**
 * @brief RSSI değerini Log-Distance Path Loss modeline göre mesafeye çevirir
 */
float ble_rssi_to_distance(float rssi, float tx_power_1m, float path_loss_exp);

#ifdef __cplusplus
}
#endif

#endif // BLE_EKF_TRACKER_H

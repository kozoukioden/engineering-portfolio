// Hakan OĞUZ - Elektrik Elektronik Mühendisi
#ifndef BLE_EKF_TRACKER_H
#define BLE_EKF_TRACKER_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define MAX_BEACONS 6
#define STATE_DIM   4


typedef struct {
    uint8_t mac[6];
    float x;
    float y;
    float tx_power_1m;
    float path_loss_exp;
} ble_anchor_t;


typedef struct {
    float x[STATE_DIM];
    float P[STATE_DIM][STATE_DIM];
    float Q[STATE_DIM][STATE_DIM];
    float R_ble;
    float last_timestamp_s;
} ekf_tracker_t;


void ekf_tracker_init(ekf_tracker_t *ekf, float init_x, float init_y);


void ekf_tracker_predict(ekf_tracker_t *ekf, float ax, float ay, float dt);


bool ekf_tracker_update_ble(ekf_tracker_t *ekf, const ble_anchor_t *anchor, float rssi);


float ble_rssi_to_distance(float rssi, float tx_power_1m, float path_loss_exp);

#ifdef __cplusplus
}
#endif

#endif

/*
 * Author : Hakan OĞUZ - Elektrik Elektronik Mühendisi
 * Project: CAN (TWAI) Tabanlı Dağıtık Sensör Düğümü
 * Date   : 2026-10-26
 * License: MIT
 * Desc   : CAN telemetri ve heartbeat paketleme/ayrıştırma mantığı
 */

#include "can_protocol.h"
#include <string.h>

bool can_protocol_pack_telemetry(const sensor_telemetry_t *sensor, can_frame_t *frame)
{
    if (!sensor || !frame) {
        return false;
    }

    frame->identifier = CAN_ID_SENSOR_TELEMETRY;
    frame->dlc = 8;

    /* Sıcaklık: 0.01 C çözünürlük ile int16_t */
    int16_t temp_raw = (int16_t)(sensor->temperature_c * 100.0f);
    frame->data[0] = (uint8_t)(temp_raw & 0xFF);
    frame->data[1] = (uint8_t)((temp_raw >> 8) & 0xFF);

    /* X İvmesi: 0.001 g (1 mg) ile int16_t */
    int16_t ax_raw = (int16_t)(sensor->accel_x_g * 1000.0f);
    frame->data[2] = (uint8_t)(ax_raw & 0xFF);
    frame->data[3] = (uint8_t)((ax_raw >> 8) & 0xFF);

    /* Y İvmesi: 0.001 g (1 mg) ile int16_t */
    int16_t ay_raw = (int16_t)(sensor->accel_y_g * 1000.0f);
    frame->data[4] = (uint8_t)(ay_raw & 0xFF);
    frame->data[5] = (uint8_t)((ay_raw >> 8) & 0xFF);

    /* Z İvmesi: 0.1 g çözünürlük ile int8_t */
    int8_t az_raw = (int8_t)(sensor->accel_z_g * 10.0f);
    frame->data[6] = (uint8_t)az_raw;

    /* Byte 7: Rolling counter (üst 4 bit) */
    frame->data[7] = (uint8_t)((sensor->rolling_counter & 0x0F) << 4);

    return true;
}

bool can_protocol_unpack_telemetry(const can_frame_t *frame, sensor_telemetry_t *sensor)
{
    if (!frame || !sensor || frame->dlc < 8) {
        return false;
    }

    int16_t temp_raw = (int16_t)((uint16_t)frame->data[0] | ((uint16_t)frame->data[1] << 8));
    sensor->temperature_c = (float)temp_raw / 100.0f;

    int16_t ax_raw = (int16_t)((uint16_t)frame->data[2] | ((uint16_t)frame->data[3] << 8));
    sensor->accel_x_g = (float)ax_raw / 1000.0f;

    int16_t ay_raw = (int16_t)((uint16_t)frame->data[4] | ((uint16_t)frame->data[5] << 8));
    sensor->accel_y_g = (float)ay_raw / 1000.0f;

    int8_t az_raw = (int8_t)frame->data[6];
    sensor->accel_z_g = (float)az_raw / 10.0f;

    sensor->rolling_counter = (frame->data[7] >> 4) & 0x0F;

    return true;
}

void can_protocol_pack_heartbeat(uint8_t node_id, node_state_t state, uint8_t tec, uint8_t rec, uint32_t uptime_sec, can_frame_t *frame)
{
    if (!frame) return;

    frame->identifier = CAN_ID_NODE_HEARTBEAT;
    frame->dlc = 8;
    frame->data[0] = node_id;
    frame->data[1] = (uint8_t)state;
    frame->data[2] = tec;
    frame->data[3] = rec;
    frame->data[4] = (uint8_t)(uptime_sec & 0xFF);
    frame->data[5] = (uint8_t)((uptime_sec >> 8) & 0xFF);
    frame->data[6] = (uint8_t)((uptime_sec >> 16) & 0xFF);
    frame->data[7] = (uint8_t)((uptime_sec >> 24) & 0xFF);
}

// Hakan OĞUZ - Elektrik Elektronik Mühendisi
#ifndef CAN_PROTOCOL_H
#define CAN_PROTOCOL_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif


#define CAN_ID_NODE_HEARTBEAT       0x120
#define CAN_ID_SENSOR_TELEMETRY     0x240
#define CAN_ID_ALARM_CRITICAL       0x080


typedef enum {
    NODE_STATE_BOOT         = 0x01,
    NODE_STATE_RUNNING      = 0x02,
    NODE_STATE_WARNING      = 0x03,
    NODE_STATE_BUS_OFF_RECOV= 0x04,
    NODE_STATE_ERROR        = 0x05
} node_state_t;


typedef struct {
    float temperature_c;
    float accel_x_g;
    float accel_y_g;
    float accel_z_g;
    uint8_t rolling_counter;
} sensor_telemetry_t;


typedef struct {
    uint32_t identifier;
    uint8_t  dlc;
    uint8_t  data[8];
} can_frame_t;


bool can_protocol_pack_telemetry(const sensor_telemetry_t *sensor, can_frame_t *frame);


bool can_protocol_unpack_telemetry(const can_frame_t *frame, sensor_telemetry_t *sensor);


void can_protocol_pack_heartbeat(uint8_t node_id, node_state_t state, uint8_t tec, uint8_t rec, uint32_t uptime_sec, can_frame_t *frame);

#ifdef __cplusplus
}
#endif

#endif

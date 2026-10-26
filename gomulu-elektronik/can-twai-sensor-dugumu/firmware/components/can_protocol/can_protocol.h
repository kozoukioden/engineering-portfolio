/*
 * Author : Hakan OĞUZ - Elektrik Elektronik Mühendisi
 * Project: CAN (TWAI) Tabanlı Dağıtık Sensör Düğümü
 * Date   : 2026-10-26
 * License: MIT
 * Desc   : Endüstriyel CAN 2.0B / TWAI çerçeve tanımları, serileştirme ve hata ayrıştırma başlığı
 */

#ifndef CAN_PROTOCOL_H
#define CAN_PROTOCOL_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* CAN 2.0B Standart ve Genişletilmiş Mesaj ID Tanımları */
#define CAN_ID_NODE_HEARTBEAT       0x120   /* Periyot: 1000 ms, Durum ve Hata Sayacı */
#define CAN_ID_SENSOR_TELEMETRY     0x240   /* Periyot: 100 ms, Sıcaklık ve 3-Eksen İvme/Titreşim */
#define CAN_ID_ALARM_CRITICAL       0x080   /* Öncelikli ID: Eşik aşımı veya donanım hatası */

/* Düğüm Durum Kodları (Heartbeat içerisinde taşınır) */
typedef enum {
    NODE_STATE_BOOT         = 0x01,
    NODE_STATE_RUNNING      = 0x02,
    NODE_STATE_WARNING      = 0x03,
    NODE_STATE_BUS_OFF_RECOV= 0x04,
    NODE_STATE_ERROR        = 0x05
} node_state_t;

/* Ham sensör telemetri veri yapısı */
typedef struct {
    float temperature_c;    /* -40.0 C ... +125.0 C (0.01 C çözünürlük) */
    float accel_x_g;        /* -16.0 g ... +16.0 g (0.001 g çözünürlük) */
    float accel_y_g;
    float accel_z_g;
    uint8_t rolling_counter;/* 0..15 sekans sayacı */
} sensor_telemetry_t;

/* CAN Çerçevesi Yükü (8 Bayt Packed Payload) */
typedef struct {
    uint32_t identifier;
    uint8_t  dlc;
    uint8_t  data[8];
} can_frame_t;

/**
 * @brief Telemetri verisini 8 baytlık standart CAN yüküne serileştirir
 * Byte 0-1: Sıcaklık (int16_t, scale = 0.01 C, offset = 0)
 * Byte 2-3: X Titreşim / İvme (int16_t, scale = 0.001 g)
 * Byte 4-5: Y Titreşim / İvme (int16_t, scale = 0.001 g)
 * Byte 6:   Z Titreşim / İvme (int8_t, scale = 0.1 g)
 * Byte 7:   [7:4] Rolling Counter (0-15), [3:0] Durum Bayrakları
 */
bool can_protocol_pack_telemetry(const sensor_telemetry_t *sensor, can_frame_t *frame);

/**
 * @brief CAN çerçevesinden sensör telemetri verisini ayrıştırır (Deserialize)
 */
bool can_protocol_unpack_telemetry(const can_frame_t *frame, sensor_telemetry_t *sensor);

/**
 * @brief Düğüm yaşam döngüsü (Heartbeat) çerçevesini paketler
 * Byte 0: Düğüm ID (1..255)
 * Byte 1: Düğüm Durumu (node_state_t)
 * Byte 2: TEC (Transmit Error Counter)
 * Byte 3: REC (Receive Error Counter)
 * Byte 4-7: Çalışma Süresi (Uptime saniye)
 */
void can_protocol_pack_heartbeat(uint8_t node_id, node_state_t state, uint8_t tec, uint8_t rec, uint32_t uptime_sec, can_frame_t *frame);

#ifdef __cplusplus
}
#endif

#endif /* CAN_PROTOCOL_H */

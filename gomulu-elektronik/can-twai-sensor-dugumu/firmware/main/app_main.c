/*
 * Author : Hakan OĞUZ - Elektrik Elektronik Mühendisi
 * Project: CAN (TWAI) Tabanlı Dağıtık Sensör Düğümü
 * Date   : 2026-10-26
 * License: MIT
 * Desc   : ESP-IDF TWAI (Two-Wire Automotive Interface / CAN) sürücüsü ve görev döngüsü
 */

#include <stdio.h>
#include <string.h>
#include <math.h>

#ifdef ESP_PLATFORM
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/twai.h"
#include "esp_log.h"
#endif

#include "can_protocol.h"

static const char *TAG = "CAN_NODE";

#define TX_GPIO_NUM     GPIO_NUM_21
#define RX_GPIO_NUM     GPIO_NUM_22
#define NODE_DEVICE_ID  0x05

#ifdef ESP_PLATFORM
/* TWAI başlatma ve filtre konfigürasyonu */
static esp_err_t twai_node_init(void)
{
    /* 500 kbps Standart Endüstriyel / Otomotiv Hızı */
    twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(TX_GPIO_NUM, RX_GPIO_NUM, TWAI_MODE_NORMAL);
    twai_timing_config_t t_config = TWAI_TIMING_CONFIG_500KBITS();
    twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();

    esp_err_t ret = twai_driver_install(&g_config, &t_config, &f_config);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "TWAI driver install failed: %s", esp_err_to_name(ret));
        return ret;
    }

    ret = twai_start();
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "TWAI driver start failed: %s", esp_err_to_name(ret));
    }
    return ret;
}

/* Bus-off kurtarma döngüsü */
static void handle_bus_recovery(void)
{
    uint32_t alerts = 0;
    twai_read_alerts(&alerts, pdMS_TO_TICKS(10));
    
    if (alerts & TWAI_ALERT_BUS_OFF) {
        ESP_LOGW(TAG, "CAN Bus-Off tespit edildi! Otomatik kurtarma baslatiliyor...");
        twai_initiate_recovery();
    }
    if (alerts & TWAI_ALERT_BUS_RECOVERED) {
        ESP_LOGI(TAG, "CAN Bus-Off kurtarma tamamlandi, TWAI yeniden baslatiliyor.");
        twai_start();
    }
}

/* 100 Hz Telemetri ve 1 Hz Heartbeat Görevi */
static void twai_transmit_task(void *pvParameters)
{
    sensor_telemetry_t sensor = {
        .temperature_c = 42.5f,
        .accel_x_g = 0.05f,
        .accel_y_g = -0.02f,
        .accel_z_g = 1.01f,
        .rolling_counter = 0
    };

    uint32_t tick_count = 0;
    can_frame_t frame;
    twai_message_t tx_msg;

    while (1) {
        /* Sentetik titreşim dalgalanması */
        sensor.accel_x_g = 0.25f * sinf(tick_count * 0.1f);
        sensor.rolling_counter = (sensor.rolling_counter + 1) & 0x0F;

        /* Telemetri paketi (100 ms) */
        if (can_protocol_pack_telemetry(&sensor, &frame)) {
            tx_msg.identifier = frame.identifier;
            tx_msg.data_length_code = frame.dlc;
            tx_msg.flags = TWAI_MSG_FLAG_NONE;
            memcpy(tx_msg.data, frame.data, 8);

            esp_err_t err = twai_transmit(&tx_msg, pdMS_TO_TICKS(10));
            if (err != ESP_OK) {
                ESP_LOGD(TAG, "Telemetri gonderim beklemede: %s", esp_err_to_name(err));
            }
        }

        /* Heartbeat paketi (1000 ms - her 10 adımda bir) */
        if (tick_count % 10 == 0) {
            twai_status_info_t status;
            twai_get_status_info(&status);

            node_state_t state = (status.state == TWAI_STATE_RUNNING) ? NODE_STATE_RUNNING : NODE_STATE_WARNING;
            can_protocol_pack_heartbeat(NODE_DEVICE_ID, state, status.tx_error_counter, status.rx_error_counter, tick_count / 10, &frame);

            tx_msg.identifier = frame.identifier;
            tx_msg.data_length_code = frame.dlc;
            tx_msg.flags = TWAI_MSG_FLAG_NONE;
            memcpy(tx_msg.data, frame.data, 8);
            twai_transmit(&tx_msg, pdMS_TO_TICKS(10));
        }

        handle_bus_recovery();
        tick_count++;
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void app_main(void)
{
    ESP_LOGI(TAG, "CAN (TWAI) Dağıtık Sensör Düğümü Başlatılıyor...");
    if (twai_node_init() == ESP_OK) {
        xTaskCreatePinnedToCore(twai_transmit_task, "twai_tx_task", 4096, NULL, 5, NULL, 1);
    }
}
#else
int main(void)
{
    printf("CAN TWAI Host Test stub - simulation suite provides full validation.\n");
    return 0;
}
#endif

/*
 * Author : Hakan OĞUZ - Elektrik Elektronik Mühendisi
 * Project: ESP32 Kestirimci Bakım Düğümü (Titreşim ve MCSA Teşhisi)
 * Date   : 2026-10-27
 * License: MIT
 * Desc   : FreeRTOS titreşim/akım toplama, FFT teşhis görevi ve MQTT/Modbus alarm yönetimi
 */

#include <stdio.h>
#include <string.h>

#ifdef ESP_PLATFORM
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#endif

#include "dsp_diagnostics.h"

static const char *TAG = "PRED_MAINT";

#ifdef ESP_PLATFORM
static void predictive_maintenance_task(void *pvParameters)
{
    bearing_fault_freqs_t bearing;
    /* 6208 Rulmanı: Nb=9, d=12mm, D=60mm, RPM=1450 */
    bearing_calc_freqs(9, 12.0f, 60.0f, 0.0f, 1450.0f, &bearing);

    ESP_LOGI(TAG, "Rulman Frekanslari -> 1X: %.2f Hz, BPFO: %.2f Hz, BPFI: %.2f Hz",
             bearing.f_shaft_hz, bearing.bpfo_hz, bearing.bpfi_hz);

    float accel_buffer[FFT_SIZE];

    while (1) {
        /* I2S / SPI üzerinden ivmeölçer DMA tamponunu oku */
        /* ... */

        float v_rms = compute_vibration_velocity_rms(accel_buffer, FFT_SIZE, 1.0f / SAMPLING_FREQ_HZ);
        iso_vibration_zone_t zone = ISO_ZONE_A_GOOD;

        if (v_rms >= 4.5f) {
            zone = ISO_ZONE_D_DANGER;
            ESP_LOGE(TAG, "KRITIK TITRESIM ALARMI! Vrms = %.2f mm/s (Zone D - Derhal Bakim)", v_rms);
        } else if (v_rms >= 2.8f) {
            zone = ISO_ZONE_C_RESTRICTED;
            ESP_LOGW(TAG, "TITRESIM UYARISI! Vrms = %.2f mm/s (Zone C - Takip)", v_rms);
        } else {
            ESP_LOGI(TAG, "Motor Durumu Normal: Vrms = %.2f mm/s (Zone A/B)", v_rms);
        }

        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

void app_main(void)
{
    ESP_LOGI(TAG, "ESP32 Kestirimci Bakim ve Titresim Tehis Dugumu Baslatiliyor...");
    xTaskCreatePinnedToCore(predictive_maintenance_task, "maint_task", 4096, NULL, 5, NULL, 1);
}
#else
int main(void)
{
    printf("DSP Diagnostics host verification test suite is available under sim/ directory.\n");
    return 0;
}
#endif

/*
 * Author : Hakan OĞUZ - Elektrik Elektronik Mühendisi
 * Project: Çok Kanallı Termokupl Veri Toplama ve PID Isı Kontrolü
 * Date   : 2026-10-26
 * License: MIT
 * Desc   : 4 Kanallı SPI Termokupl Okuma ve Isıtıcı PWM Sürücü Görevi
 */

#include <stdio.h>
#include <string.h>

#ifdef ESP_PLATFORM
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/spi_master.h"
#include "driver/ledc.h"
#include "esp_log.h"
#endif

#include "temp_control.h"

static const char *TAG = "THERMO_PID";

#define NUM_CHANNELS        4
#define SETPOINT_TEMP_C     185.0f  /* Hedef Proses Sıcaklığı (Örn: Plastik Enjeksiyon / Fırın) */
#define OVERTEMP_ALARM_C    220.0f  /* Emniyet Kesme Eşiği */

#ifdef ESP_PLATFORM
/* 4 Kanal için bağımsız CS (Chip Select) Pinleri */
static const int cs_pins[NUM_CHANNELS] = { 15, 16, 17, 18 };

static void temp_control_task(void *pvParameters)
{
    pid_controller_t heater_pid;
    /* Kp = 4.5, Ki = 0.25, Kd = 1.2, dt = 0.5 s, PWM = %0 ... %100 */
    pid_init(&heater_pid, 4.5f, 0.25f, 1.2f, 0.5f, 0.0f, 100.0f);

    float temps[NUM_CHANNELS] = { 25.0f, 25.0f, 25.0f, 25.0f };

    while (1) {
        /* SPI üzerinden 4 kanalı tara */
        for (int ch = 0; ch < NUM_CHANNELS; ch++) {
            /* max31856_read_channel(ch, &temps[ch]); */
        }

        /* Ana ısıtıcı kontrol kanalı (Kanal 0) */
        float current_temp = temps[0];
        float pwm_duty = 0.0f;

        if (current_temp >= OVERTEMP_ALARM_C) {
            ESP_LOGE(TAG, "ASIRI SICAKLIK ALARMI! (%.2f C) Isitici derhal kapatildi!", current_temp);
            pwm_duty = 0.0f;
        } else {
            pwm_duty = pid_compute(&heater_pid, SETPOINT_TEMP_C, current_temp);
        }

        ESP_LOGI(TAG, "Kanal 0: %.2f C | Hedef: %.2f C | PID Cikis: %%.1f PWM", current_temp, SETPOINT_TEMP_C, pwm_duty);
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

void app_main(void)
{
    ESP_LOGI(TAG, "Cok Kanalli Termokupl ve PID Isı Kontrol Sistemi Baslatiliyor...");
    xTaskCreatePinnedToCore(temp_control_task, "pid_task", 4096, NULL, 5, NULL, 1);
}
#else
int main(void)
{
    printf("Host test simulation available under sim/ directory.\n");
    return 0;
}
#endif

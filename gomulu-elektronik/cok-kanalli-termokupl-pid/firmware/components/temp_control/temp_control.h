/*
 * Author : Hakan OĞUZ - Elektrik Elektronik Mühendisi
 * Project: Çok Kanallı Termokupl Veri Toplama ve PID Isı Kontrolü
 * Date   : 2026-10-26
 * License: MIT
 * Desc   : MAX31856 SPI termokupl arayüzü ve anti-windup PID denetleyici başlığı
 */

#ifndef TEMP_CONTROL_H
#define TEMP_CONTROL_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* MAX31856 SPI Kaydedici Adresleri */
#define MAX31856_CR0_REG        0x00    /* Konfigürasyon 0 (Dönüşüm modu, 50/60Hz filtre) */
#define MAX31856_CR1_REG        0x01    /* Konfigürasyon 1 (Termokupl tipi K, J, T vs.) */
#define MAX31856_MASK_REG       0x02    /* Arıza maskesi */
#define MAX31856_CJTH_REG       0x0A    /* Soğuk-uç sıcaklığı MSB */
#define MAX31856_LTCBH_REG      0x0C    /* Doğrusallaştırılmış termokupl sıcaklığı MSB */
#define MAX31856_SR_REG         0x0F    /* Durum kaydedicisi (Açık devre, aşırı voltaj) */

/* K-Tipi Termokupl Sabiti: 0b0011 */
#define THERMOCOUPLE_TYPE_K     0x03

/* Arıza bayrakları */
#define FAULT_OPEN_CIRCUIT      (1 << 0)
#define FAULT_VOLTAGE_OVRANGE   (1 << 1)
#define FAULT_TC_RANGE_HIGH     (1 << 2)
#define FAULT_TC_RANGE_LOW      (1 << 3)

/* PID Denetleyici Yapısı */
typedef struct {
    float kp;               /* Oransal kazanç */
    float ki;               /* İntegral kazanç */
    float kd;               /* Türevsel kazanç */
    float dt;               /* Örnekleme süresi [s] */
    float out_min;          /* Minimum çıkış [%0] */
    float out_max;          /* Maksimum çıkış [%100 PWM] */
    
    float integral;         /* İntegral birikimi */
    float prev_error;       /* Önceki hata */
    float prev_measurement; /* Türev tekmesi (derivative kick) önleyici ölçüm */
} pid_controller_t;

/**
 * @brief PID denetleyiciyi ilklendirir
 */
void pid_init(pid_controller_t *pid, float kp, float ki, float kd, float dt, float out_min, float out_max);

/**
 * @brief Anti-windup (integratör kelepçeleme) özellikli PID hesap adımı
 */
float pid_compute(pid_controller_t *pid, float setpoint, float measured_temp);

/**
 * @brief MAX31856'dan okunan 3 baytlık ham veriyi Celsius sıcaklığına çevirir
 * @param ltcbm_bytes 3 baytlık ham dizi (Byte 0: MSB, Byte 1: LSB, Byte 2: Fractional)
 * @return float Sıcaklık [°C] (0.0078125 °C = 2^-7 çözünürlük)
 */
float max31856_raw_to_celsius(const uint8_t *ltcbm_bytes);

#ifdef __cplusplus
}
#endif

#endif /* TEMP_CONTROL_H */

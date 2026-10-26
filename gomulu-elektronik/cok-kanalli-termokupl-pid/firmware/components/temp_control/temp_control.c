/*
 * Author : Hakan OĞUZ - Elektrik Elektronik Mühendisi
 * Project: Çok Kanallı Termokupl Veri Toplama ve PID Isı Kontrolü
 * Date   : 2026-10-26
 * License: MIT
 * Desc   : MAX31856 sıcaklık dönüşümü ve anti-windup PID algoritması
 */

#include "temp_control.h"

void pid_init(pid_controller_t *pid, float kp, float ki, float kd, float dt, float out_min, float out_max)
{
    if (!pid) return;
    pid->kp = kp;
    pid->ki = ki;
    pid->kd = kd;
    pid->dt = dt;
    pid->out_min = out_min;
    pid->out_max = out_max;
    pid->integral = 0.0f;
    pid->prev_error = 0.0f;
    pid->prev_measurement = 0.0f;
}

float pid_compute(pid_controller_t *pid, float setpoint, float measured_temp)
{
    if (!pid || pid->dt <= 0.0f) return 0.0f;

    float error = setpoint - measured_temp;

    /* 1. Oransal Terim */
    float p_term = pid->kp * error;

    /* 2. İntegral Terim */
    pid->integral += error * pid->dt;

    /* 3. Türevsel Terim (Derivative on Measurement - Setpoint basamağında sıçramayı önler) */
    float d_meas = (measured_temp - pid->prev_measurement) / pid->dt;
    float d_term = -pid->kd * d_meas;

    /* Ham Kontrol Çıktısı */
    float output_raw = p_term + (pid->ki * pid->integral) + d_term;

    /* 4. Anti-Windup (Clamping / Kelepçeleme) Mantığı */
    float output = output_raw;
    if (output_raw > pid->out_max) {
        output = pid->out_max;
        /* Doyumdayken hata aynı yönde ise integrali geri al */
        if (error > 0.0f) {
            pid->integral -= error * pid->dt;
        }
    } else if (output_raw < pid->out_min) {
        output = pid->out_min;
        if (error < 0.0f) {
            pid->integral -= error * pid->dt;
        }
    }

    pid->prev_error = error;
    pid->prev_measurement = measured_temp;

    return output;
}

float max31856_raw_to_celsius(const uint8_t *b)
{
    if (!b) return 0.0f;

    /* MAX31856 Linearized TC Temperature Register (19-bit signed):
     * [18:11] Byte 0 (LTCBH)
     * [10:3]  Byte 1 (LTCBM)
     * [2:0]   Byte 2 (LTCBL) üst 3 bit -> b[2] >> 5
     * Katsayı: 2^-7 = 0.0078125 °C / LSB
     */
    int32_t raw = ((int32_t)b[0] << 16) | ((int32_t)b[1] << 8) | (int32_t)b[2];
    raw >>= 5; /* 19-bit hizalama */

    /* İşaret uzatma (Sign extension) */
    if (b[0] & 0x80) {
        raw |= 0xFFF80000;
    }

    return (float)raw * 0.0078125f;
}

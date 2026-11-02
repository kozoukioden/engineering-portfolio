// Hakan OĞUZ - Elektrik Elektronik Mühendisi
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


    float p_term = pid->kp * error;


    pid->integral += error * pid->dt;


    float d_meas = (measured_temp - pid->prev_measurement) / pid->dt;
    float d_term = -pid->kd * d_meas;


    float output_raw = p_term + (pid->ki * pid->integral) + d_term;


    float output = output_raw;
    if (output_raw > pid->out_max) {
        output = pid->out_max;

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


    int32_t raw = ((int32_t)b[0] << 16) | ((int32_t)b[1] << 8) | (int32_t)b[2];
    raw >>= 5;


    if (b[0] & 0x80) {
        raw |= 0xFFF80000;
    }

    return (float)raw * 0.0078125f;
}

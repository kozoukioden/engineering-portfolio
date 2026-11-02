// Hakan OĞUZ - Elektrik Elektronik Mühendisi
#ifndef TEMP_CONTROL_H
#define TEMP_CONTROL_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif


#define MAX31856_CR0_REG        0x00
#define MAX31856_CR1_REG        0x01
#define MAX31856_MASK_REG       0x02
#define MAX31856_CJTH_REG       0x0A
#define MAX31856_LTCBH_REG      0x0C
#define MAX31856_SR_REG         0x0F


#define THERMOCOUPLE_TYPE_K     0x03


#define FAULT_OPEN_CIRCUIT      (1 << 0)
#define FAULT_VOLTAGE_OVRANGE   (1 << 1)
#define FAULT_TC_RANGE_HIGH     (1 << 2)
#define FAULT_TC_RANGE_LOW      (1 << 3)


typedef struct {
    float kp;
    float ki;
    float kd;
    float dt;
    float out_min;
    float out_max;

    float integral;
    float prev_error;
    float prev_measurement;
} pid_controller_t;


void pid_init(pid_controller_t *pid, float kp, float ki, float kd, float dt, float out_min, float out_max);


float pid_compute(pid_controller_t *pid, float setpoint, float measured_temp);


float max31856_raw_to_celsius(const uint8_t *ltcbm_bytes);

#ifdef __cplusplus
}
#endif

#endif

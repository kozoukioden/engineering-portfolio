// Hakan OĞUZ - Elektrik Elektronik Mühendisi
#ifndef PFC_RELAY_H
#define PFC_RELAY_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define PFC_MAX_STEPS 12
#define MAX_CONTACTOR_CYCLES 100000

typedef struct {
    float kvar;
    bool is_active;
    uint32_t switch_count;
    uint32_t total_on_time_sec;
    uint32_t discharge_timer;
} pfc_step_t;

typedef struct {
    float target_cos_phi;
    float deadband_kvar;
    float thd_v_limit;
    float thd_i_limit;
    uint32_t min_discharge_time;
} pfc_config_t;

typedef struct {
    pfc_step_t steps[PFC_MAX_STEPS];
    pfc_config_t config;
    bool harmonic_resonance_alarm;
    float current_active_kvar;
} pfc_controller_t;


void pfc_init(pfc_controller_t *pfc, const float step_ratings[PFC_MAX_STEPS], float target_cos);


void pfc_process(pfc_controller_t *pfc, float P_kw, float Q_kvar, float thd_v, float thd_i, float dt_sec);


float pfc_calculate_cos_phi(float P, float Q);

#ifdef __cplusplus
}
#endif

#endif

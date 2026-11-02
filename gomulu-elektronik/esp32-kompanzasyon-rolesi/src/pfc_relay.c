// Hakan OĞUZ - Elektrik Elektronik Mühendisi
#include "pfc_relay.h"
#include <math.h>
#include <string.h>

float pfc_calculate_cos_phi(float P, float Q) {
    float S = sqrtf(P * P + Q * Q);
    if (S < 1e-3f) return 1.0f;
    return P / S;
}

void pfc_init(pfc_controller_t *pfc, const float step_ratings[PFC_MAX_STEPS], float target_cos) {
    memset(pfc, 0, sizeof(pfc_controller_t));

    pfc->config.target_cos_phi = (target_cos > 0.8f && target_cos <= 1.0f) ? target_cos : 0.98f;
    pfc->config.deadband_kvar = 5.0f;
    pfc->config.thd_v_limit = 5.0f;
    pfc->config.thd_i_limit = 20.0f;
    pfc->config.min_discharge_time = 30;

    pfc->current_active_kvar = 0.0f;
    pfc->harmonic_resonance_alarm = false;

    for (int i = 0; i < PFC_MAX_STEPS; i++) {
        pfc->steps[i].kvar = (step_ratings != NULL) ? step_ratings[i] : 25.0f;
        pfc->steps[i].is_active = false;
        pfc->steps[i].switch_count = 0;
        pfc->steps[i].total_on_time_sec = 0;
        pfc->steps[i].discharge_timer = 0;
    }
}

void pfc_process(pfc_controller_t *pfc, float P_kw, float Q_kvar, float thd_v, float thd_i, float dt_sec) {

    for (int i = 0; i < PFC_MAX_STEPS; i++) {
        if (pfc->steps[i].is_active) {
            pfc->steps[i].total_on_time_sec += (uint32_t)dt_sec;
        } else if (pfc->steps[i].discharge_timer > 0) {
            if (pfc->steps[i].discharge_timer >= (uint32_t)dt_sec) {
                pfc->steps[i].discharge_timer -= (uint32_t)dt_sec;
            } else {
                pfc->steps[i].discharge_timer = 0;
            }
        }
    }


    if (thd_v > pfc->config.thd_v_limit || thd_i > pfc->config.thd_i_limit) {
        pfc->harmonic_resonance_alarm = true;


        return;
    } else {
        pfc->harmonic_resonance_alarm = false;
    }

    if (P_kw < 2.0f) {

        return;
    }


    float phi_target = acosf(pfc->config.target_cos_phi);
    float Q_target = P_kw * tanf(phi_target);


    float Q_needed = Q_kvar - Q_target;


    if (Q_needed > pfc->config.deadband_kvar) {
        int best_candidate = -1;
        uint32_t min_switches = 0xFFFFFFFF;
        float best_kvar_diff = 1e6f;

        for (int i = 0; i < PFC_MAX_STEPS; i++) {

            if (!pfc->steps[i].is_active && pfc->steps[i].discharge_timer == 0) {

                if (pfc->steps[i].kvar <= Q_needed + pfc->config.deadband_kvar) {

                    if (pfc->steps[i].switch_count < min_switches) {
                        min_switches = pfc->steps[i].switch_count;
                        best_candidate = i;
                    }
                }
            }
        }

        if (best_candidate != -1) {
            pfc->steps[best_candidate].is_active = true;
            pfc->steps[best_candidate].switch_count++;
            pfc->current_active_kvar += pfc->steps[best_candidate].kvar;
        }
    }

    else if (Q_needed < -pfc->config.deadband_kvar || Q_kvar < 0.0f) {
        int best_candidate = -1;
        uint32_t max_on_time = 0;

        for (int i = 0; i < PFC_MAX_STEPS; i++) {
            if (pfc->steps[i].is_active) {

                if (pfc->steps[i].total_on_time_sec >= max_on_time) {
                    max_on_time = pfc->steps[i].total_on_time_sec;
                    best_candidate = i;
                }
            }
        }

        if (best_candidate != -1) {
            pfc->steps[best_candidate].is_active = false;
            pfc->steps[best_candidate].discharge_timer = pfc->config.min_discharge_time;
            pfc->current_active_kvar -= pfc->steps[best_candidate].kvar;
        }
    }
}

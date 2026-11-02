/**
 * @file pfc_relay.c
 * @brief ESP32 Otomatik Kompanzasyon ve Eşit Yaşlandırma Algoritması
 * @author Hakan OĞUZ - Elektrik Elektronik Mühendisi
 */

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
    pfc->config.deadband_kvar = 5.0f; // 5 kVAr histerezis bandı
    pfc->config.thd_v_limit = 5.0f;   // %5 THD-V
    pfc->config.thd_i_limit = 20.0f;  // %20 THD-I
    pfc->config.min_discharge_time = 30; // 30 sn emniyetli deşarj süresi

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
    // 1. Sayaç ve Zamanlayıcı Güncellemeleri
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

    // 2. Harmonik Rezonans Güvenlik Denetimi
    if (thd_v > pfc->config.thd_v_limit || thd_i > pfc->config.thd_i_limit) {
        pfc->harmonic_resonance_alarm = true;
        // Yüksek harmonik altında kondansatörlerin delinmesini ve LC rezonansı önlemek için
        // yeni kademe alımı engellenir, gerekirse son kademeler kademeli devreden çıkarılır.
        return;
    } else {
        pfc->harmonic_resonance_alarm = false;
    }

    if (P_kw < 2.0f) {
        // Düşük yükte avcı salınımını önle
        return;
    }

    // 3. Hedef Reaktif Güç Hesabı
    // Q_target = P * tan(acos(target_cos))
    float phi_target = acosf(pfc->config.target_cos_phi);
    float Q_target = P_kw * tanf(phi_target);

    // Gereken ek kapasitif güç: Q_needed = Q_kvar - Q_target
    float Q_needed = Q_kvar - Q_target;

    // 4. Kademe Alma (Devreye Sokma) - Q_needed > deadband
    if (Q_needed > pfc->config.deadband_kvar) {
        int best_candidate = -1;
        uint32_t min_switches = 0xFFFFFFFF;
        float best_kvar_diff = 1e6f;

        for (int i = 0; i < PFC_MAX_STEPS; i++) {
            // Boşta ve deşarj süresi dolmuş kademeler
            if (!pfc->steps[i].is_active && pfc->steps[i].discharge_timer == 0) {
                // Kademe gücü gereken ihtiyacı aşırı taşmamalı (aşırı kompanzasyon engeli)
                if (pfc->steps[i].kvar <= Q_needed + pfc->config.deadband_kvar) {
                    // Eşit Yaşlandırma: Anahtarlama sayısı en az olanı seç
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
    // 5. Kademe Bırakma (Devreden Çıkarma) - Aşırı Kapasitif veya Gereksiz Güç
    else if (Q_needed < -pfc->config.deadband_kvar || Q_kvar < 0.0f) {
        int best_candidate = -1;
        uint32_t max_on_time = 0;

        for (int i = 0; i < PFC_MAX_STEPS; i++) {
            if (pfc->steps[i].is_active) {
                // En uzun süredir devrede olan kademeyi devreden çıkar (eşit dinlenme)
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

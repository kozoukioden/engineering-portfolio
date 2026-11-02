/**
 * @file pfc_relay.h
 * @brief ESP32 12 Kademeli Otomatik Reaktif Güç Kompanzasyon Rölesi
 * @author Hakan OĞUZ - Elektrik Elektronik Mühendisi
 */

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
    float kvar;                 // Kademe gücü (kVAr)
    bool is_active;             // Kademe devrede mi?
    uint32_t switch_count;      // Toplam devreye girme sayısı (ömür sayacı)
    uint32_t total_on_time_sec; // Toplam devrede kalma süresi (sn)
    uint32_t discharge_timer;   // Kondansatör deşarj emniyet kilidi (sn)
} pfc_step_t;

typedef struct {
    float target_cos_phi;       // Hedef cos phi (örn: 0.98 indüktif)
    float deadband_kvar;        // Salınım (hunting) önleme ölü bandı (kVAr)
    float thd_v_limit;          // %5 gerilim harmonik sınırı
    float thd_i_limit;          // %20 akım harmonik sınırı
    uint32_t min_discharge_time;// Yeniden alma için minimum deşarj süresi (sn)
} pfc_config_t;

typedef struct {
    pfc_step_t steps[PFC_MAX_STEPS];
    pfc_config_t config;
    bool harmonic_resonance_alarm;
    float current_active_kvar;
} pfc_controller_t;

/**
 * @brief Kompanzasyon denetleyicisini başlatır
 */
void pfc_init(pfc_controller_t *pfc, const float step_ratings[PFC_MAX_STEPS], float target_cos);

/**
 * @brief Şebeke güç ölçümleriyle kompanzasyon döngüsünü çalıştırır
 * @param P_kw Aktif güç (kW)
 * @param Q_kvar Mevcut reaktif güç (kVAr, pozitif: indüktif, negatif: kapasitif)
 * @param thd_v Gerilim THD yüzdesi (%)
 * @param thd_i Akım THD yüzdesi (%)
 * @param dt_sec Geçen süre (sn)
 */
void pfc_process(pfc_controller_t *pfc, float P_kw, float Q_kvar, float thd_v, float thd_i, float dt_sec);

/**
 * @brief Mevcut güç faktörünü hesaplar
 */
float pfc_calculate_cos_phi(float P, float Q);

#ifdef __cplusplus
}
#endif

#endif // PFC_RELAY_H

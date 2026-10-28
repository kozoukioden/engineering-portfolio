/*
 * Author : Hakan OĞUZ - Elektrik Elektronik Mühendisi
 * Project: ESP32 Kestirimci Bakım Düğümü (Titreşim ve MCSA Teşhisi)
 * Date   : 2026-10-27
 * License: MIT
 * Desc   : Rulman arıza frekansları (BPFO/BPFI), zarf analizi ve ISO 10816 titreşim şiddet bölgeleri
 */

#ifndef DSP_DIAGNOSTICS_H
#define DSP_DIAGNOSTICS_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define FFT_SIZE            1024
#define SAMPLING_FREQ_HZ    5000.0f /* 5 kHz örnekleme (Nyquist = 2.5 kHz) */

/* ISO 10816-3 Titreşim Şiddet Bölgeleri (15 kW - 300 kW Orta/Büyük Motorlar için RMS Hız mm/s) */
typedef enum {
    ISO_ZONE_A_GOOD         = 0, /* Vrms < 1.4 mm/s: Yeni veya kusursuz makine */
    ISO_ZONE_B_ACCEPTABLE   = 1, /* 1.4 <= Vrms < 2.8 mm/s: Sürekli çalışmaya uygun */
    ISO_ZONE_C_RESTRICTED   = 2, /* 2.8 <= Vrms < 4.5 mm/s: Sınırlı çalışma / Takip gerektirir */
    ISO_ZONE_D_DANGER       = 3  /* Vrms >= 4.5 mm/s: Ciddi hasar riski / Derhal durdur */
} iso_vibration_zone_t;

/* Rulman Karakteristik Arıza Frekansları (Nominal 1450 d/d = 24.17 Hz şaft dönüş frekansı için) */
typedef struct {
    float f_shaft_hz;   /* Şaft dönme frekansı (1X) */
    float bpfo_hz;      /* Ball Pass Frequency Outer Race (Dış bilezik arızası) */
    float bpfi_hz;      /* Ball Pass Frequency Inner Race (İç bilezik arızası) */
    float bsf_hz;       /* Ball Spin Frequency (Bilya dönme arızası) */
    float ftf_hz;       /* Fundamental Train Frequency (Kafes arızası) */
} bearing_fault_freqs_t;

/* Teşhis ve analiz sonuç yapısı */
typedef struct {
    float v_rms_mm_s;               /* Titreşim hız RMS değeri [mm/s] */
    iso_vibration_zone_t iso_zone;  /* ISO 10816 bölgesi */
    float peak_accel_g;             /* Tepe ivme değeri [g] */
    float crest_factor;             /* Tepe faktörü (Peak / RMS) */
    float bpfo_energy;              /* BPFO civarındaki spektral enerji */
    float bpfi_energy;              /* BPFI civarındaki spektral enerji */
    bool bpfo_alarm;                /* Dış bilezik arıza uyarısı */
    bool bpfi_alarm;                /* İç bilezik arıza uyarısı */
    bool mcsa_sideband_detected;    /* MCSA kırık rotor çubuğu yan bandı tespiti (f_s +- 2*s*f_s) */
} diagnostic_result_t;

/**
 * @brief Rulman geometrisine göre karakteristik frekansları hesaplar
 * @param n_balls Bilya sayısı
 * @param d_ball Bilya çapı [mm]
 * @param d_pitch Hatve çapı (Pitch diameter) [mm]
 * @param contact_angle_rad Temas açısı [rad]
 * @param rpm Şaft devri [d/d]
 */
void bearing_calc_freqs(int n_balls, float d_ball, float d_pitch, float contact_angle_rad, float rpm, bearing_fault_freqs_t *out_freqs);

/**
 * @brief İvme zaman serisini titreşim hızına entegre eder ve RMS [mm/s] hesaplar
 */
float compute_vibration_velocity_rms(const float *accel_g, int length, float dt);

/**
 * @brief Spektrum enerjisi üzerinden belirli bir arıza frekansı civarını tarar
 */
float extract_band_energy(const float *spectrum_mag, int length, float target_hz, float bin_hz, float tolerance_hz);

#ifdef __cplusplus
}
#endif

#endif /* DSP_DIAGNOSTICS_H */

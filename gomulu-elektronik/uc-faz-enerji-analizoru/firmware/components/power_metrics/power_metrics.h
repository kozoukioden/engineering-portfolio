/*
 * Author : Hakan OGUZ - Elektrik Elektronik Muhendisi
 * Project: Three-phase energy analyzer node (ESP32 / ESP-IDF)
 * Date   : 2026-10-22
 * License: MIT
 * Desc   : Portable DSP core for per-phase RMS, power, PF and THD from sampled waveforms.
 *
 * This module has no ESP-IDF dependency on purpose: the same source is compiled on the
 * host (gcc) against synthetic waveforms for validation, and on the ESP32 inside the
 * acquisition task. The analysis window must cover an integer number of mains cycles.
 */
#ifndef POWER_METRICS_H
#define POWER_METRICS_H

#ifdef __cplusplus
extern "C" {
#endif

/* Highest harmonic order included in the THD sum. */
#define PM_MAX_HARMONIC 15

typedef struct {
    float v_rms;        /* true RMS voltage            [V]   */
    float i_rms;        /* true RMS current            [A]   */
    float p_active;     /* active power  (mean of v*i) [W]   */
    float s_apparent;   /* apparent power  Vrms*Irms   [VA]  */
    float q_nonactive;  /* non-active power sqrt(S^2-P^2) [var] */
    float power_factor; /* P / S                             */
    float thd_v;        /* voltage THD (fraction, x100 = %) */
    float thd_i;        /* current THD (fraction)           */
    float v_fund;       /* fundamental voltage amplitude [V] */
    float i_fund;       /* fundamental current amplitude [A] */
} pm_phase_result_t;

typedef struct {
    pm_phase_result_t ph[3];
    float p_total;      /* Pa+Pb+Pc   [W]  */
    float s_total;      /* Sa+Sb+Sc   [VA] */
    float q_total;      /* Qa+Qb+Qc   [var]*/
    float pf_total;     /* P_total / S_total */
} pm_system_result_t;

/*
 * Analyse one phase.
 *   v, i               : sample buffers in engineering units (V, A)
 *   n                  : total number of samples (must equal cycles * samples_per_cycle)
 *   samples_per_cycle  : samples in one mains period
 * Returns 0 on success, -1 on invalid arguments.
 */
int pm_compute_phase(const float *v, const float *i, int n,
                     int samples_per_cycle, pm_phase_result_t *out);

/* Analyse three phases and fill the aggregate fields. */
int pm_compute_system(const float *va, const float *ia,
                      const float *vb, const float *ib,
                      const float *vc, const float *ic,
                      int n, int samples_per_cycle,
                      pm_system_result_t *out);

#ifdef __cplusplus
}
#endif
#endif /* POWER_METRICS_H */

// Hakan OĞUZ - Elektrik Elektronik Mühendisi
#ifndef POWER_METRICS_H
#define POWER_METRICS_H

#ifdef __cplusplus
extern "C" {
#endif


#define PM_MAX_HARMONIC 15

typedef struct {
    float v_rms;
    float i_rms;
    float p_active;
    float s_apparent;
    float q_nonactive;
    float power_factor;
    float thd_v;
    float thd_i;
    float v_fund;
    float i_fund;
} pm_phase_result_t;

typedef struct {
    pm_phase_result_t ph[3];
    float p_total;
    float s_total;
    float q_total;
    float pf_total;
} pm_system_result_t;


int pm_compute_phase(const float *v, const float *i, int n,
                     int samples_per_cycle, pm_phase_result_t *out);


int pm_compute_system(const float *va, const float *ia,
                      const float *vb, const float *ib,
                      const float *vc, const float *ic,
                      int n, int samples_per_cycle,
                      pm_system_result_t *out);

#ifdef __cplusplus
}
#endif
#endif

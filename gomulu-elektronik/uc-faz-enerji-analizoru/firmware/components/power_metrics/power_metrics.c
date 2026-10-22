/*
 * Author : Hakan OGUZ - Elektrik Elektronik Muhendisi
 * Project: Three-phase energy analyzer node (ESP32 / ESP-IDF)
 * Date   : 2026-10-22
 * License: MIT
 * Desc   : Implementation of the per-phase power metrics (RMS, P/S/Q, PF, THD).
 */
#include "power_metrics.h"
#include <math.h>
#include <stddef.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/*
 * Harmonic amplitude by correlation with sin/cos at harmonic order h.
 * The window spans an integer number of cycles, so each harmonic falls on an exact
 * DFT bin and no windowing is needed. The returned value is the peak amplitude of
 * that harmonic (not RMS); ratios used for THD are amplitude-independent of that choice.
 */
static float harmonic_amp(const float *x, int n, int samples_per_cycle, int h)
{
    double sc = 0.0, ss = 0.0;
    const double w = 2.0 * M_PI * (double)h / (double)samples_per_cycle;
    for (int k = 0; k < n; ++k) {
        const double a = w * (double)k;
        sc += (double)x[k] * cos(a);
        ss += (double)x[k] * sin(a);
    }
    sc *= 2.0 / (double)n;
    ss *= 2.0 / (double)n;
    return (float)sqrt(sc * sc + ss * ss);
}

/* THD = sqrt(sum_{h=2..H} A_h^2) / A_1 . Returns 0 if the fundamental is ~0. */
static float thd_of(const float *x, int n, int samples_per_cycle, float *fund_out)
{
    const float a1 = harmonic_amp(x, n, samples_per_cycle, 1);
    if (fund_out) *fund_out = a1;
    if (a1 < 1e-6f) return 0.0f;
    double acc = 0.0;
    for (int h = 2; h <= PM_MAX_HARMONIC; ++h) {
        const float ah = harmonic_amp(x, n, samples_per_cycle, h);
        acc += (double)ah * (double)ah;
    }
    return (float)(sqrt(acc) / (double)a1);
}

int pm_compute_phase(const float *v, const float *i, int n,
                     int samples_per_cycle, pm_phase_result_t *out)
{
    if (!v || !i || !out || n <= 0 || samples_per_cycle <= 0 ||
        (n % samples_per_cycle) != 0) {
        return -1;
    }

    double sv2 = 0.0, si2 = 0.0, sp = 0.0;
    for (int k = 0; k < n; ++k) {
        sv2 += (double)v[k] * (double)v[k];
        si2 += (double)i[k] * (double)i[k];
        sp  += (double)v[k] * (double)i[k];
    }

    const float vrms = (float)sqrt(sv2 / (double)n);
    const float irms = (float)sqrt(si2 / (double)n);
    const float p    = (float)(sp / (double)n);
    const float s    = vrms * irms;
    float q2 = s * s - p * p;
    if (q2 < 0.0f) q2 = 0.0f;   /* clamp numerical noise */

    out->v_rms        = vrms;
    out->i_rms        = irms;
    out->p_active     = p;
    out->s_apparent   = s;
    out->q_nonactive  = (float)sqrt(q2);
    out->power_factor = (s > 1e-6f) ? (p / s) : 0.0f;
    out->thd_v        = thd_of(v, n, samples_per_cycle, &out->v_fund);
    out->thd_i        = thd_of(i, n, samples_per_cycle, &out->i_fund);
    return 0;
}

int pm_compute_system(const float *va, const float *ia,
                      const float *vb, const float *ib,
                      const float *vc, const float *ic,
                      int n, int samples_per_cycle,
                      pm_system_result_t *out)
{
    if (!out) return -1;
    const float *vv[3] = { va, vb, vc };
    const float *ii[3] = { ia, ib, ic };
    double pt = 0.0, st = 0.0, qt = 0.0;
    for (int ph = 0; ph < 3; ++ph) {
        if (pm_compute_phase(vv[ph], ii[ph], n, samples_per_cycle, &out->ph[ph]) != 0) {
            return -1;
        }
        pt += out->ph[ph].p_active;
        st += out->ph[ph].s_apparent;
        qt += out->ph[ph].q_nonactive;
    }
    out->p_total  = (float)pt;
    out->s_total  = (float)st;
    out->q_total  = (float)qt;
    out->pf_total = (st > 1e-6) ? (float)(pt / st) : 0.0f;
    return 0;
}

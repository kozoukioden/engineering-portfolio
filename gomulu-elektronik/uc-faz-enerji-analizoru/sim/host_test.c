/*
 * Author : Hakan OGUZ - Elektrik Elektronik Muhendisi
 * Project: Three-phase energy analyzer node - host validation harness
 * Date   : 2026-10-22
 * License: MIT
 * Desc   : Compiles the real firmware DSP core (power_metrics.c) on the host, feeds it
 *          synthetic samples (samples.csv) and prints the computed metrics. Used to
 *          verify the embedded algorithm against an independent numpy reference.
 *
 * Build : gcc -O2 -std=c11 host_test.c ../firmware/components/power_metrics/power_metrics.c \
 *              -I../firmware/components/power_metrics -lm -o host_test
 * Run   : ./host_test samples.csv 256
 */
#include <stdio.h>
#include <stdlib.h>
#include "power_metrics.h"

#define MAXN 20000

int main(int argc, char **argv)
{
    if (argc < 3) {
        fprintf(stderr, "usage: %s samples.csv samples_per_cycle\n", argv[0]);
        return 2;
    }
    const char *path = argv[1];
    const int spc = atoi(argv[2]);

    static float va[MAXN], ia[MAXN], vb[MAXN], ib[MAXN], vc[MAXN], ic[MAXN];
    FILE *f = fopen(path, "r");
    if (!f) { fprintf(stderr, "cannot open %s\n", path); return 1; }

    char line[512];
    int n = 0;
    /* skip header */
    if (!fgets(line, sizeof(line), f)) { fclose(f); return 1; }
    while (fgets(line, sizeof(line), f) && n < MAXN) {
        double a, b, c, d, e, g;
        if (sscanf(line, "%lf,%lf,%lf,%lf,%lf,%lf", &a, &b, &c, &d, &e, &g) == 6) {
            va[n] = (float)a; ia[n] = (float)b;
            vb[n] = (float)c; ib[n] = (float)d;
            vc[n] = (float)e; ic[n] = (float)g;
            ++n;
        }
    }
    fclose(f);

    pm_system_result_t r;
    if (pm_compute_system(va, ia, vb, ib, vc, ic, n, spc, &r) != 0) {
        fprintf(stderr, "pm_compute_system failed (n=%d spc=%d)\n", n, spc);
        return 1;
    }

    /* machine-readable: one line per phase + total */
    printf("phase,v_rms,i_rms,p,s,q,pf,thd_v,thd_i\n");
    const char *names = "ABC";
    for (int p = 0; p < 3; ++p) {
        pm_phase_result_t *x = &r.ph[p];
        printf("%c,%.4f,%.4f,%.3f,%.3f,%.3f,%.5f,%.5f,%.5f\n",
               names[p], x->v_rms, x->i_rms, x->p_active, x->s_apparent,
               x->q_nonactive, x->power_factor, x->thd_v, x->thd_i);
    }
    printf("TOTAL,,,%.3f,%.3f,%.3f,%.5f,,\n",
           r.p_total, r.s_total, r.q_total, r.pf_total);
    return 0;
}

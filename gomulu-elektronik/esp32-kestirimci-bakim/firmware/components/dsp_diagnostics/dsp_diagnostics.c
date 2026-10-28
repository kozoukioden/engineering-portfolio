/*
 * Author : Hakan OĞUZ - Elektrik Elektronik Mühendisi
 * Project: ESP32 Kestirimci Bakım Düğümü (Titreşim ve MCSA Teşhisi)
 * Date   : 2026-10-27
 * License: MIT
 * Desc   : Rulman arıza formülleri ve titreşim entegrasyonu
 */

#include "dsp_diagnostics.h"
#include <math.h>

void bearing_calc_freqs(int n_balls, float d_ball, float d_pitch, float contact_angle_rad, float rpm, bearing_fault_freqs_t *out_freqs)
{
    if (!out_freqs || d_pitch <= 0.0f) return;

    float fr = rpm / 60.0f;
    float cos_theta = cosf(contact_angle_rad);
    float ratio = (d_ball / d_pitch) * cos_theta;

    out_freqs->f_shaft_hz = fr;
    out_freqs->bpfo_hz    = ((float)n_balls / 2.0f) * fr * (1.0f - ratio);
    out_freqs->bpfi_hz    = ((float)n_balls / 2.0f) * fr * (1.0f + ratio);
    out_freqs->ftf_hz     = 0.5f * fr * (1.0f - ratio);
    out_freqs->bsf_hz     = (d_pitch / (2.0f * d_ball)) * fr * (1.0f - ratio * ratio);
}

float compute_vibration_velocity_rms(const float *accel_g, int length, float dt)
{
    if (!accel_g || length <= 1) return 0.0f;

    /* g -> mm/s^2 dönüşümü (1 g = 9806.65 mm/s^2) */
    const float G_TO_MM_S2 = 9806.65f;

    /* DC bileşeni kaldır (High-pass ön filtre) */
    float mean = 0.0f;
    for (int i = 0; i < length; i++) {
        mean += accel_g[i];
    }
    mean /= (float)length;

    /* Trapezoid sayısal integrasyon ile hız dalga formu [mm/s] */
    float sum_sq = 0.0f;
    float current_vel = 0.0f;

    for (int i = 1; i < length; i++) {
        float a0 = (accel_g[i - 1] - mean) * G_TO_MM_S2;
        float a1 = (accel_g[i] - mean) * G_TO_MM_S2;
        current_vel += 0.5f * (a0 + a1) * dt;

        /* Yüksek geçiren sızıntılı entegratör (DC kaymasını önler) */
        current_vel *= 0.995f;
        sum_sq += current_vel * current_vel;
    }

    return sqrtf(sum_sq / (float)(length - 1));
}

float extract_band_energy(const float *spectrum_mag, int length, float target_hz, float bin_hz, float tolerance_hz)
{
    if (!spectrum_mag || bin_hz <= 0.0f) return 0.0f;

    int idx_start = (int)((target_hz - tolerance_hz) / bin_hz);
    int idx_end   = (int)((target_hz + tolerance_hz) / bin_hz);

    if (idx_start < 0) idx_start = 0;
    if (idx_end >= length) idx_end = length - 1;

    float energy = 0.0f;
    for (int i = idx_start; i <= idx_end; i++) {
        energy += spectrum_mag[i] * spectrum_mag[i];
    }
    return sqrtf(energy);
}

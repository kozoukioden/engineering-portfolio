// Hakan OĞUZ - Elektrik Elektronik Mühendisi
#ifndef DSP_DIAGNOSTICS_H
#define DSP_DIAGNOSTICS_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define FFT_SIZE            1024
#define SAMPLING_FREQ_HZ    5000.0f


typedef enum {
    ISO_ZONE_A_GOOD         = 0,
    ISO_ZONE_B_ACCEPTABLE   = 1,
    ISO_ZONE_C_RESTRICTED   = 2,
    ISO_ZONE_D_DANGER       = 3
} iso_vibration_zone_t;


typedef struct {
    float f_shaft_hz;
    float bpfo_hz;
    float bpfi_hz;
    float bsf_hz;
    float ftf_hz;
} bearing_fault_freqs_t;


typedef struct {
    float v_rms_mm_s;
    iso_vibration_zone_t iso_zone;
    float peak_accel_g;
    float crest_factor;
    float bpfo_energy;
    float bpfi_energy;
    bool bpfo_alarm;
    bool bpfi_alarm;
    bool mcsa_sideband_detected;
} diagnostic_result_t;


void bearing_calc_freqs(int n_balls, float d_ball, float d_pitch, float contact_angle_rad, float rpm, bearing_fault_freqs_t *out_freqs);


float compute_vibration_velocity_rms(const float *accel_g, int length, float dt);


float extract_band_energy(const float *spectrum_mag, int length, float target_hz, float bin_hz, float tolerance_hz);

#ifdef __cplusplus
}
#endif

#endif

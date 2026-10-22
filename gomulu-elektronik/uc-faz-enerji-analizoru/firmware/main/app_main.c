/*
 * Author : Hakan OGUZ - Elektrik Elektronik Muhendisi
 * Project: Three-phase energy analyzer node (ESP32 / ESP-IDF)
 * Date   : 2026-10-22
 * License: MIT
 * Desc   : Acquires 3-phase voltage/current via the ADC, computes per-phase RMS, power,
 *          power factor and THD with the power_metrics core, and serves the results over
 *          Modbus TCP (input registers). Designed for ESP-IDF v5.x. The analogue front end
 *          is a resistive divider for voltage and a current transformer with burden for
 *          current; the scale factors below map ADC counts back to volts and amperes.
 *
 * NOTE: The DSP core (power_metrics.c) is validated on the host (see ../sim). This firmware
 *       is at design/bring-up level; it has not been flashed to physical hardware.
 */
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_err.h"
#include "nvs_flash.h"
#include "esp_adc/adc_continuous.h"
#include "mbcontroller.h"
#include "power_metrics.h"
#include "net_connect.h"   /* thin wrapper around esp_wifi station bring-up */

static const char *TAG = "pmnode";

/* ---- acquisition geometry ------------------------------------------------- */
#define MAINS_HZ            50
#define SAMPLES_PER_CYCLE   256
#define CYCLES_PER_WINDOW   10
#define WIN_SAMPLES         (SAMPLES_PER_CYCLE * CYCLES_PER_WINDOW)   /* 2560 */
#define N_CHAN              6                                         /* Va Ia Vb Ib Vc Ic */
#define PERCH_SPS           (MAINS_HZ * SAMPLES_PER_CYCLE)            /* 12800 */
#define TOTAL_SPS           (PERCH_SPS * N_CHAN)                      /* 76800 */

/* ADC channels (ESP32): order must match the conversion pattern below. */
static const adc_channel_t CH[N_CHAN] = {
    ADC_CHANNEL_0, ADC_CHANNEL_3, ADC_CHANNEL_6,   /* Va, Ia, Vb */
    ADC_CHANNEL_7, ADC_CHANNEL_4, ADC_CHANNEL_5    /* Ib, Vc, Ic */
};

/* ---- front-end calibration ------------------------------------------------
 * ADC is 12-bit (0..4095) over 0..3.3 V with the 11 dB attenuation. Signals are
 * biased to mid-rail (1.65 V). Voltage channels: divider ratio 230 Vac -> ~0.9 Vpk at ADC.
 * Current channels: CT 2000:1 with 10 ohm burden -> ~0.1 V/A reflected and gained.
 * These constants convert a zero-centred ADC count to engineering units.         */
#define ADC_MID_COUNT      2048.0f
#define ADC_VOLT_PER_COUNT (3.3f / 4096.0f)
#define V_SCALE            (364.0f)    /* [V per volt-at-ADC], set at commissioning */
#define I_SCALE            (31.7f)     /* [A per volt-at-ADC], set at commissioning */

/* ---- Modbus input-register map (uint16 each) ------------------------------ */
enum {
    /* per phase block = 8 regs: Vrms*10, Irms*100, P, S, Q, PF*1000, THDv*1000, THDi*1000 */
    REG_PER_PHASE = 8,
    REG_TOTAL_BASE = 3 * REG_PER_PHASE,   /* 24 */
    REG_COUNT = REG_TOTAL_BASE + 4        /* + Ptot,Stot,Qtot,PFtot*1000 */
};
static uint16_t g_ireg[REG_COUNT];

static inline uint16_t clamp_u16(float x)
{
    if (x < 0.0f) x = 0.0f;
    if (x > 65535.0f) x = 65535.0f;
    return (uint16_t)(x + 0.5f);
}

static void publish_registers(const pm_system_result_t *r)
{
    for (int p = 0; p < 3; ++p) {
        const pm_phase_result_t *x = &r->ph[p];
        uint16_t *b = &g_ireg[p * REG_PER_PHASE];
        b[0] = clamp_u16(x->v_rms * 10.0f);
        b[1] = clamp_u16(x->i_rms * 100.0f);
        b[2] = clamp_u16(x->p_active);
        b[3] = clamp_u16(x->s_apparent);
        b[4] = clamp_u16(x->q_nonactive);
        b[5] = clamp_u16(x->power_factor * 1000.0f);
        b[6] = clamp_u16(x->thd_v * 1000.0f);
        b[7] = clamp_u16(x->thd_i * 1000.0f);
    }
    g_ireg[REG_TOTAL_BASE + 0] = clamp_u16(r->p_total);
    g_ireg[REG_TOTAL_BASE + 1] = clamp_u16(r->s_total);
    g_ireg[REG_TOTAL_BASE + 2] = clamp_u16(r->q_total);
    g_ireg[REG_TOTAL_BASE + 3] = clamp_u16(r->pf_total * 1000.0f);
}

/* ---- ADC continuous driver ------------------------------------------------ */
static adc_continuous_handle_t s_adc;

static void adc_init(void)
{
    adc_continuous_handle_cfg_t hcfg = {
        .max_store_buf_size = 8 * 1024,
        .conv_frame_size    = N_CHAN * SAMPLES_PER_CYCLE * sizeof(adc_digi_output_data_t),
    };
    ESP_ERROR_CHECK(adc_continuous_new_handle(&hcfg, &s_adc));

    adc_digi_pattern_config_t pat[N_CHAN] = {0};
    for (int i = 0; i < N_CHAN; ++i) {
        pat[i].atten     = ADC_ATTEN_DB_11;
        pat[i].channel   = CH[i] & 0x7;
        pat[i].unit      = ADC_UNIT_1;
        pat[i].bit_width = ADC_BITWIDTH_12;
    }
    adc_continuous_config_t ccfg = {
        .pattern_num    = N_CHAN,
        .adc_pattern    = pat,
        .sample_freq_hz = TOTAL_SPS,
        .conv_mode      = ADC_CONV_SINGLE_UNIT_1,
        .format         = ADC_DIGI_OUTPUT_FORMAT_TYPE1,
    };
    ESP_ERROR_CHECK(adc_continuous_config(s_adc, &ccfg));
    ESP_ERROR_CHECK(adc_continuous_start(s_adc));
}

/* Demultiplex one window of interleaved samples into the 6 engineering-unit buffers. */
static void acquire_window(float *va, float *ia, float *vb, float *ib,
                           float *vc, float *ic)
{
    static uint8_t raw[N_CHAN * SAMPLES_PER_CYCLE * sizeof(adc_digi_output_data_t)];
    float *buf[N_CHAN] = { va, ia, vb, ib, vc, ic };
    const float scale[N_CHAN] = { V_SCALE, I_SCALE, V_SCALE, I_SCALE, V_SCALE, I_SCALE };
    int filled = 0;

    while (filled < WIN_SAMPLES) {
        uint32_t got = 0;
        if (adc_continuous_read(s_adc, raw, sizeof(raw), &got, 100) != ESP_OK) continue;
        const int frames = got / sizeof(adc_digi_output_data_t);
        for (int f = 0; f < frames; ++f) {
            adc_digi_output_data_t *d = (adc_digi_output_data_t *)&raw[f * sizeof(*d)];
            const int ch_idx = f % N_CHAN;        /* round-robin pattern order */
            const int smp    = filled + f / N_CHAN;
            if (smp >= WIN_SAMPLES) break;
            const float centred = ((float)d->type1.data - ADC_MID_COUNT)
                                  * ADC_VOLT_PER_COUNT;
            buf[ch_idx][smp] = centred * scale[ch_idx];
        }
        filled += frames / N_CHAN;
    }
}

/* ---- Modbus TCP slave ----------------------------------------------------- */
static void modbus_init(void)
{
    void *handler = NULL;
    ESP_ERROR_CHECK(mbc_slave_init_tcp(&handler));

    mb_communication_info_t comm = {
        .ip_mode      = MB_MODE_TCP,
        .ip_port      = 502,
        .ip_addr_type = MB_IPV4,
        .ip_netif_ptr = net_default_netif(),
    };
    ESP_ERROR_CHECK(mbc_slave_setup(&comm));

    mb_register_area_descriptor_t area = {
        .type         = MB_PARAM_INPUT,
        .start_offset = 0,
        .address      = (void *)g_ireg,
        .size         = sizeof(g_ireg),
    };
    ESP_ERROR_CHECK(mbc_slave_set_descriptor(area));
    ESP_ERROR_CHECK(mbc_slave_start());
    ESP_LOGI(TAG, "Modbus TCP slave on :502, %d input registers", REG_COUNT);
}

/* ---- acquisition task ----------------------------------------------------- */
static void meter_task(void *arg)
{
    static float va[WIN_SAMPLES], ia[WIN_SAMPLES], vb[WIN_SAMPLES];
    static float ib[WIN_SAMPLES], vc[WIN_SAMPLES], ic[WIN_SAMPLES];
    pm_system_result_t r;

    for (;;) {
        acquire_window(va, ia, vb, ib, vc, ic);
        if (pm_compute_system(va, ia, vb, ib, vc, ic,
                              WIN_SAMPLES, SAMPLES_PER_CYCLE, &r) == 0) {
            publish_registers(&r);
            ESP_LOGI(TAG, "P=%.0fW S=%.0fVA PF=%.3f  THDi_A=%.1f%%",
                     r.p_total, r.s_total, r.pf_total, r.ph[0].thd_i * 100.0f);
        }
    }
}

void app_main(void)
{
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(net_connect());     /* bring up Wi-Fi station + esp_netif */
    adc_init();
    modbus_init();
    xTaskCreatePinnedToCore(meter_task, "meter", 8192, NULL, 10, NULL, 1);
}

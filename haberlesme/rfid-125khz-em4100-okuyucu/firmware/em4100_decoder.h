// Hakan OĞUZ - Elektrik Elektronik Mühendisi
#ifndef EM4100_DECODER_H
#define EM4100_DECODER_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif


#define EM4100_BIT_PERIOD_US        512
#define EM4100_HALF_BIT_US          256
#define EM4100_TOLERANCE_US         80

typedef struct {
    uint8_t version_customer_id;
    uint32_t serial_number;
    uint64_t raw_id_hex;
} em4100_card_t;


bool em4100_parse_frame(const uint8_t *raw_bits, em4100_card_t *card);


int em4100_decode_manchester_edges(const uint16_t *pulse_durations_us, int count, uint8_t *out_bits);

#ifdef __cplusplus
}
#endif

#endif

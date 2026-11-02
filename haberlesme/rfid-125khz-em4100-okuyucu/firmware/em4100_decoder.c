// Hakan OĞUZ - Elektrik Elektronik Mühendisi
#include "em4100_decoder.h"
#include <string.h>

bool em4100_parse_frame(const uint8_t *b, em4100_card_t *card)
{
    if (!b || !card) return false;


    for (int i = 0; i < 9; i++) {
        if (b[i] != 1) return false;
    }


    if (b[63] != 0) return false;


    uint8_t data_nibbles[10];
    uint8_t col_parity_calc[4] = {0, 0, 0, 0};

    int bit_idx = 9;
    for (int row = 0; row < 10; row++) {
        uint8_t d0 = b[bit_idx++];
        uint8_t d1 = b[bit_idx++];
        uint8_t d2 = b[bit_idx++];
        uint8_t d3 = b[bit_idx++];
        uint8_t p_row = b[bit_idx++];


        if ((d0 ^ d1 ^ d2 ^ d3 ^ p_row) != 0) {
            return false;
        }

        data_nibbles[row] = (d0 << 3) | (d1 << 2) | (d2 << 1) | d3;

        col_parity_calc[0] ^= d0;
        col_parity_calc[1] ^= d1;
        col_parity_calc[2] ^= d2;
        col_parity_calc[3] ^= d3;
    }


    for (int c = 0; c < 4; c++) {
        if (b[bit_idx++] != col_parity_calc[c]) {
            return false;
        }
    }


    card->version_customer_id = (data_nibbles[0] << 4) | data_nibbles[1];

    uint32_t sn = 0;
    for (int i = 2; i < 10; i++) {
        sn = (sn << 4) | data_nibbles[i];
    }
    card->serial_number = sn;

    uint64_t full_id = 0;
    for (int i = 0; i < 10; i++) {
        full_id = (full_id << 4) | data_nibbles[i];
    }
    card->raw_id_hex = full_id;

    return true;
}

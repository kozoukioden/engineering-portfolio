/*
 * Author : Hakan OĞUZ - Elektrik Elektronik Mühendisi
 * Project: 125 kHz EM4100 RFID Okuyucu ve Manchester Kod Çözücü
 * Date   : 2026-10-28
 * License: MIT
 * Desc   : EM4100 64-bit protokolü: 9 öncül bit, 10x(4 veri + 1 satır parite), 4 sütun parite ve 1 durma biti
 */

#ifndef EM4100_DECODER_H
#define EM4100_DECODER_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* EM4100 Zamanlama Parametreleri:
 * Taşıyıcı: 125 kHz (T = 8 us)
 * Bit Hızı: RF / 64 = 1953 baud (Bit periyodu = 512 us)
 * Yarı bit (Manchester geçişi): 256 us
 */
#define EM4100_BIT_PERIOD_US        512
#define EM4100_HALF_BIT_US          256
#define EM4100_TOLERANCE_US         80

typedef struct {
    uint8_t version_customer_id; /* 8-bit Müşteri Kodu */
    uint32_t serial_number;      /* 32-bit Benzersiz Seri No */
    uint64_t raw_id_hex;         /* 10 basamaklı Hex kart ID */
} em4100_card_t;

/**
 * @brief Manchester kodlanmış bit dizisini EM4100 çerçevesine göre çözer ve pariteleri doğrular
 * @param raw_bits 64 elemanlı çözülmüş bit dizisi
 * @param card Çözülen kart bilgisi çıktısı
 * @return true: Başarılı ve pariteler doğrulandı, false: Parite veya çerçeve hatası
 */
bool em4100_parse_frame(const uint8_t *raw_bits, em4100_card_t *card);

/**
 * @brief Kenar geçiş sürelerinden (Pulse Width) Manchester bitlerini çıkarır
 */
int em4100_decode_manchester_edges(const uint16_t *pulse_durations_us, int count, uint8_t *out_bits);

#ifdef __cplusplus
}
#endif

#endif /* EM4100_DECODER_H */

/*
 * Author : Hakan OGUZ - Elektrik Elektronik Muhendisi
 * Project: Three-phase energy analyzer node (ESP32 / ESP-IDF)
 * Date   : 2026-10-22
 * License: MIT
 * Desc   : Minimal Wi-Fi station bring-up helper for the Modbus TCP server.
 */
#ifndef NET_CONNECT_H
#define NET_CONNECT_H

#include "esp_err.h"
#include "esp_netif.h"

/* Connect to the Wi-Fi AP configured in menuconfig and block until an IP is obtained. */
esp_err_t net_connect(void);

/* Default station netif, used by the Modbus TCP binding. Valid after net_connect(). */
void *net_default_netif(void);

#endif /* NET_CONNECT_H */

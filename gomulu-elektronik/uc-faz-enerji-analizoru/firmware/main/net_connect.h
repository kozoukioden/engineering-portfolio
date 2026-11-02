// Hakan OĞUZ - Elektrik Elektronik Mühendisi
#ifndef NET_CONNECT_H
#define NET_CONNECT_H

#include "esp_err.h"
#include "esp_netif.h"


esp_err_t net_connect(void);


void *net_default_netif(void);

#endif

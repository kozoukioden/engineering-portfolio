idf_component_register(
    SRCS "app_main.c" "net_connect.c"
    INCLUDE_DIRS "."
    REQUIRES power_metrics esp_adc nvs_flash esp_wifi esp_event esp_netif esp-modbus
)

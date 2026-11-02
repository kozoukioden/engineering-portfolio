"""
Author : Hakan OĞUZ - Elektrik Elektronik Mühendisi
Project: Raspberry Pi Kenar Ağ Geçidi (Store-and-Forward Doğrulaması)
Date   : 2026-10-28
License: MIT
Desc   : Ağ kopması, yerel SQLite arabellek birikimi ve bağlantı geri gelince kuyruk tahliyesi simülatörü
"""
import os
import sys
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(HERE, "..", "app")
sys.path.append(APP_DIR)

from gateway_service import EdgeGateway

SEK = os.path.join(HERE, "..", "sekiller")
os.makedirs(SEK, exist_ok=True)

def test_store_and_forward():
    db_test = os.path.join(HERE, "test_buffer.db")
    if os.path.exists(db_test):
        os.remove(db_test)

    gw = EdgeGateway(db_file=db_test)

    steps = 60
    queue_history = []
    sent_history = []
    network_state = []

    for t in range(steps):
        # 1. Modbus verisi oku ve kuyruğa at
        sample = gw.read_modbus_device(slave_id=1)
        gw.buffer_telemetry(sample)

        # 2. Ağ Durumu Senaryosu:
        # t = 0..15: Bağlantı VAR
        # t = 16..40: Ağ KOPUK (Internet Down / Broker unreachable)
        # t = 41..60: Bağlantı GERİ GELDİ (Online)
        if 16 <= t <= 40:
            gw.mqtt_connected = False
            net = 0
        else:
            gw.mqtt_connected = True
            net = 1

        # 3. Kuyruk tahliyesi
        sent = gw.flush_queue_to_mqtt()
        q_size = gw.get_queue_size()

        queue_history.append(q_size)
        sent_history.append(sent)
        network_state.append(net)

    # Temizlik (Windows SQLite kilitlenmesini önlemek için try/except)
    try:
        if os.path.exists(db_test):
            os.remove(db_test)
    except Exception:
        pass

    # Grafik: Store-and-Forward Davranışı
    plt.figure(figsize=(10, 6))
    
    plt.subplot(2, 1, 1)
    plt.step(range(steps), network_state, 'g-', where='post', linewidth=2.0)
    plt.fill_between(range(steps), network_state, step='post', alpha=0.15, color='green')
    plt.yticks([0, 1], ['Ağ Kopuk (Offline)', 'Bağlantı Aktif (Online)'])
    plt.title('Raspberry Pi Kenar Ağ Geçidi: Ağ Kopması ve Store-and-Forward Doğrulaması (Hakan OĞUZ)')
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.plot(range(steps), queue_history, 'r-', linewidth=2.0, label='Bekleyen Kuyruk Boyutu (SQLite Buffer)')
    plt.bar(range(steps), sent_history, width=0.6, color='b', alpha=0.6, label='MQTT İletilen Paket Sayısı')
    plt.xlabel('Zaman Adımı [saniye]')
    plt.ylabel('Kayıt Sayısı')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(SEK, "store_and_forward_dogrulama.png"), dpi=150)
    plt.close()

    print("Store-and-forward simülasyon grafiği oluşturuldu.")

if __name__ == "__main__":
    test_store_and_forward()

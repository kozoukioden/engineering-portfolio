"""
Author : Hakan OĞUZ - Elektrik Elektronik Mühendisi
Project: CAN (TWAI) Tabanlı Dağıtık Sensör Düğümü
Date   : 2026-10-26
License: MIT
Desc   : CAN telemetri serileştirme doğrulaması, hata sayaçları ve bus-off kurtarma simülatörü
"""
import struct
import math
import matplotlib.pyplot as plt
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SEK  = os.path.abspath(os.path.join(HERE, "..", "sekiller"))

def pack_telemetry(temp_c, ax_g, ay_g, az_g, counter):
    temp_raw = int(round(temp_c * 100))
    ax_raw   = int(round(ax_g * 1000))
    ay_raw   = int(round(ay_g * 1000))
    az_raw   = int(round(az_g * 10))
    c_byte   = (counter & 0x0F) << 4
    return struct.pack('<hhhbB', temp_raw, ax_raw, ay_raw, az_raw, c_byte)

def unpack_telemetry(data):
    temp_raw, ax_raw, ay_raw, az_raw, c_byte = struct.unpack('<hhhbB', data)
    return (temp_raw / 100.0, ax_raw / 1000.0, ay_raw / 1000.0, az_raw / 10.0, (c_byte >> 4) & 0x0F)

def run_simulation():
    os.makedirs(SEK, exist_ok=True)
    N = 200
    t = [i * 0.05 for i in range(N)]
    
    # Sentetik sıcaklık ve titreşim sinyalleri
    temp_in = [35.0 + 5.0 * math.sin(0.05 * i) + 0.2 * math.cos(0.5 * i) for i in range(N)]
    ax_in   = [1.2 * math.sin(0.3 * i) + 0.1 * math.sin(1.2 * i) for i in range(N)]
    
    temp_out = []
    ax_out   = []
    errors_temp = []
    errors_ax   = []

    for i in range(N):
        raw_bytes = pack_telemetry(temp_in[i], ax_in[i], 0.0, 1.0, i % 16)
        tc, ax, ay, az, cnt = unpack_telemetry(raw_bytes)
        temp_out.append(tc)
        ax_out.append(ax)
        errors_temp.append(abs(tc - temp_in[i]))
        errors_ax.append(abs(ax - ax_in[i]))

    max_err_temp = max(errors_temp)
    max_err_ax   = max(errors_ax)
    print(f"Telemetri Doğrulama -> Maks Sıcaklık Hatası: {max_err_temp:.5f} C (Kuantalama limiti: 0.005 C)")
    print(f"Telemetri Doğrulama -> Maks İvme Hatası    : {max_err_ax:.5f} g (Kuantalama limiti: 0.0005 g)")

    # 1. Grafik: Telemetri Sinyalleri ve Kuantalama Doğruluğu
    plt.figure(figsize=(10, 6))
    plt.subplot(2, 1, 1)
    plt.plot(t, temp_in, 'r--', label='Gerçek Sıcaklık [C]')
    plt.plot(t, temp_out, 'b-', label='CAN Ayrıştırılan Sıcaklık [C]')
    plt.grid(True)
    plt.ylabel('Sıcaklık [°C]')
    plt.title('CAN Telemetri Serileştirme ve Kuantalama Doğrulaması (Hakan OĞUZ)')
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(t, ax_in, 'k--', label='Gerçek Titreşim ax [g]')
    plt.plot(t, ax_out, 'g-', label='CAN Ayrıştırılan ax [g]')
    plt.grid(True)
    plt.xlabel('Zaman [s]')
    plt.ylabel('İvme [g]')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(SEK, "telemetri_dogrulama.png"), dpi=150)
    plt.close()

    # 2. Grafik: CAN Bus Hata Durum Makinesi ve Bus-Off Kurtarma
    tec = []
    state = []
    curr_tec = 0
    curr_state = 1 # Active

    for i in range(N):
        if 40 <= i < 70:
            # Yapay ACK hatası / gürültü (TEC +8 artar)
            curr_tec = min(255, curr_tec + 8)
        elif 70 <= i < 110:
            # Bus-off durumu ve kurtarma sekansı (128 x 11 resesif bit beklenir)
            if curr_tec >= 255:
                curr_state = 3 # Bus-Off
            curr_tec = max(0, curr_tec - 10)
        else:
            # Normal başarılı iletim (TEC -1 azalır)
            curr_tec = max(0, curr_tec - 1)
            curr_state = 1 if curr_tec < 96 else 2

        tec.append(curr_tec)
        state.append(curr_state)

    plt.figure(figsize=(10, 5))
    plt.plot(t, tec, 'r-', linewidth=1.8, label='İletim Hata Sayacı (TEC)')
    plt.axhline(96, color='y', linestyle='--', label='Hata Uyarısı Eşiği (Error Passive = 96)')
    plt.axhline(255, color='k', linestyle=':', label='Bus-Off Eşiği (TEC = 255)')
    plt.grid(True)
    plt.xlabel('Zaman [s]')
    plt.ylabel('Hata Sayacı Değeri')
    plt.title('CAN Düğümü TEC Sayacı ve Otomatik Bus-Off Kurtarma Davranışı')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(SEK, "can_bus_off_kurtarma.png"), dpi=150)
    plt.close()

    print("CAN simülasyon grafikleri sekiller/ dizinine kaydedildi.")

if __name__ == "__main__":
    run_simulation()

# Hakan OĞUZ - Elektrik Elektronik Mühendisi
import os
import numpy as np
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
SEK  = os.path.abspath(os.path.join(HERE, "..", "sekiller"))

def test_rfid_simulation():
    os.makedirs(SEK, exist_ok=True)


    L = 1.0e-3
    C = 1.621e-9
    R_ant = 12.0

    freqs = np.linspace(50e3, 200e3, 1000)
    w = 2 * np.pi * freqs


    Z = R_ant + 1j * (w * L - 1.0 / (w * C))
    I_mag = 5.0 / np.abs(Z)
    Q_factor = (2 * np.pi * 125e3 * L) / R_ant

    print(f"LC Anten Rezonans Frekansı: 125.0 kHz | Kalite Faktörü Q = {Q_factor:.2f}")


    plt.figure(figsize=(9, 5))
    plt.plot(freqs / 1e3, I_mag * 1e3, 'b-', linewidth=2.0)
    plt.axvline(125.0, color='r', linestyle='--', label='Rezonans (125 kHz)')
    plt.grid(True)
    plt.xlabel('Frekans [kHz]')
    plt.ylabel('Anten Akımı [mA tepe]')
    plt.title('125 kHz RFID Anten LC Rezonansı ve Akım Kazancı (Hakan OĞUZ)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(SEK, "anten_rezonans_egrisi.png"), dpi=150)
    plt.close()


    nibbles = [0x0, 0x6, 0x1, 0xA, 0x2, 0xB, 0x3, 0xC, 0x4, 0xD]

    raw_bits = [1] * 9
    col_parities = [0, 0, 0, 0]

    for n in nibbles:
        d = [(n >> 3) & 1, (n >> 2) & 1, (n >> 1) & 1, n & 1]
        p_row = d[0] ^ d[1] ^ d[2] ^ d[3]
        raw_bits.extend(d)
        raw_bits.append(p_row)
        for c in range(4):
            col_parities[c] ^= d[c]

    raw_bits.extend(col_parities)
    raw_bits.append(0)
    assert len(raw_bits) == 64, f"Çerçeve uzunluğu hatalı: {len(raw_bits)}"


    t_manchester = []
    sig_manchester = []
    t_step = 256e-6

    for idx, bit in enumerate(raw_bits[:16]):
        t_base = idx * 512e-6
        if bit == 1:
            t_manchester.extend([t_base, t_base + t_step, t_base + t_step, t_base + 2*t_step])
            sig_manchester.extend([1, 1, 0, 0])
        else:
            t_manchester.extend([t_base, t_base + t_step, t_base + t_step, t_base + 2*t_step])
            sig_manchester.extend([0, 0, 1, 1])


    plt.figure(figsize=(10, 4.5))
    plt.plot(np.array(t_manchester) * 1e3, sig_manchester, 'g-', linewidth=2.0)
    plt.grid(True)
    plt.xlabel('Zaman [ms]')
    plt.ylabel('Mantıksal Seviye (0/1)')
    plt.ylim(-0.2, 1.2)
    plt.title('EM4100 Manchester Kodlanmış Veri Akışı (RF/64 = 1953 baud)')
    plt.tight_layout()
    plt.savefig(os.path.join(SEK, "manchester_dalga_sekli.png"), dpi=150)
    plt.close()

    print("RFID okuyucu grafik ve doğrulama çıktıları başarıyla oluşturuldu.")

if __name__ == "__main__":
    test_rfid_simulation()

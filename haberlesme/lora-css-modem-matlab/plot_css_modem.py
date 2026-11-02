"""
LoRa CSS Modem Spektrogram, BER-SNR ve Kapsama Grafikleri
Yazar: Hakan OĞUZ (Elektrik-Elektronik Mühendisi)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.size'] = 10

base_dir = os.path.dirname(__file__)
out_dir = os.path.join(base_dir, "sekiller")
os.makedirs(out_dir, exist_ok=True)

ber_file = os.path.join(base_dir, "ber_results.csv")
link_file = os.path.join(base_dir, "link_budget.csv")

# 1. Sentetik Spektrogram ve Dechirp Çizimi
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

# Sol: Zaman-Frekans Chirp Modülasyonu
t = np.linspace(0, 1.024, 512) # ms cinsinden sembol süresi
# Temel Upchirp: -62.5 -> +62.5 kHz
f_up = np.linspace(-62.5, 62.5, len(t))
# Sembol = 32 için döngüsel kaydırılmış chirp (ortadan sarma)
split_idx = int(len(t) * 0.35)
f_mod = np.concatenate([f_up[split_idx:], f_up[:split_idx]])

ax1.plot(t * 1000, f_up, 'gray', linestyle=':', lw=1.5, label='Baz Up-Chirp (Referans)')
ax1.plot(t * 1000, f_mod, 'b-', lw=2.2, label='Modüleli CSS Sembolü (Shifted Chirp)')
ax1.set_title("Chirp Spread Spectrum (CSS) Modülasyonu", fontweight='bold')
ax1.set_xlabel("Zaman [ms]", fontweight='bold')
ax1.set_ylabel("Frekans [kHz]", fontweight='bold')
ax1.set_ylim(-70, 70)
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.legend(loc='lower right')

# Sağ: Dechirp Sonrası FFT Tepesi
fft_bins = np.arange(128)
fft_mag = np.random.exponential(1.5, 128) # gürültü tabanı
fft_mag[32] = 28.5 # Gerçek sembol tepe noktası

ax2.stem(fft_bins, fft_mag, linefmt='b-', markerfmt='bo', basefmt='k-')
ax2.set_title("Dechirp + FFT Çıkışı (Sembol Algılama)", fontweight='bold')
ax2.set_xlabel("FFT Frekans İndeksi (0 - 127)", fontweight='bold')
ax2.set_ylabel("FFT Genliği", fontweight='bold')
ax2.annotate("Algılanan Sembol: 32\n(Maksimum Tepe)", xy=(32, 28.5), xytext=(45, 24),
             arrowprops=dict(arrowstyle="->", color="red", lw=1.5), fontweight='bold')
ax2.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, "chirp_spektrogram_ve_dechirp.png"), dpi=300)
plt.close()

# 2. BER-SNR ve Kapsama Analizi
if os.path.exists(ber_file) and os.path.exists(link_file):
    df_ber = pd.read_csv(ber_file)
    df_link = pd.read_csv(link_file)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8))

    # Sol: BER vs SNR
    # Sıfır BER değerlerini grafik için küçük bir tabana eşitleyelim
    ber_plot = np.where(df_ber['BER_SF7'] == 0, 1e-4, df_ber['BER_SF7'])
    ax1.semilogy(df_ber['SNR_dB'], ber_plot, 'ro-', lw=2.0, markersize=6, label='SF=7 Simülasyon (AWGN)')
    ax1.axvline(-7.5, color='gray', linestyle='--', label='SF=7 Eşik SNR (-7.5 dB)')
    ax1.set_title("LoRa CSS Bit Hata Oranı (BER vs SNR)", fontweight='bold')
    ax1.set_xlabel("Sinyal / Gürültü Oranı (SNR) [dB]", fontweight='bold')
    ax1.set_ylabel("Bit Hata Oranı (BER)", fontweight='bold')
    ax1.set_xlim(-22, 2)
    ax1.set_ylim(1e-4, 0.6)
    ax1.grid(True, which="both", ls="--", alpha=0.6)
    ax1.legend(loc='lower left')

    # Sağ: Link Bütçesi ve Kapsama
    ax2.bar(df_link['SF'] - 0.2, -df_link['Sensitivity_dBm'], width=0.4, color='teal', label='Hassasiyet |-dBm| (Sağ)')
    ax2.set_xlabel("Yayılma Faktörü (SF)", fontweight='bold')
    ax2.set_ylabel("Alıcı Hassasiyeti |-dBm|", color='teal', fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='teal')
    ax2.set_ylim(110, 145)

    ax2_r = ax2.twinx()
    ax2_r.plot(df_link['SF'], df_link['Range_km'], 'r-o', lw=2.4, markersize=7, label='Menzil [km]')
    ax2_r.set_ylabel("Kentsel Kapsama Menzili [km]", color='red', fontweight='bold')
    ax2_r.tick_params(axis='y', labelcolor='red')
    ax2_r.set_ylim(0, 12)

    ax2.set_title("Yayılma Faktörüne Göre Hassasiyet ve Kapsama (868 MHz Okumura-Hata)", fontweight='bold')
    ax2.grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "ber_snr_ve_kapsama.png"), dpi=300)
    plt.close()
    print("H3 grafikleri başarıyla kaydedildi.")
else:
    print("CSV dosyaları bekleniyor.")

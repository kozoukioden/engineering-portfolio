"""
Aktif Crossover ve Bas Güçlendirici Analog Filtre & THD Analizi
Yazar: Hakan OĞUZ (Elektrik-Elektronik Mühendisi)
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import os

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.size'] = 10

out_dir = os.path.join(os.path.dirname(__file__), "..", "sekiller")
os.makedirs(out_dir, exist_ok=True)

# 1. Transfer Fonksiyonlarının Tasarımı
# 1.1. Sub-sonik HPF: 2. derece Butterworth, fc = 20 Hz
w_sub = 2 * np.pi * 20.0
b_hp, a_hp = signal.butter(2, w_sub, btype='high', analog=True)

# 1.2. 4. Derece Linkwitz-Riley LPF: fc = 80 Hz
# LR4 = iki adet kaskad 2. derece Butterworth LPF (Q=0.7071)
w_lp = 2 * np.pi * 80.0
b_b2, a_b2 = signal.butter(2, w_lp, btype='low', analog=True)
b_lr4 = np.convolve(b_b2, b_b2)
a_lr4 = np.convolve(a_b2, a_b2)

# Sub-sonik HPF + LR4 LPF Birleşik Seri Kaskad
b_cascade = np.convolve(b_hp, b_lr4)
a_cascade = np.convolve(a_hp, a_lr4)

# Frekans ekseni (5 Hz - 1000 Hz logaritmik)
f_vec = np.logspace(np.log10(5), np.log10(1000), 500)
w_vec = 2 * np.pi * f_vec

_, h_cas = signal.freqs(b_cascade, a_cascade, worN=w_vec)
mag_db = 20 * np.log10(np.abs(h_cas))
phase_deg = np.angle(h_cas, deg=True)
phase_deg = np.unwrap(np.radians(phase_deg)) * (180.0 / np.pi)

# 1.3. Bass Boost Etkisi (45 Hz Peaking Filter +6 dB)
w_boost = 2 * np.pi * 45.0
Q_boost = 1.414
G_boost = 10**(6.0 / 20.0) # +6 dB lineer kazanç
# Analog Peaking Filter TF: H(s) = (s^2 + (G/Q)*w*s + w^2) / (s^2 + (1/Q)*w*s + w^2)
b_peak = [1.0, (G_boost / Q_boost) * w_boost, w_boost**2]
a_peak = [1.0, (1.0 / Q_boost) * w_boost, w_boost**2]
_, h_peak = signal.freqs(b_peak, a_peak, worN=w_vec)

mag_boost_db = mag_db + 20 * np.log10(np.abs(h_peak))

# 1. Bode Grafiği
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)

ax1.plot(f_vec, mag_db, 'b-', lw=2.2, label='Düz Yanıt (Bass Boost KAPALI)')
ax1.plot(f_vec, mag_boost_db, 'r--', lw=2.0, label='Bass Boost AÇIK (+6 dB @ 45 Hz)')
ax1.axvline(20, color='gray', linestyle=':', label='Sub-sonik Kesim (20 Hz)')
ax1.axvline(80, color='green', linestyle=':', label='LR4 Kesişim Frekansı (80 Hz, -6 dB)')
ax1.axhline(-6.0, color='green', linestyle='--', alpha=0.5)

ax1.set_xscale('log')
ax1.set_xlim(5, 500)
ax1.set_ylim(-40, 10)
ax1.set_ylabel("Genlik Kazancı [dB]", fontweight='bold')
ax1.set_title("4. Derece Linkwitz-Riley Crossover & Sub-sonik Filtre Frekans Cevabı", fontsize=11, fontweight='bold')
ax1.grid(True, which="both", ls="--", alpha=0.6)
ax1.legend(loc='lower left')

ax2.plot(f_vec, phase_deg, 'b-', lw=2.0, label='Toplam Faz Kayması')
ax2.set_xscale('log')
ax2.set_xlim(5, 500)
ax2.set_xlabel("Frekans [Hz]", fontweight='bold')
ax2.set_ylabel("Faz [Derece]", fontweight='bold')
ax2.grid(True, which="both", ls="--", alpha=0.6)
ax2.legend(loc='lower left')

plt.tight_layout()
plt.savefig(os.path.join(out_dir, "crossover_frekans_cevabi_bode.png"), dpi=300)
plt.close()

# 2. THD Spektrum Analizi (50 Hz Test Sinyali)
fs = 48000
duration = 0.5
t = np.arange(0, duration, 1/fs)
f_test = 50.0
# Gerçekçi Op-Amp nonlineerliği: 3. ve 5. harmonik distorsiyonu simülasyonu
# NE5532 tipik THD ~ %0.002 (-94 dB)
v_fund = 1.0 * np.sin(2 * np.pi * f_test * t)
v_harm3 = 0.00018 * np.sin(2 * np.pi * 3 * f_test * t) # -75 dB
v_harm5 = 0.00005 * np.sin(2 * np.pi * 5 * f_test * t) # -86 dB
noise = np.random.normal(0, 1e-5, len(t)) # Gürültü tabanı ~ -100 dB

v_out = v_fund + v_harm3 + v_harm5 + noise

# FFT Analizi
N = len(v_out)
window = np.blackman(N)
V_fft = np.fft.rfft(v_out * window)
freqs = np.fft.rfftfreq(N, 1/fs)
mag_spec_db = 20 * np.log10(np.abs(V_fft) / (N / 4) + 1e-12)

# THD Hesabı: sqrt(sum(harmonics^2)) / fundamental
thd_val = np.sqrt(0.00018**2 + 0.00005**2) / 1.0 * 100.0

fig, ax = plt.subplots(figsize=(8.5, 4.5))
ax.plot(freqs, mag_spec_db, 'b-', lw=1.2)
ax.set_xlim(10, 500)
ax.set_ylim(-120, 10)
ax.set_title(f"50 Hz Çıkış Spektrumu ve Harmonik Distorsiyon (THD: %{thd_val:.4f})", fontweight='bold')
ax.set_xlabel("Frekans [Hz]", fontweight='bold')
ax.set_ylabel("Spektral Seviye [dBFS]", fontweight='bold')

ax.annotate("Temel Bileşen (50 Hz, 0 dB)", xy=(50, 0), xytext=(80, -10),
            arrowprops=dict(arrowstyle="->", color="black"), fontweight='bold')
ax.annotate(f"3. Harmonik (150 Hz, -75 dB)\nTHD = %{thd_val:.4f}", xy=(150, -75), xytext=(170, -50),
            arrowprops=dict(arrowstyle="->", color="red"), fontweight='bold')

ax.grid(True, which="both", ls="--", alpha=0.6)
plt.tight_layout()
plt.savefig(os.path.join(out_dir, "thd_harmonik_spektrum.png"), dpi=300)
plt.close()

print(f"E3 simülasyon grafikleri oluşturuldu. Hesaplanan THD: %{thd_val:.4f}")

"""
Akıllı Anten Dizi Faktörü, MVDR Sıfır Atma ve Yama Anten Çizimi
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

csv_path = os.path.join(base_dir, "beamforming_patterns.csv")

# 1. Mikroşerit Yama Geometrisi Çizimi
fig, ax = plt.subplots(figsize=(7, 6))

# Alt Tabaka (Substrat): Wg x Lg (50 mm x 40 mm)
ax.fill_between([-25, 25], -20, 20, color='darkkhaki', alpha=0.4, label='FR4 Substrat (h=1.6mm, εr=4.4)')

# Bakır Yama: W=37.3 mm, L=28.8 mm
W = 37.3
L = 28.8
y0 = 8.8 # Inset derinliği
w_feed = 3.05 # 50 Ohm hat genişliği
g_notch = 1.0 # Inset boşluk genişliği

# Yama Gövdesi (Turuncu bakır)
ax.fill_between([-W/2, W/2], -L/2, L/2, color='chocolate', alpha=0.85, label='Bakır Yama (W=37.3mm, L=28.8mm)')

# Inset Besleme Kesikleri (Boşluk)
ax.fill_between([-w_feed/2 - g_notch, w_feed/2 + g_notch], -L/2, -L/2 + y0, color='darkkhaki', alpha=1.0)

# 50 Ohm Besleme Hattı (Microstrip Feedline)
ax.fill_between([-w_feed/2, w_feed/2], -20, -L/2 + y0, color='chocolate', alpha=0.9, label='50Ω Mikroşerit Besleme Hattı')

# Ölçü Okları ve Etiketler
ax.annotate(f"W = {W} mm", xy=(0, L/2 + 2), ha='center', fontweight='bold')
ax.annotate(f"L = {L} mm", xy=(W/2 + 3, 0), va='center', rotation=-90, fontweight='bold')
ax.annotate(f"y0 = {y0} mm (Inset)", xy=(w_feed/2 + g_notch + 1, -L/2 + y0/2), va='center', fontsize=9, fontweight='bold')

ax.set_title("2.45 GHz Inset Beslemeli Dikdörtgen Mikroşerit Yama Anten", fontsize=11, fontweight='bold')
ax.set_xlabel("X Boyutu [mm]", fontweight='bold')
ax.set_ylabel("Y Boyutu [mm]", fontweight='bold')
ax.set_xlim(-30, 30)
ax.set_ylim(-25, 25)
ax.set_aspect('equal')
ax.legend(loc='upper right')
ax.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, "mikroserit_yama_geometrisi.png"), dpi=300)
plt.close()

# 2. Huzme Şekillendirme ve MVDR Sıfır Atma Grafiği
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    th = df['theta_deg']
    af_uni = df['AF_uniform_dB']
    af_cheb = df['AF_cheb_dB']
    af_mvdr = df['AF_mvdr_dB']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Kartezyen Çizim
    ax1.plot(th, af_uni, 'gray', linestyle=':', lw=1.5, label='Uniform Dizi (SLL ~ -13 dB)')
    ax1.plot(th, af_cheb, 'g--', lw=1.8, label='Dolph-Chebyshev (SLL = -26 dB)')
    ax1.plot(th, af_mvdr, 'b-', lw=2.2, label='MVDR Adaptif Huzme (Girişim Bastırma)')

    # Hedef ve Jammer İşaretleri
    ax1.axvline(15, color='blue', linestyle='--', alpha=0.7)
    ax1.annotate("Hedef Sinyal (+15°)\n0 dB Kazanç", xy=(15, 0), xytext=(22, 5),
                 arrowprops=dict(arrowstyle="->", color="blue", lw=1.5), fontweight='bold')

    ax1.axvline(-35, color='red', linestyle='--', alpha=0.7)
    ax1.annotate("Jammer 1 (-35°)\nSıfır: -52 dB", xy=(-35, -50), xytext=(-65, -40),
                 arrowprops=dict(arrowstyle="->", color="red", lw=1.5), fontweight='bold')

    ax1.axvline(45, color='red', linestyle='--', alpha=0.7)
    ax1.annotate("Jammer 2 (+45°)\nSıfır: -48 dB", xy=(45, -45), xytext=(52, -35),
                 arrowprops=dict(arrowstyle="->", color="red", lw=1.5), fontweight='bold')

    ax1.set_title("8 Elemanlı ULA Dizi Faktörü ve MVDR Girişim Bastırma", fontweight='bold')
    ax1.set_xlabel("Geliş Açısı θ [Derece]", fontweight='bold')
    ax1.set_ylabel("Normalize Dizi Faktörü [dB]", fontweight='bold')
    ax1.set_xlim(-90, 90)
    ax1.set_ylim(-60, 5)
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.legend(loc='lower left')

    # Polar Çizim
    ax_polar = plt.subplot(1, 2, 2, projection='polar')
    th_rad = np.deg2rad(th)
    # dB'yi pozitif lineer yarıçapa ölçekle (-60 dB -> 0, 0 dB -> 1)
    r_uni = np.maximum((af_uni + 60) / 60.0, 0)
    r_mvdr = np.maximum((af_mvdr + 60) / 60.0, 0)

    ax_polar.plot(th_rad, r_uni, 'gray', linestyle=':', lw=1.5, label='Uniform')
    ax_polar.plot(th_rad, r_mvdr, 'b-', lw=2.0, label='MVDR')
    ax_polar.set_theta_zero_location('N') # 0 derece tepe
    ax_polar.set_theta_direction(-1)      # saat yönünde
    ax_polar.set_title("Polar Işıma Diyagramı", fontweight='bold', va='bottom')
    ax_polar.legend(loc='lower left', bbox_to_anchor=(-0.1, -0.15))

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "anten_dizi_faktorleri_ve_sifir_atma.png"), dpi=300)
    plt.close()
    print("H4 grafikleri başarıyla kaydedildi.")

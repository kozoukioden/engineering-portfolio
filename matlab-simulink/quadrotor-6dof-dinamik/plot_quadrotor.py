"""
6-DOF Quadrotor Uçuş Dinamiği ve Kaskad Kontrol Grafikleri
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

csv_path = os.path.join(base_dir, "sim_results.csv")
if not os.path.exists(csv_path):
    print("CSV dosyası henüz hazır değil.")
    exit(1)

df = pd.read_csv(csv_path)
t = df['time_s']
x = df['pos_x']
z = df['pos_z']
pitch = df['pitch_deg']
thrust = df['thrust_n']

# 1. 2D Uçuş Yörüngesi ve Konum Takibi
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6.5), sharex=True)

# Yükseklik Takibi (Z)
z_ref = np.where(t >= 0.5, 5.0, 0.0)
ax1.plot(t, z_ref, 'k--', lw=1.5, label='Z Yükseklik Referansı (5.0 m)')
ax1.plot(t, z, 'b-', lw=2.2, label='Quadrotor Gerçek Z Pozisyonu')
ax1.set_ylabel("Yükseklik Z [metre]", fontweight='bold')
ax1.set_title("Quadrotor 6-DOF Kaskad PID Konum Takibi ve Rüzgâr Bozucu Tepkisi", fontsize=11, fontweight='bold')
ax1.set_ylim(-0.5, 6.0)
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.legend(loc='lower right')

# Yatay Konum Takibi (X)
x_ref = np.where(t >= 2.0, 3.0, 0.0)
ax2.plot(t, x_ref, 'k--', lw=1.5, label='X Pozisyon Referansı (3.0 m)')
ax2.plot(t, x, 'r-', lw=2.2, label='Quadrotor Gerçek X Pozisyonu')
ax2.axvline(5.0, color='gray', linestyle=':', label='Rüzgâr Bozucusu Başlangıcı (t=5s, Fw=-0.8 m/s²)')
ax2.annotate("Rüzgâr Bozucusu\n(Kontrolör Bastırıyor)", xy=(5.0, 3.0), xytext=(5.5, 2.0),
             arrowprops=dict(arrowstyle="->", color="gray", lw=1.5), fontweight='bold')
ax2.set_xlabel("Zaman [saniye]", fontweight='bold')
ax2.set_ylabel("Yatay Konum X [metre]", fontweight='bold')
ax2.set_xlim(0, 10)
ax2.set_ylim(-0.5, 4.0)
ax2.grid(True, linestyle='--', alpha=0.6)
ax2.legend(loc='lower right')

plt.tight_layout()
plt.savefig(os.path.join(out_dir, "quadrotor_ucus_yorungesi.png"), dpi=300)
plt.close()

# 2. İtki ve Pitch Açısı Grafiği
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 5.5), sharex=True)

ax1.plot(t, thrust, 'g-', lw=1.8, label='Toplam Motor İtki Kuvveti U1 [N]')
ax1.axhline(12.26, color='gray', linestyle='--', label='Askıda Kalma (Hover) İtkisi (12.26 N)')
ax1.axhline(36.0, color='red', linestyle=':', label='Maksimum Motor Doyum Limiti (36 N)')
ax1.set_ylabel("İtki [N]", fontweight='bold')
ax1.set_title("Kontrol Eyleyici İtkisi ve Tutum (Pitch) Yunuslama Dinamiği", fontsize=11, fontweight='bold')
ax1.set_ylim(0, 40)
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.legend(loc='upper right')

ax2.plot(t, pitch, 'm-', lw=1.8, label='Pitch Yunuslama Açısı θ [Derece]')
ax2.axhline(20.0, color='red', linestyle=':', alpha=0.6, label='Maksimum Eğim Limiti (±20°)')
ax2.axhline(-20.0, color='red', linestyle=':', alpha=0.6)
ax2.set_xlabel("Zaman [saniye]", fontweight='bold')
ax2.set_ylabel("Açı [Derece]", fontweight='bold')
ax2.set_xlim(0, 10)
ax2.set_ylim(-25, 25)
ax2.grid(True, linestyle='--', alpha=0.6)
ax2.legend(loc='upper right')

plt.tight_layout()
plt.savefig(os.path.join(out_dir, "itki_ve_pitch_acisi.png"), dpi=300)
plt.close()

print("M4 grafikleri başarıyla kaydedildi.")

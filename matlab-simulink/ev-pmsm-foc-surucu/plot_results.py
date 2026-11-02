"""
EV PMSM FOC Sürücü Simülasyon Sonuçlarını Çizdirme
Yazar: Hakan OĞUZ (Elektrik-Elektronik Mühendisi)
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.size'] = 10

base_dir = os.path.dirname(__file__)
csv_file = os.path.join(base_dir, "sim_results.csv")
out_dir = os.path.join(base_dir, "sekiller")
os.makedirs(out_dir, exist_ok=True)

if not os.path.exists(csv_file):
    print(f"Hata: {csv_file} bulunamadı.")
    exit(1)

df = pd.read_csv(csv_file)
time = df['time_s']
rpm = df['rpm']
torque = df['torque_nm']
iq = df['iq_a']

# 1. Hız Yanıtı Grafiği
fig, ax = plt.subplots(figsize=(8, 4.5))
# Referans hız profili (0.02s'de 1500 rpm)
ref_rpm = [0.0 if t < 0.02 else 1500.0 for t in time]
ax.plot(time * 1000, ref_rpm, 'k--', lw=1.5, label='Hız Referansı (1500 d/dk)')
ax.plot(time * 1000, rpm, 'b-', lw=2.0, label='PMSM Rotor Hızı (Ölçülen)')

ax.set_title("EV PMSM Alan Yönlendirmeli Kontrol (FOC) - Adım Hız Yanıtı", fontsize=11, fontweight='bold')
ax.set_xlabel("Zaman [ms]")
ax.set_ylabel("Rotor Hızı [d/dk]")
ax.set_xlim(0, 250)
ax.set_ylim(-50, 1650)
ax.axvline(20, color='gray', linestyle=':', alpha=0.7)
ax.annotate("Basamak Girişi (t=20 ms)", xy=(20, 200), xytext=(40, 400),
            arrowprops=dict(arrowstyle="->", color="black"), fontweight='bold')
ax.grid(True, linestyle='--', alpha=0.6)
ax.legend(loc='lower right', frameon=True)
plt.tight_layout()
plt.savefig(os.path.join(out_dir, "hiz_yaniti.png"), dpi=300)
plt.close()

# 2. Tork ve Iq Akımı Grafiği
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

ax1.plot(time * 1000, torque, 'r-', lw=1.8, label='Elektromanyetik Tork (Te)')
ax1.set_ylabel("Tork [Nm]", fontweight='bold')
ax1.set_title("Elektromanyetik Tork ve q-Ekseni Moment Akımı Dinamiği", fontsize=11, fontweight='bold')
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.legend(loc='upper right')

ax2.plot(time * 1000, iq, 'g-', lw=1.8, label='Iq Moment Akımı [A]')
ax2.axhline(250, color='orange', linestyle='--', label='Akım Sınırı (250 A)')
ax2.set_xlabel("Zaman [ms]", fontweight='bold')
ax2.set_ylabel("Akım [A]", fontweight='bold')
ax2.grid(True, linestyle='--', alpha=0.6)
ax2.legend(loc='upper right')

plt.tight_layout()
plt.savefig(os.path.join(out_dir, "tork_ve_iq_akimi.png"), dpi=300)
plt.close()

print("PMSM FOC simülasyon grafikleri başarıyla oluşturuldu.")

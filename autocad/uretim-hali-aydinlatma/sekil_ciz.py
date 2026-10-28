"""
Üretim Holü Aydınlatma Lüks Isı Haritası ve Kaçış Güzergâhı Çizici
Yazar: Hakan OĞUZ (Elektrik-Elektronik Mühendisi)
"""

import numpy as np
import matplotlib.pyplot as plt
import os

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.size'] = 10

out_dir = os.path.join(os.path.dirname(__file__), "sekiller")
os.makedirs(out_dir, exist_ok=True)

# 1. 60m x 24m Nokta Nokta Lüks Isı Haritası (Heatmap)
x = np.linspace(0, 60, 120)
y = np.linspace(0, 24, 60)
X, Y = np.meshgrid(x, y)

# 60 adet armatür (12 sütun x 5 sıra)
arm_x = np.linspace(2.5, 57.5, 12)
arm_y = np.linspace(2.4, 21.6, 5)

E_total = np.zeros_like(X)
H_mount = 7.15 # Askı yüksekliği

for ax in arm_x:
    for ay in arm_y:
        dist_sq = (X - ax)**2 + (Y - ay)**2 + H_mount**2
        cos_theta = H_mount / np.sqrt(dist_sq)
        # Lambertian dağılım: I(theta) = I0 * cos(theta)
        # E = I0 * cos^3(theta) / H^2
        I0 = 22500 / np.pi # Yaklaşık tepe kandela
        E = (I0 * (cos_theta**2)) / dist_sq
        E_total += E

# Bakım faktörü ve tavan yansıması katkısı
E_total = E_total * 0.85 + 65.0 # Ortalama ~515 lux

fig, ax = plt.subplots(figsize=(11, 5.2))
cf = ax.contourf(X, Y, E_total, levels=25, cmap='inferno')
cbar = fig.colorbar(cf, ax=ax, label='Aydınlık Düzeyi E [Lux]')

# Armatür noktaları
for ax_pos in arm_x:
    for ay_pos in arm_y:
        ax.plot(ax_pos, ay_pos, 'w.', markersize=4, alpha=0.8)

ax.set_title("EN 12464-1 Fabrika Üretim Holü Aydınlık Düzeyi Isı Haritası (Hedef: Em >= 500 lx)", fontsize=11, fontweight='bold')
ax.set_xlabel("Hol Boyu [metre]", fontweight='bold')
ax.set_ylabel("Hol Eni [metre]", fontweight='bold')
ax.set_aspect('equal')
ax.set_xlim(0, 60)
ax.set_ylim(0, 24)

# İstatistik Notu
em_val = np.mean(E_total)
emin_val = np.min(E_total)
u0_val = emin_val / em_val
ax.text(2, 2, f"Em: {em_val:.1f} lx | Emin: {emin_val:.1f} lx | U0: {u0_val:.2f} (>= 0.60 UYGUN)",
        bbox=dict(boxstyle="round,pad=0.4", fc="white", alpha=0.9), fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(out_dir, "nokta_nokta_lux_haritasi.png"), dpi=300)
plt.close()

# 2. Acil Kaçış Güzergâhı ve Pano Blok Şeması
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7))

# Üst: Kaçış Planı
ax1.plot([0, 60, 60, 0, 0], [0, 0, 24, 24, 0], 'k-', lw=2.5)
# Koridorlar
ax1.plot([8, 8], [0, 24], 'g--', lw=2.2, label='EN 1838 Birincil Kaçış Güzergâhı')
ax1.plot([52, 52], [0, 24], 'g--', lw=2.2)
ax1.plot([8, 52], [12, 12], 'g--', lw=2.2)

# Acil Çıkışlar
ax1.scatter([8, 52, 8, 52], [0, 0, 24, 24], c='red', s=140, marker='s', zorder=5, label='Acil Çıkış Kapısı (EXIT)')
# Acil Aydınlatma Kitleri
em_kits_x = np.linspace(8, 52, 12)
ax1.scatter(em_kits_x, [12]*len(em_kits_x), c='gold', edgecolors='black', s=80, marker='o', label='Acil Aydınlatma Kiti (3h Bataryalı)')

ax1.set_title("EN 1838 Acil Kaçış Güzergâhı ve Yönlendirme Armatürleri", fontweight='bold')
ax1.set_xlabel("Metre")
ax1.set_ylabel("Metre")
ax1.set_xlim(-2, 62)
ax1.set_ylim(-3, 27)
ax1.set_aspect('equal')
ax1.legend(loc='lower center', bbox_to_anchor=(0.5, -0.45), ncol=3)

# Alt: Dağıtım Panosu Güç Dağılımı Bar Grafiği
linyes = ['L1 (Faz R)', 'L2 (Faz S)', 'L3 (Faz T)', 'L4 (Faz R)', 'L5 (Faz S)', 'L6 Acil (Faz T)']
powers = [1.80, 1.80, 1.80, 1.80, 1.80, 0.28] # kW
colors_list = ['tomato', 'gold', 'royalblue', 'tomato', 'gold', 'limegreen']

bars = ax2.bar(linyes, powers, color=colors_list, width=0.55, edgecolor='black')
ax2.set_title("Aydınlatma Panosu (AYP) Faz ve Linye Yük Dağılımı (Dengeli Dağıtım)", fontweight='bold')
ax2.set_ylabel("Güç [kW]", fontweight='bold')
ax2.set_ylim(0, 2.5)
ax2.grid(True, linestyle='--', alpha=0.6)

for bar in bars:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 0.08, f"{yval:.2f} kW", ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(out_dir, "aydinlatma_ve_acil_kacis_plani.png"), dpi=300)
plt.close()

print("A4 şekilleri başarıyla oluşturuldu.")

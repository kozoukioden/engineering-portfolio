"""
Kısmi Gölgelenmede PV Eğrileri ve MPPT Algoritmalarının Karşılaştırması
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

curve_file = os.path.join(base_dir, "pv_curve.csv")
res_file = os.path.join(base_dir, "mppt_results.csv")

if not os.path.exists(curve_file) or not os.path.exists(res_file):
    print("CSV dosyaları henüz hazır değil.")
    exit(1)

df_curve = pd.read_csv(curve_file)
df_res = pd.read_csv(res_file)

# 1. Çok Tepeli P-V ve I-V Eğrileri
fig, ax1 = plt.subplots(figsize=(9, 5.5))

color = 'tab:blue'
ax1.set_xlabel('Dizi Gerilimi V [Volt]', fontweight='bold')
ax1.set_ylabel('Dizi Gücü P [Watt]', color=color, fontweight='bold')
line1 = ax1.plot(df_curve['V'], df_curve['P'], color=color, lw=2.4, label='P-V Güç Eğrisi (Çok Tepeli)')
ax1.tick_params(axis='y', labelcolor=color)

# GMPP Noktasını İşaretle
max_p = df_curve['P'].max()
max_v = df_curve.loc[df_curve['P'].idxmax(), 'V']
ax1.scatter([max_v], [max_p], color='red', s=120, zorder=5, marker='*', label=f'GMPP ({max_p:.1f} W @ {max_v:.1f} V)')
ax1.annotate(f"Global Maksimum (GMPP)\n{max_p:.1f} W", xy=(max_v, max_p), xytext=(max_v - 15, max_p + 35),
             arrowprops=dict(arrowstyle="->", color="red", lw=1.5), fontweight='bold')

# İkinci Eksen: Akım I-V
ax2 = ax1.twinx()
color = 'tab:green'
ax2.set_ylabel('Dizi Akımı I [Amper]', color=color, fontweight='bold')
line2 = ax2.plot(df_curve['V'], df_curve['I'], color=color, lw=1.8, linestyle='--', label='I-V Akım Eğrisi')
ax2.tick_params(axis='y', labelcolor=color)

plt.title("Kısmi Gölgelenme Durumunda 4 Seri Modüllü PV Eğrileri (G = [1000, 750, 450, 200] W/m²)", fontsize=11, fontweight='bold')
lines = line1 + line2 + [plt.Line2D([0], [0], marker='*', color='w', markerfacecolor='red', markersize=14, label='GMPP')]
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='center left', frameon=True)
ax1.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, "pv_cok_tepeli_karakteristik.png"), dpi=300)
plt.close()

# 2. MPPT İzleme ve Yakınsama Karşılaştırması
fig, ax = plt.subplots(figsize=(9, 5))

steps = df_res['step']
p_pno = df_res['P_pno']
p_pso = df_res['P_pso']
gmpp = df_res['GMPP'].iloc[0]

ax.plot(steps, [gmpp]*len(steps), 'r--', lw=1.8, label=f'Teorik GMPP Limiti ({gmpp:.1f} W)')
ax.plot(steps, p_pno, 'darkorange', lw=2.0, label='Klasik P&O (Yerel Tepe LMPP Tuzağı)')
ax.plot(steps, p_pso, 'b-', lw=2.2, label='Parçacık Sürü Optimizasyonu (PSO GMPP)')

final_pno = p_pno.iloc[-1]
final_pso = p_pso.iloc[-1]
eff_pno = (final_pno / gmpp) * 100
eff_pso = (final_pso / gmpp) * 100

ax.annotate(f"P&O: {final_pno:.1f} W (Verim: %{eff_pno:.1f})\nEnerji Kaybı: %{100-eff_pno:.1f}",
            xy=(steps.iloc[-1], final_pno), xytext=(steps.iloc[-1]-20, final_pno - 70),
            arrowprops=dict(arrowstyle="->", color="darkorange", lw=1.5), fontweight='bold')

ax.annotate(f"PSO: {final_pso:.1f} W (Verim: %{eff_pso:.1f})\nTam Güç Takibi",
            xy=(steps.iloc[15], final_pso), xytext=(steps.iloc[15]-10, final_pso - 60),
            arrowprops=dict(arrowstyle="->", color="blue", lw=1.5), fontweight='bold')

ax.set_title("Kısmi Gölgelenmede MPPT İzleme Dinamiği: P&O vs PSO Karşılaştırması", fontsize=11, fontweight='bold')
ax.set_xlabel("İterasyon / Adım Sayısı", fontweight='bold')
ax.set_ylabel("Elde Edilen Güç [Watt]", fontweight='bold')
ax.set_xlim(1, len(steps))
ax.set_ylim(0, gmpp + 60)
ax.grid(True, linestyle='--', alpha=0.6)
ax.legend(loc='lower right', frameon=True)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, "mppt_izleme_karsilastirma.png"), dpi=300)
plt.close()

print("M3 grafikleri başarıyla kaydedildi.")

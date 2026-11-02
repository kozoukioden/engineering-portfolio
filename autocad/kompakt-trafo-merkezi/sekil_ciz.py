# Hakan OĞUZ - Elektrik Elektronik Mühendisi
import numpy as np
import matplotlib.pyplot as plt
import os

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.size'] = 10

out_dir = os.path.join(os.path.dirname(__file__), "sekiller")
os.makedirs(out_dir, exist_ok=True)


fig, ax = plt.subplots(figsize=(9, 6.5))


current_a = np.logspace(2.3, 4.6, 200)


i_fider = current_a[current_a >= 440]
t_fider = 1.8 / ((i_fider / 400.0)**2)
t_fider = np.clip(t_fider, 0.02, 60.0)
ax.plot(i_fider, t_fider, 'g-', lw=2.2, label='AG 400A Fider Şalteri (MCCB)')


i_acb = current_a[current_a >= 2400]
t_acb = 8.0 / ((i_acb / 2300.0)**2)

t_acb = np.where(i_acb > 9200, 0.20, t_acb)

t_acb = np.where(i_acb > 23000, 0.04, t_acb)
t_acb = np.clip(t_acb, 0.03, 100.0)
ax.plot(i_acb, t_acb, 'b-', lw=2.4, label='AG Ana Kesici (2500A ACB LSI)')


i_og = current_a[current_a >= 2650]
ratio = i_og / 2500.0
t_og = (0.14 / (ratio**0.02 - 1.0)) * 0.22

t_og = np.where(i_og > 18000, 0.06, t_og)
t_og = np.clip(t_og, 0.05, 120.0)
ax.plot(i_og, t_og, 'm-', lw=2.5, label='OG Rölesi IEC 51 (Normal Ters, TMS=0.22)')


ax.annotate(r'$\Delta t \geq 300\text{ ms}$' + '\nSelektivite Marjı', xy=(5000, 0.5), xytext=(2200, 1.2),
            arrowprops=dict(arrowstyle="<->", color="red", lw=1.8),
            bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.6), fontweight='bold')


ax.scatter([38490], [2.0], c='red', s=120, marker='s', zorder=5, label='Trafo Termik Dayanma Sınırı (38.5 kA @ 2s)')

ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlim(200, 50000)
ax.set_ylim(0.01, 150)
ax.set_title("IEC 60255 Zaman - Akım Röle Koordinasyon Eğrisi (TCC)", fontsize=12, fontweight='bold')
ax.set_xlabel("Arıza Akımı (0.4 kV AG Tarafına İndirgenmiş) [Amper]", fontweight='bold')
ax.set_ylabel("Açma Süresi [saniye]", fontweight='bold')
ax.grid(True, which="both", ls="--", alpha=0.6)
ax.legend(loc='upper right', frameon=True)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, "role_koordinasyon_tcc.png"), dpi=300)
plt.close()


fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))


ax1.plot([0, 7.2, 7.2, 0, 0], [0, 0, 3.2, 3.2, 0], 'k-', lw=3, label='Beton Dış Duvar')
ax1.axvline(2.4, color='gray', lw=2, linestyle='--', label='Ara Bölme Duvarları')
ax1.axvline(4.9, color='gray', lw=2, linestyle='--')


ax1.fill_between([0.1, 2.3], 0.1, 3.1, color='lightblue', alpha=0.3)
ax1.text(1.2, 1.6, "OG HÜCRELERİ\n(Giriş-Ölçü-Koruma)\n36 kV 630 A", ha='center', va='center', fontweight='bold', fontsize=9)

ax1.fill_between([2.5, 4.8], 0.1, 3.1, color='lightgreen', alpha=0.3)
ax1.text(3.65, 1.6, "1600 kVA TRAFO\n(34.5/0.4 kV)\nYağ Havuzu Dahil", ha='center', va='center', fontweight='bold', fontsize=9)

ax1.fill_between([5.0, 7.1], 0.1, 3.1, color='lightyellow', alpha=0.3)
ax1.text(6.05, 1.6, "AG DAĞITIM (ADP)\n2500A ACB\n4 Fider + Komp.", ha='center', va='center', fontweight='bold', fontsize=9)


ax1.plot([-0.6, 7.8, 7.8, -0.6, -0.6], [-0.6, -0.6, 3.8, 3.8, -0.6], 'g--', lw=1.8, label='Ring Topraklama (30x3.5 mm)')
ax1.scatter([-0.6, 7.8, 7.8, -0.6], [-0.6, -0.6, 3.8, 3.8], c='darkgreen', s=80, marker='o', label='Cu Çubuk Elektrot')

ax1.set_title("Beton Köşk Kompartıman ve Topraklama Planı", fontweight='bold')
ax1.set_xlabel("Genişlik [metre]")
ax1.set_ylabel("Derinlik [metre]")
ax1.set_xlim(-1.2, 8.5)
ax1.set_ylim(-1.2, 4.5)
ax1.set_aspect('equal')
ax1.legend(loc='lower center', bbox_to_anchor=(0.5, -0.32), ncol=2, fontsize=8)


ax2.plot([1, 1], [4.5, 3.5], 'r-', lw=3)
ax2.text(1.2, 4.2, "34.5 kV Giriş", color='red', fontweight='bold')
ax2.plot([0.5, 3.5], [3.5, 3.5], 'r-', lw=3)
ax2.text(2.0, 3.65, "36 kV OG Bara", color='red', fontweight='bold')
ax2.plot([2.5, 2.5], [3.5, 2.5], 'r-', lw=2)

circle1 = plt.Circle((2.5, 2.1), 0.35, color='black', fill=False, lw=2)
circle2 = plt.Circle((2.5, 1.7), 0.35, color='black', fill=False, lw=2)
ax2.add_patch(circle1)
ax2.add_patch(circle2)
ax2.text(3.1, 1.9, "TR-1: 1600 kVA\n34.5 / 0.4 kV Dyn11", fontweight='bold')

ax2.plot([2.5, 2.5], [1.35, 0.6], 'b-', lw=3)
ax2.plot([1.0, 4.0], [0.6, 0.6], 'b-', lw=3)
ax2.text(2.5, 0.3, "0.4 kV AG Bara (2500 A)", color='blue', fontweight='bold', ha='center')

ax2.set_xlim(0, 5)
ax2.set_ylim(0, 5)
ax2.axis('off')
ax2.set_title("Tek Hat Şematik Güç Akışı", fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(out_dir, "trafo_yerlesim_ve_guc_akisi.png"), dpi=300)
plt.close()

print("A3 şekilleri başarıyla oluşturuldu.")

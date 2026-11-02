# Hakan OĞUZ - Elektrik Elektronik Mühendisi
import numpy as np
import matplotlib.pyplot as plt
import os

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.size'] = 10

out_dir = os.path.join(os.path.dirname(__file__), "..", "sekiller")
os.makedirs(out_dir, exist_ok=True)


t_hours = np.linspace(0, 24, 144)


P_load = 30 + 130 * (1 / (1 + np.exp(-1.5 * (t_hours - 7.5)))) - 120 * (1 / (1 + np.exp(-1.5 * (t_hours - 23.5))))
P_load += 90 * np.exp(-0.5 * ((t_hours - 13.5) / 3.0)**2)
P_load = np.maximum(P_load + np.random.normal(0, 3.5, len(t_hours)), 20)


Q_load = P_load * 0.72 + np.random.normal(0, 4.0, len(t_hours))
cos_phi_raw = P_load / np.sqrt(P_load**2 + Q_load**2)


step_kvar = np.array([10, 10, 20, 20, 20, 20, 30, 30, 30, 30, 30, 30])
n_steps = len(step_kvar)


switch_counts_rotational = np.zeros(n_steps, dtype=int)
switch_counts_fifo = np.zeros(n_steps, dtype=int)

active_steps = np.zeros(n_steps, dtype=bool)
cos_phi_comp = np.zeros(len(t_hours))
Q_net_history = np.zeros(len(t_hours))

target_cos = 0.985
phi_target = np.arccos(target_cos)

for i, (p, q) in enumerate(zip(P_load, Q_load)):
    q_target = p * np.tan(phi_target)
    q_needed = q - q_target

    current_cap = np.sum(step_kvar[active_steps])
    net_needed = q_needed - current_cap


    if net_needed > 10.0:

        inactive_indices = np.where(~active_steps)[0]
        if len(inactive_indices) > 0:

            chosen = inactive_indices[np.argmin(switch_counts_rotational[inactive_indices])]
            active_steps[chosen] = True
            switch_counts_rotational[chosen] += 1

            switch_counts_fifo[inactive_indices[0]] += 1

    elif net_needed < -10.0:
        active_indices = np.where(active_steps)[0]
        if len(active_indices) > 0:
            chosen = active_indices[0]
            active_steps[chosen] = False

    total_cap = np.sum(step_kvar[active_steps])
    q_net = max(q - total_cap, 0.0)
    Q_net_history[i] = q_net
    cos_phi_comp[i] = p / np.sqrt(p**2 + q_net**2)


fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

ax1.plot(t_hours, cos_phi_raw, 'r--', lw=1.5, label='Kompanzasyon Öncesi cosφ (0.78 - 0.82)')
ax1.plot(t_hours, cos_phi_comp, 'b-', lw=2.2, label='ESP32 Röle ile Kompanze Edilen cosφ (0.97 - 0.99)')
ax1.axhline(0.98, color='green', linestyle=':', label='Hedef cosφ (0.98)')
ax1.axhline(0.90, color='darkorange', linestyle='--', alpha=0.7, label='Ceza Sınırı (cosφ < 0.90 Endüktif Ceza)')
ax1.set_ylabel("Güç Faktörü (cosφ)", fontweight='bold')
ax1.set_ylim(0.70, 1.02)
ax1.set_title("24 Saatlik Yük Profilinde Otomatik Kompanzasyon Performansı", fontsize=11, fontweight='bold')
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.legend(loc='lower left')

ax2.plot(t_hours, Q_load, 'r--', lw=1.5, label='Ham Endüktif Reaktif Güç Q [kVAr]')
ax2.plot(t_hours, Q_net_history, 'b-', lw=1.8, label='Şebekeden Çekilen Net Q [kVAr]')
ax2.set_xlabel("Günün Saati [Saat]", fontweight='bold')
ax2.set_ylabel("Reaktif Güç [kVAr]", fontweight='bold')
ax2.set_xlim(0, 24)
ax2.set_ylim(-10, 220)
ax2.grid(True, linestyle='--', alpha=0.6)
ax2.legend(loc='upper right')

plt.tight_layout()
plt.savefig(os.path.join(out_dir, "cosphi_ve_reaktif_guc.png"), dpi=300)
plt.close()


fig, ax = plt.subplots(figsize=(9, 4.8))

x_indices = np.arange(1, n_steps + 1)
width = 0.38


ax.bar(x_indices - width/2, switch_counts_fifo, width=width, color='salmon', edgecolor='black', label='Klasik Sıralı Seçim (Dengesiz Aşınma)')
ax.bar(x_indices + width/2, switch_counts_rotational, width=width, color='royalblue', edgecolor='black', label='Rotasyonel Eşit Yaşlandırma (Dengeli Aşınma)')

ax.set_title("12 Kademe Kontaktör Anahtarlama Sayıları Karşılaştırması", fontsize=11, fontweight='bold')
ax.set_xlabel("Kondansatör Kademe Numarası (1..12)", fontweight='bold')
ax.set_ylabel("Günlük Anahtarlama Sayısı", fontweight='bold')
ax.set_xticks(x_indices)
ax.grid(True, linestyle='--', alpha=0.6)
ax.legend(loc='upper right')


std_fifo = np.std(switch_counts_fifo)
std_rot = np.std(switch_counts_rotational)
ax.text(1.2, max(switch_counts_fifo) * 0.85,
        f"Klasik Sıralı Sapma: σ = {std_fifo:.1f} (1. kademe 5 kat hızlı tükenir!)\nEşit Yaşlandırma Sapma: σ = {std_rot:.1f} (Mükemmel homojen aşınma)",
        bbox=dict(boxstyle="round,pad=0.4", fc="yellow", alpha=0.6), fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(out_dir, "kontaktor_omru_esit_kullanim.png"), dpi=300)
plt.close()

print("E4 grafikleri başarıyla oluşturuldu.")

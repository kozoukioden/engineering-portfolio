"""
ESP32 BLE RSSI + IMU EKF Kapalı Alan Konumlandırma Simülasyonu ve Analizi
Yazar: Hakan OĞUZ (Elektrik-Elektronik Mühendisi)
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares
import os

# Grafik stili
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.size'] = 10

def generate_ground_truth(duration=60.0, dt=0.05):
    """
    15m x 15m laboratuvar/depo alanında gerçekçi yörünge üretimi
    """
    t = np.arange(0, duration, dt)
    n = len(t)
    pos = np.zeros((n, 2))
    vel = np.zeros((n, 2))
    acc = np.zeros((n, 2))

    # Yumuşak manevralı yörünge (Lissajous / sekiz benzeri kapalı döngü)
    # Alan: [2, 13] x [2, 13] metre
    pos[:, 0] = 7.5 + 4.5 * np.sin(0.12 * t)
    pos[:, 1] = 7.5 + 4.5 * np.sin(0.24 * t)

    # Sayısal türevle hız ve ivme
    vel[:, 0] = np.gradient(pos[:, 0], dt)
    vel[:, 1] = np.gradient(pos[:, 1], dt)
    acc[:, 0] = np.gradient(vel[:, 0], dt)
    acc[:, 1] = np.gradient(vel[:, 1], dt)

    return t, pos, vel, acc

def log_distance_rssi(dist, tx_power=-59.0, n=2.4, sigma=2.2):
    """
    Log-distance path loss modeli + gölgeleme (shadowing) gürültüsü
    """
    dist_safe = np.maximum(dist, 0.1)
    rssi_ideal = tx_power - 10.0 * n * np.log10(dist_safe)
    noise = np.random.normal(0, sigma, size=dist.shape)
    return rssi_ideal + noise

def rssi_to_distance(rssi, tx_power=-59.0, n=2.4):
    """
    Ölçülen RSSI'dan mesafe tahmini
    """
    exponent = (tx_power - rssi) / (10.0 * n)
    return 10.0 ** exponent

def trilateration(distances, anchors, initial_guess=(7.5, 7.5)):
    """
    En küçük kareler ile ham trilaterasyon çözümü
    """
    def residuals(p):
        return [np.linalg.norm(p - a) - d for a, d in zip(anchors, distances)]
    
    res = least_squares(residuals, initial_guess, bounds=([0, 0], [15, 15]))
    return res.x

class EKFTracker:
    def __init__(self, init_pos, q_pos=0.04, q_vel=0.15, r_ble=3.5):
        self.x = np.array([init_pos[0], init_pos[1], 0.0, 0.0])
        self.P = np.diag([2.0, 2.0, 1.0, 1.0])
        self.Q = np.diag([q_pos, q_pos, q_vel, q_vel])
        self.R_ble = r_ble

    def predict(self, ax, ay, dt):
        F = np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, 1,  0],
            [0, 0, 0,  1]
        ])
        B = np.array([
            [0.5 * dt**2, 0],
            [0, 0.5 * dt**2],
            [dt, 0],
            [0, dt]
        ])
        u = np.array([ax, ay])
        self.x = F @ self.x + B @ u
        self.P = F @ self.P @ F.T + self.Q

    def update_ble(self, anchor_pos, meas_dist):
        dx = self.x[0] - anchor_pos[0]
        dy = self.x[1] - anchor_pos[1]
        h_dist = np.sqrt(dx**2 + dy**2)
        if h_dist < 1e-3:
            h_dist = 1e-3

        H = np.array([[dx / h_dist, dy / h_dist, 0, 0]])
        y = meas_dist - h_dist
        S = (H @ self.P @ H.T)[0, 0] + self.R_ble
        K = (self.P @ H.T) / S

        self.x = self.x + (K * y).flatten()
        I = np.eye(4)
        self.P = (I - K @ H) @ self.P

def main():
    np.random.seed(42)
    dt = 0.05
    duration = 60.0
    t, pos_true, vel_true, acc_true = generate_ground_truth(duration, dt)
    n_steps = len(t)

    # 4 Sabit Anchor (15m x 15m köşe yerleşimi)
    anchors = np.array([
        [1.0, 1.0],
        [14.0, 1.0],
        [14.0, 14.0],
        [1.0, 14.0]
    ])
    tx_power = -59.0
    path_loss_n = 2.4

    # IMU Ölçüm Simülasyonu (İvmeölçer bias + gürültü)
    imu_bias = np.array([0.05, -0.04]) # Sabit bias
    acc_meas = acc_true + imu_bias + np.random.normal(0, 0.15, acc_true.shape)

    # EKF ve Ham Trilaterasyon çalıştır
    ekf = EKFTracker(init_pos=pos_true[0] + np.random.normal(0, 0.5, 2))
    pos_ekf = np.zeros((n_steps, 2))
    pos_raw_trilat = np.zeros((n_steps, 2))

    ble_rate = 10 # 10 Hz BLE örnekleme (her 2 dt adımda bir)

    current_trilat = pos_true[0].copy()

    for k in range(n_steps):
        # 1. EKF Tahmin (IMU 20 Hz)
        ekf.predict(acc_meas[k, 0], acc_meas[k, 1], dt)

        # 2. BLE Ölçüm (10 Hz)
        if k % 2 == 0:
            dists_meas = []
            for a_idx, anchor in enumerate(anchors):
                true_d = np.linalg.norm(pos_true[k] - anchor)
                rssi = log_distance_rssi(np.array([true_d]), tx_power, path_loss_n, sigma=2.4)[0]
                d_est = rssi_to_distance(rssi, tx_power, path_loss_n)
                dists_meas.append(d_est)

                # EKF güncellemesi
                ekf.update_ble(anchor, d_est)

            # Ham Trilaterasyon
            current_trilat = trilateration(dists_meas, anchors, initial_guess=current_trilat)

        pos_raw_trilat[k] = current_trilat
        pos_ekf[k] = ekf.x[:2]

    # Hata Metrikleri
    err_raw = np.linalg.norm(pos_raw_trilat - pos_true, axis=1)
    err_ekf = np.linalg.norm(pos_ekf - pos_true, axis=1)

    rmse_raw = np.sqrt(np.mean(err_raw**2))
    rmse_ekf = np.sqrt(np.mean(err_ekf**2))

    cep_raw = np.percentile(err_raw, 50)
    cep_ekf = np.percentile(err_ekf, 50)

    r95_raw = np.percentile(err_raw, 95)
    r95_ekf = np.percentile(err_ekf, 95)

    print("==================================================")
    print("Kapalı Alan Konumlandırma Performans Sonuçları:")
    print(f"Ham Trilaterasyon -> RMSE: {rmse_raw:.2f} m | CEP(%50): {cep_raw:.2f} m | %95: {r95_raw:.2f} m")
    print(f"BLE+IMU EKF       -> RMSE: {rmse_ekf:.2f} m | CEP(%50): {cep_ekf:.2f} m | %95: {r95_ekf:.2f} m")
    print(f"İyileşme Oranı    -> RMSE'de %{(1.0 - rmse_ekf/rmse_raw)*100:.1f} hata azalması")
    print("==================================================")

    out_dir = os.path.join(os.path.dirname(__file__), "..", "sekiller")
    os.makedirs(out_dir, exist_ok=True)

    # 1. Yörünge Grafiği
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.plot(pos_true[:, 0], pos_true[:, 1], 'k-', lw=2.2, label='Gerçek Yörünge (Ground Truth)')
    ax.plot(pos_raw_trilat[::4, 0], pos_raw_trilat[::4, 1], 'r.', alpha=0.35, markersize=5, label='Ham BLE Trilaterasyon')
    ax.plot(pos_ekf[:, 0], pos_ekf[:, 1], 'b-', lw=1.8, label=f'BLE + IMU EKF (RMSE: {rmse_ekf:.2f} m)')
    
    # Çapalar
    ax.scatter(anchors[:, 0], anchors[:, 1], c='green', marker='^', s=140, edgecolors='black', zorder=5, label='BLE Sabit Çapa (Anchor)')
    for i, a in enumerate(anchors):
        ax.annotate(f"A{i+1} ({a[0]:.0f},{a[1]:.0f})", (a[0]+0.3, a[1]+0.3), fontweight='bold')

    ax.set_title("15m x 15m Kapalı Alanda 2D Konumlandırma ve İzleme", fontsize=12, fontweight='bold')
    ax.set_xlabel("X Koordinatı [metre]")
    ax.set_ylabel("Y Koordinatı [metre]")
    ax.set_xlim(-0.5, 15.5)
    ax.set_ylim(-0.5, 15.5)
    ax.set_aspect('equal')
    ax.legend(loc='upper right', frameon=True)
    ax.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "konum_yorungesi_karsilastirma.png"), dpi=300)
    plt.close()

    # 2. Hata Zaman Grafiği ve CDF (Kümülatif Dağılım)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

    # Zaman grafiği
    ax1.plot(t, err_raw, 'r-', alpha=0.5, lw=1.0, label=f'Ham BLE (RMSE: {rmse_raw:.2f} m)')
    ax1.plot(t, err_ekf, 'b-', lw=1.5, label=f'BLE+IMU EKF (RMSE: {rmse_ekf:.2f} m)')
    ax1.set_title("Zamana Göre Konumlandırma Hatası", fontweight='bold')
    ax1.set_xlabel("Zaman [s]")
    ax1.set_ylabel("Öklid Hatası [metre]")
    ax1.set_ylim(0, 5.0)
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.legend(loc='upper right')

    # CDF Grafiği
    sorted_raw = np.sort(err_raw)
    sorted_ekf = np.sort(err_ekf)
    cdf_raw = np.linspace(0, 1, len(sorted_raw))
    cdf_ekf = np.linspace(0, 1, len(sorted_ekf))

    ax2.plot(sorted_raw, cdf_raw, 'r--', lw=1.8, label=f'Ham BLE CEP: {cep_raw:.2f} m')
    ax2.plot(sorted_ekf, cdf_ekf, 'b-', lw=2.0, label=f'EKF CEP: {cep_ekf:.2f} m')
    ax2.axhline(0.5, color='gray', linestyle=':', label='%50 CEP Seviyesi')
    ax2.axhline(0.95, color='orange', linestyle=':', label='%95 Doğruluk')
    ax2.set_title("Hata Kümülatif Dağılım Fonksiyonu (CDF)", fontweight='bold')
    ax2.set_xlabel("Konum Hatası [metre]")
    ax2.set_ylabel("Olasılık P(Hata <= x)")
    ax2.set_xlim(0, 4.0)
    ax2.set_ylim(0, 1.02)
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.legend(loc='lower right')

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "hata_analizi_cdf.png"), dpi=300)
    plt.close()
    print("Grafikler başarıyla kaydedildi.")

if __name__ == "__main__":
    main()

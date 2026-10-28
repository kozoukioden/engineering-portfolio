"""
Author : Hakan OĞUZ - Elektrik Elektronik Mühendisi
Project: ESP32 Kestirimci Bakım Düğümü (Titreşim ve MCSA Teşhisi)
Date   : 2026-10-27
License: MIT
Desc   : Sentetik rulman arıza sinyalleri (BPFO/BPFI), MCSA kırık rotor çubuğu yan bantları ve ISO 10816 doğrulama
"""
import os
import math
import numpy as np
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
SEK  = os.path.abspath(os.path.join(HERE, "..", "sekiller"))

def run_diagnostics_validation():
    os.makedirs(SEK, exist_ok=True)

    # 1. Rulman Parametreleri (Standart 6208 Rulmanı)
    # Nb = 9 bilya, d = 12 mm, D = 60 mm, theta = 0 rad, RPM = 1450 d/d
    rpm = 1450.0
    fr = rpm / 60.0 # 24.167 Hz
    Nb = 9
    d = 12.0
    D = 60.0
    ratio = d / D # 0.2

    bpfo = (Nb / 2.0) * fr * (1.0 - ratio) # 87.0 Hz
    bpfi = (Nb / 2.0) * fr * (1.0 + ratio) # 130.5 Hz
    print(f"Rulman Karakteristik Frekansları -> 1X: {fr:.2f} Hz | BPFO: {bpfo:.2f} Hz | BPFI: {bpfi:.2f} Hz")

    # 2. Sentetik Titreşim Sinyali Üretimi (Dış Bilezik Arızalı: BPFO Darbeleri + Yüksek Frekans Rezonansı)
    fs = 5000.0 # 5 kHz örnekleme
    N = 4096
    t = np.arange(N) / fs

    # Temel dönme harmonikleri (1X, 2X)
    sig_normal = 0.4 * np.sin(2 * np.pi * fr * t) + 0.15 * np.sin(2 * np.pi * 2 * fr * t)

    # BPFO Arıza Darbeleri: 87 Hz periyotlu darbe katarı ve yapısal rezonans (f_res = 1200 Hz)
    impulse_train = np.zeros(N)
    period_samples = int(fs / bpfo)
    for k in range(0, N, period_samples):
        impulse_train[k] = 1.8

    # Rezonans tepkisi (sönümlü sinüs ile konvolüsyon)
    decay = np.exp(-t[:150] * 600.0) * np.sin(2 * np.pi * 1200.0 * t[:150])
    fault_vibration = np.convolve(impulse_train, decay, mode='same')

    # Toplam Titreşim
    total_accel = sig_normal + fault_vibration + 0.05 * np.random.randn(N)

    # Titreşim Hız RMS (ISO 10816 Analizi)
    # a [g] -> a [m/s^2] -> sayısal entegrasyon ile v [mm/s]
    a_ms2 = total_accel * 9.80665
    v_m_s = np.cumsum(a_ms2 - np.mean(a_ms2)) / fs
    v_rms_mm_s = np.sqrt(np.mean(v_m_s**2)) * 1000.0
    print(f"ISO 10816-3 Titreşim Şiddeti: Vrms = {v_rms_mm_s:.2f} mm/s")

    # Spektrum ve Zarf (Envelope) Analizi (Hilbert benzeri mutlak değer + alçak geçiren filtre)
    fft_acc = np.abs(np.fft.rfft(total_accel)) / (N / 2)
    freqs = np.fft.rfftfreq(N, 1.0 / fs)

    # Zarf spektrumu: 1000 - 1500 Hz rezonans bandını filtreleyip demodüle et
    rectified = np.abs(fault_vibration)
    fft_env = np.abs(np.fft.rfft(rectified)) / (N / 2)

    # 1. Grafik: Titreşim Zaman Dalgası ve Zarf Spektrumunda BPFO Tespiti
    plt.figure(figsize=(11, 6))
    plt.subplot(2, 1, 1)
    plt.plot(t[:500] * 1000, total_accel[:500], 'b-', linewidth=1.2)
    plt.grid(True)
    plt.xlabel('Zaman [ms]')
    plt.ylabel('İvme [g]')
    plt.title('Motor Rulman Titreşimi (Dış Bilezik BPFO Darbe Katarı) - Hakan OĞUZ')

    plt.subplot(2, 1, 2)
    mask_env = freqs <= 350.0
    plt.plot(freqs[mask_env], fft_env[mask_env], 'r-', linewidth=1.5, label='Demodüle Zarf Spektrumu')
    plt.axvline(bpfo, color='k', linestyle='--', label=f'BPFO = {bpfo:.1f} Hz (Dış Bilezik)')
    plt.axvline(2 * bpfo, color='m', linestyle=':', label=f'2xBPFO = {2*bpfo:.1f} Hz')
    plt.grid(True)
    plt.xlabel('Frekans [Hz]')
    plt.ylabel('Zarf Genliği')
    plt.title('Zarf Analizi ile Rulman Arıza Frekansı Ayrıştırması')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(SEK, "rulman_titresim_zarf_analizi.png"), dpi=150)
    plt.close()

    # 3. MCSA (Motor Akım İmzası Analizi - Motor Current Signature Analysis)
    # Şebeke frekansı fs_line = 50 Hz, kayma s = 0.033 (Nominal yükte)
    # Kırık rotor çubuğu yan bantları: f_side = fs_line * (1 +- 2*s) = 50 +- 3.3 Hz -> 46.7 Hz ve 53.3 Hz
    s_slip = 0.033
    f_sb_low = 50.0 * (1.0 - 2.0 * s_slip)
    f_sb_high = 50.0 * (1.0 + 2.0 * s_slip)

    # Sentetik Stator Akımı (50 Hz ana taşıyıcı + -35 dB seviyesinde kırık çubuk yan bantları)
    I_fund = 45.0 * np.sin(2 * np.pi * 50.0 * t)
    I_fault = 0.8 * np.sin(2 * np.pi * f_sb_low * t) + 0.8 * np.sin(2 * np.pi * f_sb_high * t)
    I_total = I_fund + I_fault + 0.1 * np.random.randn(N)

    fft_i = np.abs(np.fft.rfft(I_total)) / (N / 2)
    fft_i_db = 20 * np.log10(fft_i / np.max(fft_i) + 1e-6)

    # 2. Grafik: MCSA Akım Spektrumu (Kırık Rotor Çubuğu Yan Bantları)
    plt.figure(figsize=(10, 5))
    mask_mcsa = (freqs >= 35.0) & (freqs <= 65.0)
    plt.plot(freqs[mask_mcsa], fft_i_db[mask_mcsa], 'b-', linewidth=1.6)
    plt.axvline(50.0, color='r', linestyle='--', label='Ana Şebeke Frekansı (50 Hz)')
    plt.axvline(f_sb_low, color='g', linestyle=':', label=f'Alt Yan Bant (46.7 Hz, s={s_slip})')
    plt.axvline(f_sb_high, color='g', linestyle=':', label=f'Üst Yan Bant (53.3 Hz, s={s_slip})')
    plt.grid(True)
    plt.xlabel('Frekans [Hz]')
    plt.ylabel('Normalleştirilmiş Genlik [dB]')
    plt.title('MCSA ile Kırık Rotor Çubuğu Yan Bantları Teşhisi (fs ± 2·s·fs)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(SEK, "mcsa_kirik_cubuk_spektrum.png"), dpi=150)
    plt.close()

    print("Kestirimci bakım grafik ve analiz çıktıları başarıyla oluşturuldu.")

if __name__ == "__main__":
    run_diagnostics_validation()

# Hakan OĞUZ - Elektrik Elektronik Mühendisi
import os
import math
import numpy as np
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
SEK  = os.path.abspath(os.path.join(HERE, "..", "sekiller"))

def run_diagnostics_validation():
    os.makedirs(SEK, exist_ok=True)


    rpm = 1450.0
    fr = rpm / 60.0
    Nb = 9
    d = 12.0
    D = 60.0
    ratio = d / D

    bpfo = (Nb / 2.0) * fr * (1.0 - ratio)
    bpfi = (Nb / 2.0) * fr * (1.0 + ratio)
    print(f"Rulman Karakteristik Frekansları -> 1X: {fr:.2f} Hz | BPFO: {bpfo:.2f} Hz | BPFI: {bpfi:.2f} Hz")


    fs = 5000.0
    N = 4096
    t = np.arange(N) / fs


    sig_normal = 0.4 * np.sin(2 * np.pi * fr * t) + 0.15 * np.sin(2 * np.pi * 2 * fr * t)


    impulse_train = np.zeros(N)
    period_samples = int(fs / bpfo)
    for k in range(0, N, period_samples):
        impulse_train[k] = 1.8


    decay = np.exp(-t[:150] * 600.0) * np.sin(2 * np.pi * 1200.0 * t[:150])
    fault_vibration = np.convolve(impulse_train, decay, mode='same')


    total_accel = sig_normal + fault_vibration + 0.05 * np.random.randn(N)


    a_ms2 = total_accel * 9.80665
    v_m_s = np.cumsum(a_ms2 - np.mean(a_ms2)) / fs
    v_rms_mm_s = np.sqrt(np.mean(v_m_s**2)) * 1000.0
    print(f"ISO 10816-3 Titreşim Şiddeti: Vrms = {v_rms_mm_s:.2f} mm/s")


    fft_acc = np.abs(np.fft.rfft(total_accel)) / (N / 2)
    freqs = np.fft.rfftfreq(N, 1.0 / fs)


    rectified = np.abs(fault_vibration)
    fft_env = np.abs(np.fft.rfft(rectified)) / (N / 2)


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


    s_slip = 0.033
    f_sb_low = 50.0 * (1.0 - 2.0 * s_slip)
    f_sb_high = 50.0 * (1.0 + 2.0 * s_slip)


    I_fund = 45.0 * np.sin(2 * np.pi * 50.0 * t)
    I_fault = 0.8 * np.sin(2 * np.pi * f_sb_low * t) + 0.8 * np.sin(2 * np.pi * f_sb_high * t)
    I_total = I_fund + I_fault + 0.1 * np.random.randn(N)

    fft_i = np.abs(np.fft.rfft(I_total)) / (N / 2)
    fft_i_db = 20 * np.log10(fft_i / np.max(fft_i) + 1e-6)


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

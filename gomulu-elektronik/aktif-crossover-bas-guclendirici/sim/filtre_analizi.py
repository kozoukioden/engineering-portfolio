# Hakan OĞUZ - Elektrik Elektronik Mühendisi
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

out_dir = os.path.join(os.path.dirname(__file__), "..", "sekiller")
os.makedirs(out_dir, exist_ok=True)

C_hp, Rf_hp, Rg_hp = 150e-9, 39e3, 75e3
hp = ([1, 0, 0], [1, 2 / (Rg_hp * C_hp), 1 / (Rf_hp * Rg_hp * C_hp**2)])

R_lp, C1_lp, C2_lp = 29.4e3, 100e-9, 47e-9
w2 = 1 / (R_lp**2 * C1_lp * C2_lp)
lp = ([w2], [1, 2 / (R_lp * C1_lp), w2])

def cascade(*tfs):
    b, a = [1.0], [1.0]
    for bb, aa in tfs:
        b, a = np.convolve(b, bb), np.convolve(a, aa)
    return b, a

def allpass(R):
    tau = R * 220e-9
    return ([-tau, 1], [tau, 1])

def shelf(Rv):
    Rg, Cf = 10e3, 180e-9
    if Rv == 0:
        return ([1.0], [1.0])
    return ([Rv * Cf, 1 + Rv / Rg], [Rv * Cf, 1])

for name, (b, a) in (("HPF", hp), ("LPF", lp)):
    w0 = np.sqrt(a[2])
    print(f"{name}: fc = {w0 / (2 * np.pi):.1f} Hz, Q = {w0 / a[1]:.3f}")

f = np.logspace(np.log10(5), np.log10(1000), 800)
w = 2 * np.pi * f
b_x, a_x = cascade(hp, lp, lp)
_, h_x = signal.freqs(b_x, a_x, worN=w)

bi_hp = signal.butter(2, 2 * np.pi * 20, "high", analog=True)
bi_lp = signal.butter(2, 2 * np.pi * 80, "low", analog=True)
_, h_i = signal.freqs(*cascade(bi_hp, bi_lp, bi_lp), worN=w)

f80 = np.interp(-6.02, 20 * np.log10(np.abs(h_x))[f > 40][::-1], f[f > 40][::-1])
print(f"LR4 -6 dB noktasi: {f80:.1f} Hz")
print(f"80 Hz kazanc: {20 * np.log10(abs(signal.freqs(b_x, a_x, worN=[2 * np.pi * 80])[1][0])):.2f} dB")

for R in (470, 25e3, 50.47e3):
    ph = np.degrees(np.angle(signal.freqs(*allpass(R), worN=[2 * np.pi * 80])[1][0]))
    print(f"Faz ayari R = {R / 1e3:.2f} k -> 80 Hz'de {ph:.1f} derece")
for Rv in (0, 5e3, 10e3):
    g = 20 * np.log10(abs(signal.freqs(*shelf(Rv), worN=[2 * np.pi * 30])[1][0]))
    print(f"Bas raf RV2 = {Rv / 1e3:.0f} k -> 30 Hz'de {g:+.2f} dB")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
ax1.semilogx(f, 20 * np.log10(np.abs(h_i)), "k:", lw=1.5, label="Ideal (Butterworth^2, 20 Hz HPF)")
ax1.semilogx(f, 20 * np.log10(np.abs(h_x)), "b-", lw=2, label="Semadaki degerler")
for Rv, c in ((5e3, "orange"), (10e3, "r")):
    _, hs = signal.freqs(*shelf(Rv), worN=w)
    ax1.semilogx(f, 20 * np.log10(np.abs(h_x * hs)), "--", color=c, lw=1.5, label=f"RV2 = {Rv / 1e3:.0f} k")
ax1.axhline(-6, color="g", ls="--", alpha=0.5)
ax1.axvline(80, color="g", ls=":")
ax1.set_ylim(-40, 10)
ax1.set_ylabel("Kazanc [dB]")
ax1.set_title("Subsonik HPF + LR4 alcak geciren + bas raf")
ax1.grid(True, which="both", ls="--", alpha=0.5)
ax1.legend(loc="lower left", fontsize=8)

for R, c in ((470, "b"), (10e3, "g"), (50.47e3, "r")):
    _, ha = signal.freqs(*allpass(R), worN=w)
    ax2.semilogx(f, np.degrees(np.unwrap(np.angle(ha))), color=c, label=f"R = {R / 1e3:.1f} k")
ax2.axvline(80, color="g", ls=":")
ax2.set_xlim(5, 1000)
ax2.set_xlabel("Frekans [Hz]")
ax2.set_ylabel("Tum geciren faz [derece]")
ax2.grid(True, which="both", ls="--", alpha=0.5)
ax2.legend(fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(out_dir, "crossover_frekans_cevabi_bode.png"), dpi=200)
plt.close()

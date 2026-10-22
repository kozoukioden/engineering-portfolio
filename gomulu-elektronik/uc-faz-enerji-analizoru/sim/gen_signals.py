# Author : Hakan OGUZ - Elektrik Elektronik Muhendisi
# Project: Three-phase energy analyzer node - signal generator / reference
# Date   : 2026-10-22
# License: MIT
# Desc   : Builds synthetic 3-phase V/I with known harmonics, writes samples.csv,
#          computes an independent numpy reference, and plots waveforms + spectrum.
import os
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
SEK = os.path.join(ROOT, "sekiller")
os.makedirs(SEK, exist_ok=True)

F0 = 50.0
SPC = 256                 # samples per cycle
CYCLES = 10
N = SPC * CYCLES          # 2560 samples
FS = F0 * SPC             # 12800 Hz

VRMS1 = 230.0             # fundamental phase-neutral voltage (RMS)
IRMS1 = 20.0              # fundamental current (RMS)
PF1 = 0.90                # fundamental displacement power factor (lagging)
PHI1 = np.arccos(PF1)

# harmonic content as fraction of the FUNDAMENTAL amplitude (order: fraction, phase[rad])
V_HARM = {3: (0.015, 0.0), 5: (0.025, 0.0), 7: (0.010, 0.0)}
I_HARM = {5: (0.080, 0.6), 7: (0.050, -0.4), 11: (0.030, 1.1)}

SQRT2 = np.sqrt(2.0)
w = 2.0 * np.pi * F0
t = np.arange(N) / FS


def phase_signals(delta):
    """One phase shifted by 'delta' rad on the fundamental (both V and I)."""
    v = VRMS1 * SQRT2 * np.cos(w * t + delta)
    for h, (frac, ph) in V_HARM.items():
        v += VRMS1 * SQRT2 * frac * np.cos(h * (w * t + delta) + ph)
    i = IRMS1 * SQRT2 * np.cos(w * t + delta - PHI1)
    for h, (frac, ph) in I_HARM.items():
        i += IRMS1 * SQRT2 * frac * np.cos(h * (w * t + delta) + ph)
    return v, i


va, ia = phase_signals(0.0)
vb, ib = phase_signals(-2.0 * np.pi / 3.0)
vc, ic = phase_signals(+2.0 * np.pi / 3.0)

# --- write samples.csv (columns consumed by the C host test) -----------------
data = np.column_stack([va, ia, vb, ib, vc, ic]).astype(np.float64)
np.savetxt(os.path.join(HERE, "samples.csv"), data, delimiter=",",
           header="va,ia,vb,ib,vc,ic", comments="", fmt="%.6f")


# --- independent numpy reference metrics (same definitions as the C core) -----
def ref_metrics(v, i):
    vrms = np.sqrt(np.mean(v * v))
    irms = np.sqrt(np.mean(i * i))
    p = np.mean(v * i)
    s = vrms * irms
    q = np.sqrt(max(s * s - p * p, 0.0))
    pf = p / s if s > 1e-9 else 0.0

    def thd(x):
        k = np.arange(N)
        a1c = 2.0 / N * np.sum(x * np.cos(2 * np.pi * 1 * k / SPC))
        a1s = 2.0 / N * np.sum(x * np.sin(2 * np.pi * 1 * k / SPC))
        a1 = np.hypot(a1c, a1s)
        acc = 0.0
        for h in range(2, 16):
            hc = 2.0 / N * np.sum(x * np.cos(2 * np.pi * h * k / SPC))
            hs = 2.0 / N * np.sum(x * np.sin(2 * np.pi * h * k / SPC))
            acc += hc * hc + hs * hs
        return (np.sqrt(acc) / a1 if a1 > 1e-9 else 0.0), a1

    thd_v, v1 = thd(v)
    thd_i, i1 = thd(i)
    return dict(v_rms=vrms, i_rms=irms, p=p, s=s, q=q, pf=pf,
                thd_v=thd_v, thd_i=thd_i, v_fund=v1, i_fund=i1)


ref = {"A": ref_metrics(va, ia), "B": ref_metrics(vb, ib), "C": ref_metrics(vc, ic)}
ref["TOTAL"] = {
    "p": sum(ref[p]["p"] for p in "ABC"),
    "s": sum(ref[p]["s"] for p in "ABC"),
    "q": sum(ref[p]["q"] for p in "ABC"),
}
ref["TOTAL"]["pf"] = ref["TOTAL"]["p"] / ref["TOTAL"]["s"]
with open(os.path.join(HERE, "reference.json"), "w") as f:
    json.dump(ref, f, indent=2)

# analytic THD expectations (from injected content)
thd_v_an = np.sqrt(sum(f * f for f, _ in V_HARM.values()))
thd_i_an = np.sqrt(sum(f * f for f, _ in I_HARM.values()))

print("Fs = %.0f Hz, N = %d (%d cycles x %d)" % (FS, N, CYCLES, SPC))
print("Per-phase A: Vrms=%.3f Irms=%.3f P=%.1f W S=%.1f VA PF=%.4f THDv=%.3f%% THDi=%.3f%%"
      % (ref["A"]["v_rms"], ref["A"]["i_rms"], ref["A"]["p"], ref["A"]["s"],
         ref["A"]["pf"], ref["A"]["thd_v"] * 100, ref["A"]["thd_i"] * 100))
print("Analytic THDv=%.3f%%  THDi=%.3f%%" % (thd_v_an * 100, thd_i_an * 100))
print("3-phase: P=%.1f W  S=%.1f VA  PF=%.4f"
      % (ref["TOTAL"]["p"], ref["TOTAL"]["s"], ref["TOTAL"]["pf"]))

# --- plot 1: waveforms (2 cycles of phase A) ---------------------------------
ns = 2 * SPC
tt = t[:ns] * 1000.0
fig, ax1 = plt.subplots(figsize=(9, 4.2))
ax1.plot(tt, va[:ns], color="#1f4e79", lw=1.6, label="Va")
ax1.set_xlabel("time [ms]")
ax1.set_ylabel("voltage [V]", color="#1f4e79")
ax1.tick_params(axis="y", labelcolor="#1f4e79")
ax1.axhline(0, color="#999", lw=0.6)
ax2 = ax1.twinx()
ax2.plot(tt, ia[:ns], color="#b8341b", lw=1.6, label="Ia")
ax2.set_ylabel("current [A]", color="#b8341b")
ax2.tick_params(axis="y", labelcolor="#b8341b")
ax1.set_title("Phase A voltage and current (PF=0.90 lagging, with harmonics)")
fig.tight_layout()
fig.savefig(os.path.join(SEK, "waveforms.png"), dpi=150)
plt.close(fig)

# --- plot 2: harmonic spectrum of phase-A current ----------------------------
k = np.arange(N)
orders = np.arange(1, 16)
mags = []
for h in orders:
    hc = 2.0 / N * np.sum(ia * np.cos(2 * np.pi * h * k / SPC))
    hs = 2.0 / N * np.sum(ia * np.sin(2 * np.pi * h * k / SPC))
    mags.append(np.hypot(hc, hs))
mags = np.array(mags)
pct = 100.0 * mags / mags[0]
fig, ax = plt.subplots(figsize=(9, 4.2))
bars = ax.bar(orders, pct, color="#b8341b", width=0.6)
bars[0].set_color("#1f4e79")
ax.set_xlabel("harmonic order")
ax.set_ylabel("magnitude [% of fundamental]")
ax.set_title("Phase-A current harmonic spectrum (THDi = %.2f%%)" % (ref["A"]["thd_i"] * 100))
ax.set_xticks(orders)
for o, p in zip(orders, pct):
    if p > 1.0:
        ax.text(o, p + 0.4, "%.1f" % p, ha="center", fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(SEK, "spectrum.png"), dpi=150)
plt.close(fig)

print("wrote samples.csv, reference.json, waveforms.png, spectrum.png")

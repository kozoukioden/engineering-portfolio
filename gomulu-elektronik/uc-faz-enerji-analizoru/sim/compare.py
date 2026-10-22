# Author : Hakan OGUZ - Elektrik Elektronik Muhendisi
# Project: Three-phase energy analyzer node - validation report
# Date   : 2026-10-22
# License: MIT
# Desc   : Compares the firmware DSP output (fw_results.csv) with the numpy reference
#          (reference.json) and renders a validation figure.
import os
import json
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
SEK = os.path.join(ROOT, "sekiller")

ref = json.load(open(os.path.join(HERE, "reference.json")))
fw = {}
with open(os.path.join(HERE, "fw_results.csv")) as f:
    for row in csv.DictReader(f):
        fw[row["phase"]] = row

keys = [("v_rms", "Vrms [V]", "v_rms"), ("i_rms", "Irms [A]", "i_rms"),
        ("p", "P [W]", "p"), ("s", "S [VA]", "s"), ("pf", "PF", "pf"),
        ("thd_v", "THDv", "thd_v"), ("thd_i", "THDi", "thd_i")]

print("Phase A : firmware DSP vs numpy reference")
print("%-10s %14s %14s %12s" % ("metric", "firmware", "reference", "rel.err"))
rows = []
for fwk, label, refk in keys:
    fval = float(fw["A"][fwk])
    rval = float(ref["A"][refk])
    err = abs(fval - rval) / (abs(rval) if abs(rval) > 1e-9 else 1.0)
    rows.append((label, fval, rval, err))
    print("%-10s %14.5f %14.5f %12.2e" % (label, fval, rval, err))

maxerr = max(r[3] for r in rows)
print("\nmax relative error (phase A): %.2e" % maxerr)
print("3-phase P firmware=%.1f W  reference=%.1f W" %
      (float(fw["TOTAL"]["p"]), ref["TOTAL"]["p"]))

# validation figure: relative error per metric (log scale)
labels = [r[0] for r in rows]
errs = [max(r[3], 1e-12) for r in rows]
fig, ax = plt.subplots(figsize=(9, 4.2))
ax.bar(labels, errs, color="#2e6b34", width=0.6)
ax.set_yscale("log")
ax.set_ylabel("relative error (firmware vs numpy)")
ax.set_title("Firmware DSP validation against independent reference (phase A)")
ax.axhline(1e-4, color="#b8341b", ls="--", lw=1.0, label="0.01% band")
ax.legend()
for i, e in enumerate(errs):
    ax.text(i, e * 1.4, "%.0e" % e, ha="center", fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(SEK, "validation.png"), dpi=150)
plt.close(fig)
print("wrote validation.png")

# Author : Hakan OĞUZ - Elektrik Elektronik Mühendisi
# Project: Cati Ustu 110 kWp Sebeke Baglantili GES - Saha Yerlesimi ve Tek Hat Semasi
# Date   : 2026-10-22
# License: MIT
# Desc   : ezdxf ile 110 kWp catı GES icin saha yerlesim plani ve AG tek hat semasi uretir.
"""
Cizim birimi: milimetre. Iki pafta uretilir:
  GES-01  ges-saha-yerlesimi.dxf  -> catı uzeri string yerlesimi, inverter/pano, DC-AC, topraklama
  GES-02  ges-tek-hat-semasi.dxf  -> string -> DC ayirici/sigorta -> inverter -> AG pano -> sayac -> sebeke

Sistem parametreleri (hesaplar README'de):
  Modul   : 550 Wp mono, Voc=49.5 V, Vmp=41.7 V, Isc=13.95 A, Imp=13.19 A, beta_Voc=-0.27 %/C, 2278x1134 mm
  Dizge   : 10 string x 20 modul = 200 modul = 110.0 kWp
  Inverter: 100 kW, MPPT 200-1000 V, V_dc_max=1100 V, 3F 400 V
"""
import os
import ezdxf
from ezdxf.enums import TextEntityAlignment

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.abspath(os.path.join(HERE, ".."))
SEK  = os.path.join(OUT, "sekiller")

MODUL_W, MODUL_D = 2278.0, 1134.0
MODUL_GAP        = 25.0
STRING_SAYI      = 10
MODUL_PER_STRING = 20
SIRA_PITCH       = 3000.0
ARRAY_X0, ARRAY_Y0 = 2500.0, 3000.0
CATI_W, CATI_D   = 50000.0, 34000.0
STRING_ACI = [1, 2, 3, 4, 5, 6, 30, 40, 150, 200]

KATMANLAR = [
    ("CATI", 8, "CONTINUOUS"), ("PANELLER", 7, "CONTINUOUS"), ("STRING", 7, "CONTINUOUS"),
    ("INVERTER", 4, "CONTINUOUS"), ("DC_KABLO", 1, "DASHED"), ("AC_KABLO", 5, "CONTINUOUS"),
    ("TOPRAKLAMA", 3, "DASHDOT"), ("OLCU", 8, "CONTINUOUS"), ("YAZI", 7, "CONTINUOUS"),
    ("LEJANT", 7, "CONTINUOUS"), ("ANTET", 7, "CONTINUOUS"), ("SEMA", 7, "CONTINUOUS"),
]


def yeni_doc():
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 4
    doc.header["$MEASUREMENT"] = 1
    for ad, renk, lt in KATMANLAR:
        if lt not in doc.linetypes:
            lt = "CONTINUOUS"
        doc.layers.add(ad, color=renk, linetype=lt)
    if "ANNOT" not in doc.styles:
        doc.styles.add("ANNOT", font="arial.ttf")
    return doc


def yazi(msp, text, x, y, h=400, layer="YAZI", align=TextEntityAlignment.LEFT, rot=0, color=None):
    attr = {"layer": layer, "style": "ANNOT"}
    if color is not None:
        attr["color"] = color
    t = msp.add_text(text, height=h, rotation=rot, dxfattribs=attr)
    t.set_placement((x, y), align=align)
    return t


def antet(msp, pafta_adi, pafta_no, olcek, x0, y0):
    w, h = 16000.0, 7200.0
    msp.add_lwpolyline([(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)],
                       close=True, dxfattribs={"layer": "ANTET", "const_width": 60})
    for yy in (y0 + h - 1600, y0 + h - 3000, y0 + h - 4400, y0 + 1600):
        msp.add_line((x0, yy), (x0 + w, yy), dxfattribs={"layer": "ANTET"})
    yazi(msp, "CATI USTU 110 kWp SEBEKE BAGLANTILI GES", x0 + 400, y0 + h - 1150, h=600, layer="ANTET")
    yazi(msp, pafta_adi, x0 + 400, y0 + h - 2650, h=500, layer="ANTET")
    yazi(msp, "Cizen : Hakan OGUZ", x0 + 400, y0 + h - 4000, h=500, layer="ANTET")
    yazi(msp, "Elektrik Elektronik Muhendisi", x0 + 400, y0 + h - 5250, h=450, layer="ANTET")
    xr = x0 + 9600
    msp.add_line((xr, y0 + 1600), (xr, y0), dxfattribs={"layer": "ANTET"})
    yazi(msp, "Tarih", xr + 300, y0 + 1130, h=340, layer="ANTET")
    yazi(msp, "2026-10-22", xr + 300, y0 + 480, h=400, layer="ANTET")
    xr2 = x0 + 12900
    msp.add_line((xr2, y0 + 1600), (xr2, y0), dxfattribs={"layer": "ANTET"})
    yazi(msp, "Olcek", xr2 + 300, y0 + 1130, h=340, layer="ANTET")
    yazi(msp, olcek, xr2 + 300, y0 + 480, h=400, layer="ANTET")
    yazi(msp, "Pafta No : " + pafta_no, x0 + 400, y0 + 500, h=500, layer="ANTET")


def kuzey_oku(msp, x, y, r=1600):
    msp.add_line((x, y - r), (x, y + r), dxfattribs={"layer": "YAZI"})
    msp.add_solid([(x, y + r), (x - r * 0.28, y + r * 0.45), (x + r * 0.28, y + r * 0.45)],
                  dxfattribs={"layer": "YAZI"})
    yazi(msp, "K", x, y + r + 300, h=600, layer="YAZI", align=TextEntityAlignment.CENTER)


def olcu_yatay(msp, x1, x2, y, metin, ofs=900):
    msp.add_line((x1, y), (x1, y + ofs * 1.2), dxfattribs={"layer": "OLCU"})
    msp.add_line((x2, y), (x2, y + ofs * 1.2), dxfattribs={"layer": "OLCU"})
    msp.add_line((x1, y + ofs), (x2, y + ofs), dxfattribs={"layer": "OLCU"})
    for xx, s in ((x1, 1), (x2, -1)):
        msp.add_solid([(xx, y + ofs), (xx + s * 350, y + ofs + 110), (xx + s * 350, y + ofs - 110)],
                      dxfattribs={"layer": "OLCU"})
    yazi(msp, metin, (x1 + x2) / 2, y + ofs + 180, h=380, layer="OLCU", align=TextEntityAlignment.CENTER)


# ============================================================ PAFTA 1
def saha_plani():
    doc = yeni_doc()
    msp = doc.modelspace()

    msp.add_lwpolyline([(0, 0), (CATI_W, 0), (CATI_W, CATI_D), (0, CATI_D)],
                       close=True, dxfattribs={"layer": "CATI", "const_width": 80})
    yazi(msp, "CATI SINIRI", 500, CATI_D - 1150, h=520, layer="YAZI")

    adim = MODUL_W + MODUL_GAP
    array_w = MODUL_PER_STRING * adim - MODUL_GAP
    string_sag_x = []
    for s in range(STRING_SAYI):
        y0 = ARRAY_Y0 + s * SIRA_PITCH
        aci = STRING_ACI[s % len(STRING_ACI)]
        for m in range(MODUL_PER_STRING):
            x0 = ARRAY_X0 + m * adim
            msp.add_lwpolyline(
                [(x0, y0), (x0 + MODUL_W, y0), (x0 + MODUL_W, y0 + MODUL_D), (x0, y0 + MODUL_D)],
                close=True, dxfattribs={"layer": "PANELLER", "color": aci})
            msp.add_line((x0, y0), (x0 + MODUL_W, y0 + MODUL_D),
                         dxfattribs={"layer": "PANELLER", "color": aci})
        yazi(msp, "STRING %02d  (20 x 550Wp = 11.0 kWp)" % (s + 1),
             ARRAY_X0 + 150, y0 + MODUL_D + 250, h=360, layer="STRING", color=aci)
        string_sag_x.append((ARRAY_X0 + array_w, y0 + MODUL_D / 2))

    # teknik hacim: inverter + AG pano (catının altinda)
    inv = (33000.0, -5200.0, 4200.0, 3000.0)   # x,y,w,h
    msp.add_lwpolyline([(inv[0], inv[1]), (inv[0] + inv[2], inv[1]),
                        (inv[0] + inv[2], inv[1] + inv[3]), (inv[0], inv[1] + inv[3])],
                       close=True, dxfattribs={"layer": "INVERTER"})
    yazi(msp, "INVERTER", inv[0] + inv[2] / 2, inv[1] + inv[3] / 2 + 250, h=420,
         layer="INVERTER", align=TextEntityAlignment.CENTER)
    yazi(msp, "100 kW / 3F", inv[0] + inv[2] / 2, inv[1] + inv[3] / 2 - 450, h=360,
         layer="INVERTER", align=TextEntityAlignment.CENTER)
    pano = (39000.0, -5200.0, 3600.0, 3000.0)
    msp.add_lwpolyline([(pano[0], pano[1]), (pano[0] + pano[2], pano[1]),
                        (pano[0] + pano[2], pano[1] + pano[3]), (pano[0], pano[1] + pano[3])],
                       close=True, dxfattribs={"layer": "AC_KABLO"})
    yazi(msp, "AG DAGITIM", pano[0] + pano[2] / 2, pano[1] + pano[3] / 2 + 250, h=380,
         layer="AC_KABLO", align=TextEntityAlignment.CENTER)
    yazi(msp, "PANOSU", pano[0] + pano[2] / 2, pano[1] + pano[3] / 2 - 400, h=380,
         layer="AC_KABLO", align=TextEntityAlignment.CENTER)

    # DC toplama: her string sag ucundan dusey DC bara, inverter girisine
    bara_x = ARRAY_X0 + array_w + 900
    for (sx, sy) in string_sag_x:
        msp.add_line((sx, sy), (bara_x, sy), dxfattribs={"layer": "DC_KABLO"})
    msp.add_line((bara_x, string_sag_x[0][1]), (bara_x, string_sag_x[-1][1]),
                 dxfattribs={"layer": "DC_KABLO"})
    msp.add_line((bara_x, string_sag_x[0][1]), (bara_x, inv[1] + inv[3]),
                 dxfattribs={"layer": "DC_KABLO"})
    msp.add_line((bara_x, inv[1] + inv[3]), (inv[0] + inv[2] / 2, inv[1] + inv[3]),
                 dxfattribs={"layer": "DC_KABLO"})
    yazi(msp, "DC BARA (10 string)", bara_x + 250, (string_sag_x[0][1] + string_sag_x[-1][1]) / 2,
         h=330, layer="DC_KABLO", rot=90, align=TextEntityAlignment.CENTER)

    # AC: inverter -> AG pano -> sebeke
    msp.add_line((inv[0] + inv[2], inv[1] + inv[3] / 2), (pano[0], pano[1] + pano[3] / 2),
                 dxfattribs={"layer": "AC_KABLO"})
    msp.add_line((pano[0] + pano[2], pano[1] + pano[3] / 2),
                 (pano[0] + pano[2] + 2500, pano[1] + pano[3] / 2),
                 dxfattribs={"layer": "AC_KABLO"})
    yazi(msp, "SEBEKE (OG/AG)", pano[0] + pano[2] + 300, pano[1] + pano[3] / 2 + 300,
         h=360, layer="AC_KABLO")

    # topraklama ring (dizge cevresi) + kazik sembolleri
    gx0, gy0 = ARRAY_X0 - 800, ARRAY_Y0 - 800
    gx1, gy1 = ARRAY_X0 + array_w + 400, ARRAY_Y0 + (STRING_SAYI - 1) * SIRA_PITCH + MODUL_D + 800
    msp.add_lwpolyline([(gx0, gy0), (gx1, gy0), (gx1, gy1), (gx0, gy1)],
                       close=True, dxfattribs={"layer": "TOPRAKLAMA"})
    for (kx, ky) in ((gx0, gy0), (gx1, gy0), (gx0, gy1), (gx1, gy1)):
        msp.add_circle((kx, ky), 350, dxfattribs={"layer": "TOPRAKLAMA"})
        msp.add_line((kx - 250, ky - 250), (kx + 250, ky + 250), dxfattribs={"layer": "TOPRAKLAMA"})
    yazi(msp, "TOPRAKLAMA RINGI (Cu 50mm2) + KAZIK", gx0, gy1 + 300, h=360, layer="TOPRAKLAMA")

    # olculer
    olcu_yatay(msp, 0, CATI_W, CATI_D + 300, "50000 (catı)")
    olcu_yatay(msp, ARRAY_X0, ARRAY_X0 + array_w, ARRAY_Y0 - 2200, "%.0f (dizge genisligi)" % array_w)

    kuzey_oku(msp, CATI_W - 2500, CATI_D - 3500)

    # lejant
    lx, ly = 1200.0, -5400.0
    yazi(msp, "LEJANT", lx, ly + 2600, h=520, layer="LEJANT")
    lej = [("PV MODUL (550 Wp)", 5), ("DC KABLO (1100V DC)", 1),
           ("AC KABLO (3F 400V)", 5), ("TOPRAKLAMA", 3), ("INVERTER / PANO", 4)]
    for i, (ad, c) in enumerate(lej):
        yy = ly + 1800 - i * 700
        msp.add_lwpolyline([(lx, yy), (lx + 1400, yy), (lx + 1400, yy + 400), (lx, yy + 400)],
                           close=True, dxfattribs={"layer": "LEJANT", "color": c})
        yazi(msp, ad, lx + 1700, yy + 40, h=360, layer="LEJANT")

    antet(msp, "SAHA YERLESIM PLANI", "GES-01", "1:200", CATI_W - 15000.0, -14500.0)

    doc.saveas(os.path.join(OUT, "ges-saha-yerlesimi.dxf"))
    return doc


# ============================================================ PAFTA 2: TEK HAT SEMASI
def kutu(msp, x, y, w, h, metin, layer="SEMA", th=380):
    msp.add_lwpolyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
                       close=True, dxfattribs={"layer": layer})
    for i, satir in enumerate(metin.split("\n")):
        yazi(msp, satir, x + w / 2, y + h / 2 + (len(metin.split("\n")) - 1) * th * 0.6 - i * th * 1.2,
             h= th, layer=layer, align=TextEntityAlignment.CENTER)


def tek_hat():
    doc = yeni_doc()
    msp = doc.modelspace()

    yazi(msp, "AG TEK HAT SEMASI - 110 kWp SEBEKE BAGLANTILI GES", 0, 23000, h=700, layer="SEMA")

    # sol: string grubu temsili (3 string cizilir, 10 string yazilir)
    x = 0.0
    for i in range(3):
        yy = 18000 - i * 2600
        msp.add_lwpolyline([(x, yy), (x + 2600, yy), (x + 2600, yy + 1500), (x, yy + 1500)],
                           close=True, dxfattribs={"layer": "SEMA", "color": STRING_ACI[i]})
        msp.add_line((x, yy), (x + 2600, yy + 1500), dxfattribs={"layer": "SEMA", "color": STRING_ACI[i]})
        yazi(msp, "STRING %02d" % (i + 1), x + 1300, yy + 1900, h=360, layer="SEMA",
             align=TextEntityAlignment.CENTER)
        msp.add_line((x + 2600, yy + 750), (6500, yy + 750), dxfattribs={"layer": "DC_KABLO"})
    yazi(msp, ". . . 10 STRING", x + 900, 18000 - 3 * 2600 - 300, h=420, layer="SEMA")
    yazi(msp, "Her string: 20 x 550Wp\nVoc(-10C)=1083V < 1100V\nImp=13.2A",
         x, 7800, h=330, layer="YAZI")

    # DC toplama kutusu: sigorta + SPD + DC ayirici
    kutu(msp, 6500, 13500, 4200, 4200,
         "DC TOPLAMA\n10 x gPV sigorta 16A\nTip II DC SPD\nDC AYIRICI 1100V", "SEMA", 330)
    msp.add_line((10700, 15600), (13500, 15600), dxfattribs={"layer": "DC_KABLO"})
    yazi(msp, "DC 1100V", 11000, 15800, h=330, layer="DC_KABLO")

    # inverter
    kutu(msp, 13500, 13500, 4600, 4200, "INVERTER\n100 kW\nMPPT 200-1000V\nDC/AC", "INVERTER", 360)
    msp.add_line((18100, 15600), (21000, 15600), dxfattribs={"layer": "AC_KABLO"})
    yazi(msp, "3F 400V", 18400, 15800, h=330, layer="AC_KABLO")

    # AC kesici (inverter cikis)
    kutu(msp, 21000, 14100, 3400, 3000, "AC KESICI\n160A 3F\n(MCCB)", "AC_KABLO", 360)
    msp.add_line((24400, 15600), (27000, 15600), dxfattribs={"layer": "AC_KABLO"})

    # sayac
    kutu(msp, 27000, 14100, 3400, 3000, "CIFT YONLU\nSAYAC\n(OSOS)", "SEMA", 360)
    msp.add_line((30400, 15600), (33000, 15600), dxfattribs={"layer": "AC_KABLO"})

    # AG pano / sebeke
    kutu(msp, 33000, 14100, 3800, 3000, "AG DAGITIM\nPANOSU\n+ SPD Tip II", "AC_KABLO", 360)
    msp.add_line((36800, 15600), (39600, 15600), dxfattribs={"layer": "AC_KABLO"})
    # sebeke sembolu
    msp.add_circle((40500, 15600), 900, dxfattribs={"layer": "AC_KABLO"})
    yazi(msp, "~", 40500, 15300, h=900, layer="AC_KABLO", align=TextEntityAlignment.CENTER)
    yazi(msp, "SEBEKE", 40500, 13900, h=380, layer="AC_KABLO", align=TextEntityAlignment.CENTER)

    # topraklama bara
    msp.add_line((6500, 11200), (36800, 11200), dxfattribs={"layer": "TOPRAKLAMA"})
    for tx in (8600, 15800, 22700, 28700, 34900):
        msp.add_line((tx, 11200), (tx, 13500 if tx < 20000 else 14100),
                     dxfattribs={"layer": "TOPRAKLAMA"})
    # topraklama sembolu
    gx = 21500
    msp.add_line((gx, 11200), (gx, 10200), dxfattribs={"layer": "TOPRAKLAMA"})
    for i, wdt in enumerate((1400, 900, 450)):
        msp.add_line((gx - wdt / 2, 10200 - i * 300), (gx + wdt / 2, 10200 - i * 300),
                     dxfattribs={"layer": "TOPRAKLAMA"})
    yazi(msp, "KORUMA TOPRAKLAMA BARASI (PE)", 6500, 10900, h=330, layer="TOPRAKLAMA")

    # notlar
    yazi(msp, "NOTLAR:", 0, 5200, h=420, layer="YAZI")
    notlar = [
        "1. Tasarim IEC 62548 (PV array) ve IEC 60364-7-712 esaslarina gore yapilmistir.",
        "2. String Voc en dusuk modul sicakliginda (-10C) 1083V olup inverter Vdc_max=1100V altindadir.",
        "3. DC tarafta gPV string sigortalari ve Tip II DC SPD; AC tarafta MCCB ve Tip II SPD ongorulmustur.",
        "4. Tum metal govdeler ve modul tasiyici konstruksiyon PE barasina baglanir (espotansiyel).",
        "5. Kurulu guc 110.0 kWp (DC), inverter 100 kW (AC); DC/AC orani 1.10.",
    ]
    for i, n in enumerate(notlar):
        yazi(msp, n, 0, 4400 - i * 650, h=330, layer="YAZI")

    antet(msp, "AG TEK HAT SEMASI", "GES-02", "-", 26000.0, -3500.0)

    doc.saveas(os.path.join(OUT, "ges-tek-hat-semasi.dxf"))
    return doc


# ============================================================ PNG RENDER
def render_png(doc, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from ezdxf.addons.drawing import RenderContext, Frontend
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy

    msp = doc.modelspace()
    fig = plt.figure(figsize=(16, 11))
    ax = fig.add_axes([0, 0, 1, 1])
    ctx = RenderContext(doc)
    be = MatplotlibBackend(ax)
    cfg = Configuration(background_policy=BackgroundPolicy.WHITE)
    Frontend(ctx, be, config=cfg).draw_layout(msp, finalize=True)
    fig.savefig(path, dpi=150, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    d1 = saha_plani()
    d2 = tek_hat()
    os.makedirs(SEK, exist_ok=True)
    render_png(d1, os.path.join(SEK, "saha-yerlesimi.png"))
    render_png(d2, os.path.join(SEK, "tek-hat-semasi.png"))
    print("OK: 2 DXF + 2 PNG uretildi ->", OUT)

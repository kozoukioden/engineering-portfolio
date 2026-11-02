# Author : Hakan OĞUZ - Elektrik Elektronik Mühendisi
# Project: Mısır İşleme Hattı MCC ve VFD Kumanda Panosu
# Date   : 2026-10-27
# License: MIT
# Desc   : Mısır kırma, eleme, pnömatik taşıma ve kurutma fanları için MCC güç/kumanda şeması, pano görünüşü ve kablo/gerilim düşümü tablosu.

import os
import ezdxf
from ezdxf.enums import TextEntityAlignment

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.abspath(os.path.join(HERE, ".."))
SEK  = os.path.join(OUT, "sekiller")

KATMANLAR = [
    ("CERCEVE", 7, "CONTINUOUS"),
    ("GUC_HAT", 1, "CONTINUOUS"),       # Kırmızı güç barası / besleme
    ("KUMANDA_HAT", 5, "CONTINUOUS"),   # Mavi 24VDC/230VAC kumanda hatları
    ("MOTOR_HAT", 3, "CONTINUOUS"),     # Yeşil motor besleme
    ("PANO_KARKAS", 8, "CONTINUOUS"),   # Gri pano dış hatları
    ("PANO_ELEMAN", 4, "CONTINUOUS"),   # Cihazlar (VFD, kontaktör, TMŞ)
    ("OLCU", 8, "CONTINUOUS"),          # Gerçek ölçü çizgileri
    ("YAZI", 7, "CONTINUOUS"),
    ("ANTET", 7, "CONTINUOUS"),
]

def yeni_doc():
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 4       # mm
    doc.header["$MEASUREMENT"] = 1    # Metric
    for ad, renk, lt in KATMANLAR:
        if lt not in doc.linetypes:
            lt = "CONTINUOUS"
        doc.layers.add(ad, color=renk, linetype=lt)
    if "MCC_STYLE" not in doc.styles:
        doc.styles.add("MCC_STYLE", font="arial.ttf")
    return doc

def yazi(msp, text, x, y, h=300, layer="YAZI", align=TextEntityAlignment.LEFT, rot=0, color=None):
    attr = {"layer": layer, "style": "MCC_STYLE"}
    if color is not None:
        attr["color"] = color
    t = msp.add_text(text, height=h, rotation=rot, dxfattribs=attr)
    t.set_placement((x, y), align=align)
    return t

def antet(msp, pafta_adi, pafta_no, olcek, x0, y0):
    w, h = 15000.0, 6000.0
    msp.add_lwpolyline([(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)],
                       close=True, dxfattribs={"layer": "ANTET", "const_width": 40})
    for yy in (y0 + h - 1400, y0 + h - 2600, y0 + h - 3800, y0 + 1400):
        msp.add_line((x0, yy), (x0 + w, yy), dxfattribs={"layer": "ANTET"})
    
    yazi(msp, "MISIR ENTEGRE ISLEME TESISI - MCC PANOSU", x0 + 400, y0 + h - 1000, h=450, layer="ANTET")
    yazi(msp, pafta_adi, x0 + 400, y0 + h - 2200, h=400, layer="ANTET")
    yazi(msp, "Cizen : Hakan OGUZ", x0 + 400, y0 + h - 3300, h=400, layer="ANTET")
    yazi(msp, "Elektrik Elektronik Muhendisi", x0 + 400, y0 + h - 4400, h=380, layer="ANTET")
    
    xr = x0 + 9500
    msp.add_line((xr, y0 + 1400), (xr, y0), dxfattribs={"layer": "ANTET"})
    yazi(msp, "Tarih", xr + 300, y0 + 1000, h=300, layer="ANTET")
    yazi(msp, "2026-10-27", xr + 300, y0 + 400, h=350, layer="ANTET")
    
    xr2 = x0 + 12500
    msp.add_line((xr2, y0 + 1400), (xr2, y0), dxfattribs={"layer": "ANTET"})
    yazi(msp, "Olcek", xr2 + 300, y0 + 1000, h=300, layer="ANTET")
    yazi(msp, olcek, xr2 + 300, y0 + 400, h=350, layer="ANTET")


def ciz_mcc_guc_kumanda():
    doc = yeni_doc()
    msp = doc.modelspace()

    # Dış Çerçeve (55000 x 36000 mm)
    msp.add_lwpolyline([(0, 0), (55000, 0), (55000, 36000), (0, 36000)],
                       close=True, dxfattribs={"layer": "CERCEVE", "const_width": 50})

    yazi(msp, "MISIR KIRMA & ELEME HATTI MCC GUC VE KUMANDA SEMASI", 2500, 34000, h=650, layer="YAZI")
    yazi(msp, "400V 50Hz 3P+N+PE - VFD Hız Kontrollü Kirici & DOL/Y-D Konveyör Motorlari", 2500, 32800, h=400, layer="YAZI")

    # Ana Dağıtım Barası (Cu 50x5 mm)
    bx0, bx1 = 4000, 50000
    by = 28000
    msp.add_lwpolyline([(bx0, by), (bx1, by)], dxfattribs={"layer": "GUC_HAT", "const_width": 50})
    msp.add_lwpolyline([(bx0, by-400), (bx1, by-400)], dxfattribs={"layer": "GUC_HAT", "const_width": 30})
    yazi(msp, "MCC ANA BARA: 3x(Cu 50x5 mm) In = 630A | Icw = 25 kA / 1s", bx0, by + 600, h=400, layer="GUC_HAT")

    # 4 Motor Kolu (Fiderler):
    # M1: Mısır Çekiçli Kırıcı Değirmen (55 kW - VFD Hız Kontrollü)
    # M2: Pnömatik Taşıma / Aspiratör Fanı (30 kW - Yumuşak Yol Verici / Soft Starter)
    # M3: Döner Elek Tambur Motoru (15 kW - Yıldız-Üçgen Kumandalı)
    # M4: Kovalı Elevatör Besleme Helezonu (7.5 kW - Direkt Yol Verme / DOL)

    motorlar = [
        {"x": 8000,  "kod": "M1", "ad": "Cekicli Kirici Degirmen", "kw": "55 kW", "in": "102 A", "surucu": "VFD (Frekans Konvertoru)", "kablo": "3x50+25 mm2 2YSLCY (Ekranli)", "L": 35, "drop": 0.82},
        {"x": 18000, "kod": "M2", "ad": "Pnömatik Emis Fani",     "kw": "30 kW", "in": "57 A",  "surucu": "Soft Starter",              "kablo": "4x25 mm2 NYY",                "L": 45, "drop": 1.15},
        {"x": 28000, "kod": "M3", "ad": "Döner Elek Tamburu",     "kw": "15 kW", "in": "29 A",  "surucu": "Yildiz-Ucgen (Y/D)",        "kablo": "7x6 mm2 NYY (Cift Besleme)",   "L": 25, "drop": 0.68},
        {"x": 38000, "kod": "M4", "ad": "Kovali Elevator Helezon","kw": "7.5 kW","in": "15.2 A","surucu": "Direkt (DOL) + Termik",    "kablo": "4x4 mm2 NYY",                 "L": 30, "drop": 0.74},
    ]

    for m in motorlar:
        mx = m["x"]
        # Baradan fider inişi
        msp.add_line((mx, by), (mx, 25000), dxfattribs={"layer": "GUC_HAT"})
        
        # Fider Koruma Şalteri (MCCB)
        msp.add_lwpolyline([(mx - 600, 23500), (mx + 600, 23500), (mx + 600, 25000), (mx - 600, 25000)],
                           close=True, dxfattribs={"layer": "PANO_ELEMAN", "const_width": 20})
        msp.add_line((mx - 600, 23500), (mx + 600, 25000), dxfattribs={"layer": "PANO_ELEMAN"})
        yazi(msp, f"QF_{m['kod']}: MCCB", mx + 800, 24400, h=300, layer="PANO_ELEMAN")
        yazi(msp, f"In: {m['in']}", mx + 800, 23800, h=250, layer="PANO_ELEMAN")

        # Şalterden sürücü/kontaktöre hat
        msp.add_line((mx, 23500), (mx, 20500), dxfattribs={"layer": "GUC_HAT"})

        # Sürücü / Kontaktör Bloğu
        msp.add_lwpolyline([(mx - 1200, 16500), (mx + 1200, 16500), (mx + 1200, 20500), (mx - 1200, 20500)],
                           close=True, dxfattribs={"layer": "PANO_ELEMAN", "const_width": 30})
        yazi(msp, m["surucu"], mx - 1000, 19500, h=280, layer="PANO_ELEMAN")
        yazi(msp, f"Guc: {m['kw']}", mx - 1000, 18500, h=260, layer="PANO_ELEMAN")
        yazi(msp, "PLC 4-20mA / Modbus", mx - 1000, 17200, h=220, layer="KUMANDA_HAT")

        # Sürücüden klemens sırasına hat
        msp.add_line((mx, 16500), (mx, 13000), dxfattribs={"layer": "GUC_HAT"})

        # Ray Klemens Grubu
        msp.add_lwpolyline([(mx - 800, 12000), (mx + 800, 12000), (mx + 800, 13000), (mx - 800, 13000)],
                           close=True, dxfattribs={"layer": "PANO_ELEMAN"})
        yazi(msp, f"X1_{m['kod']}: U-V-W-PE", mx - 700, 12400, h=240, layer="PANO_ELEMAN")

        # Klemenslerden Motor Sembolüne
        msp.add_line((mx, 12000), (mx, 9000), dxfattribs={"layer": "MOTOR_HAT"})
        msp.add_circle((mx, 7500), 1200, dxfattribs={"layer": "MOTOR_HAT"})
        yazi(msp, "M", mx - 300, 7800, h=600, layer="MOTOR_HAT")
        yazi(msp, "3~", mx - 250, 7100, h=400, layer="MOTOR_HAT")

        # Motor Bilgi Etiketi
        yazi(msp, m["ad"], mx - 1200, 5600, h=320, layer="YAZI")
        yazi(msp, f"P={m['kw']} | In={m['in']}", mx - 1200, 4900, h=260, layer="YAZI")
        yazi(msp, f"Kablo: {m['kablo']}", mx - 1200, 4300, h=240, layer="MOTOR_HAT")
        yazi(msp, f"L={m['L']}m | %e=%{m['drop']}", mx - 1200, 3700, h=240, layer="OLCU")

    # Tablo: Kablo Kesiti ve Gerilim Düşümü Parametrik Hesabı (Alt Sol Kısım)
    tx, ty = 2500, 22000
    msp.add_lwpolyline([(tx, ty), (tx + 22000, ty), (tx + 22000, ty - 6000), (tx, ty - 6000)],
                       close=True, dxfattribs={"layer": "CERCEVE", "const_width": 30})
    msp.add_line((tx, ty - 1200), (tx + 22000, ty - 1200), dxfattribs={"layer": "CERCEVE"})
    yazi(msp, "MOTOR BESLEME HATLARI GERILIM DUSUMU VE KABLO HESABI", tx + 500, ty - 800, h=350, layer="YAZI")

    satirlar = [
        "M1: 55 kW Kirici -> 3x50+25 mm2 Ekranli Cu -> L=35 m -> %e = %0.82 < %3.0 (Uygun)",
        "M2: 30 kW Fan    -> 4x25 mm2 NYY Cu        -> L=45 m -> %e = %1.15 < %3.0 (Uygun)",
        "M3: 15 kW Elek   -> 7x6 mm2 NYY Cu         -> L=25 m -> %e = %0.68 < %3.0 (Uygun)",
        "M4: 7.5kW Helezon-> 4x4 mm2 NYY Cu         -> L=30 m -> %e = %0.74 < %3.0 (Uygun)",
    ]
    for idx, sat in enumerate(satirlar):
        yazi(msp, sat, tx + 400, ty - 2000 - idx * 1000, h=280, layer="OLCU")

    # Gerçek Ölçülendirme Çizgileri
    msp.add_line((8000, 2000), (38000, 2000), dxfattribs={"layer": "OLCU"})
    yazi(msp, "<--- FIDERLER ARASI MODUL MESAFESI: 10000 mm --->", 17000, 1400, h=320, layer="OLCU")

    antet(msp, "MCC GUC VE MOTOR KUMANDA SEMASI", "MCC-01", "1/50", 38000.0, 500.0)

    dxf_path = os.path.join(OUT, "mcc-guc-kumanda-semasi.dxf")
    doc.saveas(dxf_path)
    return doc


def ciz_mcc_pano_gorunus():
    doc = yeni_doc()
    msp = doc.modelspace()

    # Dış Çerçeve
    msp.add_lwpolyline([(0, 0), (55000, 0), (55000, 36000), (0, 36000)],
                       close=True, dxfattribs={"layer": "CERCEVE", "const_width": 50})

    yazi(msp, "MISIR ENTEGRE ISLEME TESISI MCC PANOSU MEKANIK ON GORUNUS PLANI", 2500, 34000, h=650, layer="YAZI")
    yazi(msp, "Dikili Tip Form 3b Cekmeceli/Sabit Moduler Pano: 3200 x 2100 x 800 mm (4 Goz x 800 mm), IP54", 2500, 32800, h=400, layer="YAZI")

    px0, py0 = 5000, 7000
    col_w = 8000   # 800 mm sütun (10x ölçek)
    p_h   = 21000  # 2100 mm yükseklik
    baza  = 1500   # 150 mm baza

    # 4 Gözlü Pano Dış Gövdesi
    total_w = 4 * col_w
    msp.add_lwpolyline([(px0, py0 - baza), (px0 + total_w, py0 - baza), (px0 + total_w, py0), (px0, py0)],
                       close=True, dxfattribs={"layer": "PANO_KARKAS", "const_width": 30})
    yazi(msp, "BAZA 150 mm (Kablo Giris & Havalandirma Menfezi)", px0 + 10000, py0 - 1000, h=350, layer="PANO_KARKAS")

    msp.add_lwpolyline([(px0, py0), (px0 + total_w, py0), (px0 + total_w, py0 + p_h), (px0, py0 + p_h)],
                       close=True, dxfattribs={"layer": "PANO_KARKAS", "const_width": 60})

    sutunlar = [
        ("GOZ 1: ANA GIRIS & 55 kW VFD", "Kirici Degirmen VFD"),
        ("GOZ 2: 30 kW SOFT STARTER",   "Aspirator Fani"),
        ("GOZ 3: Y-D & DOL YOLLAYICILAR","Elek ve Helezonlar"),
        ("GOZ 4: PLC & OTOMASYON GOZU",  "Siemens S7-1500 + HMI"),
    ]

    for idx, (baslik, aciklama) in enumerate(sutunlar):
        cx = px0 + idx * col_w
        # Sütun bölme çizgisi
        if idx > 0:
            msp.add_lwpolyline([(cx, py0), (cx, py0 + p_h)], dxfattribs={"layer": "PANO_KARKAS", "const_width": 30})

        yazi(msp, baslik, cx + 500, py0 + p_h + 800, h=320, layer="YAZI")
        yazi(msp, aciklama, cx + 500, py0 + p_h + 300, h=260, layer="YAZI")

        # Üst Bara Bölmesi Kapağı
        msp.add_lwpolyline([(cx + 300, py0 + p_h - 3000), (cx + col_w - 300, py0 + p_h - 3000), 
                            (cx + col_w - 300, py0 + p_h - 400), (cx + 300, py0 + p_h - 400)],
                           close=True, dxfattribs={"layer": "PANO_ELEMAN"})
        yazi(msp, "BARA BOLMESI", cx + 2200, py0 + p_h - 1800, h=300, layer="PANO_ELEMAN")

        # Cihaz Bölmeleri (Kapaklar ve Havalandırma Izgaraları)
        if idx == 0:
            # Göz 1: 55 kW VFD Cihazı + Filtre Fanı
            msp.add_lwpolyline([(cx + 800, py0 + 5000), (cx + col_w - 800, py0 + 5000), 
                                (cx + col_w - 800, py0 + 17000), (cx + 800, py0 + 17000)],
                               close=True, dxfattribs={"layer": "PANO_ELEMAN", "const_width": 30})
            yazi(msp, "VFD SURUCU (55 kW)", cx + 1800, py0 + 14000, h=400, layer="PANO_ELEMAN")
            yazi(msp, "Kırıcı Frekans Konvertörü", cx + 1400, py0 + 12800, h=300, layer="PANO_ELEMAN")
            # Fan Izgarası
            msp.add_lwpolyline([(cx + 2000, py0 + 6000), (cx + col_w - 2000, py0 + 6000), 
                                (cx + col_w - 2000, py0 + 9500), (cx + 2000, py0 + 9500)],
                               close=True, dxfattribs={"layer": "PANO_ELEMAN"})
            yazi(msp, "Cebri Havalandirma Fani", cx + 2200, py0 + 7800, h=250, layer="PANO_ELEMAN")
        elif idx == 3:
            # Göz 4: PLC ve Dokunmatik Operatör Paneli (HMI)
            msp.add_lwpolyline([(cx + 1200, py0 + 11000), (cx + col_w - 1200, py0 + 11000), 
                                (cx + col_w - 1200, py0 + 16500), (cx + 1200, py0 + 16500)],
                               close=True, dxfattribs={"layer": "PANO_ELEMAN", "const_width": 30})
            yazi(msp, "10'' RENKLI HMI PANEL", cx + 1800, py0 + 14000, h=380, layer="PANO_ELEMAN")
            yazi(msp, "Proses Canli Izleme Ekrani", cx + 1600, py0 + 13000, h=260, layer="PANO_ELEMAN")
            # Sinyal Lambaları ve Butonlar
            for b_idx in range(4):
                bx_btn = cx + 1600 + b_idx * 1400
                msp.add_circle((bx_btn, py0 + 9000), 350, dxfattribs={"layer": "PANO_ELEMAN"})
            yazi(msp, "Start / Stop / Acil Durdurma / Ariza Reset Butonlari", cx + 800, py0 + 7800, h=240, layer="PANO_ELEMAN")

    # Gerçek Ölçülendirme Çizgileri
    msp.add_line((px0, py0 - 2500), (px0 + total_w, py0 - 2500), dxfattribs={"layer": "OLCU"})
    yazi(msp, "<--- TOPLAM MCC GENISLIGI: 3200 mm (4 Modul x 800 mm) --->", px0 + 7000, py0 - 3200, h=350, layer="OLCU")

    msp.add_line((px0 - 1500, py0), (px0 - 1500, py0 + p_h), dxfattribs={"layer": "OLCU"})
    yazi(msp, "<--- YUKSEKLIK: 2100 mm --->", px0 - 2200, py0 + 8000, h=350, layer="OLCU", rot=90)

    antet(msp, "MCC PANO MEKANIK ON GORUNUS PLANI", "MCC-02", "1/20", 38000.0, 500.0)

    dxf_path = os.path.join(OUT, "mcc-pano-mekanik-yerlesimi.dxf")
    doc.saveas(dxf_path)
    return doc


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
    os.makedirs(SEK, exist_ok=True)
    print("MCC Guc ve Kumanda Semasi ciziliyor...")
    d1 = ciz_mcc_guc_kumanda()
    render_png(d1, os.path.join(SEK, "mcc-guc-kumanda.png"))
    
    print("MCC Pano Mekanik Yerlesimi ciziliyor...")
    d2 = ciz_mcc_pano_gorunus()
    render_png(d2, os.path.join(SEK, "mcc-pano-yerlesimi.png"))
    
    print("TAMAMLANDI: 2 DXF ve 2 PNG uretildi.")

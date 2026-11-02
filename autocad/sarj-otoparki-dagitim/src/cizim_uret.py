# Author : Hakan OĞUZ - Elektrik Elektronik Mühendisi
# Project: 20 AC + 4 DC Şarj İstasyonlu Otopark Elektrik Dağıtım Projesi
# Date   : 2026-10-28
# License: MIT
# Desc   : 1000 kVA trafo, 20x22 kW AC Tip-2 soket, 4x120 kW DC CCS hızlı şarj, kablo tavası, dinamik yük yönetimi (DLM) ve tek hat şeması.

import os
import ezdxf
from ezdxf.enums import TextEntityAlignment

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.abspath(os.path.join(HERE, ".."))
SEK  = os.path.join(OUT, "sekiller")

KATMANLAR = [
    ("CERCEVE", 7, "CONTINUOUS"),
    ("OTOPARK_MIMARI", 8, "CONTINUOUS"), # Gri otopark çizgileri, park cepleri
    ("KABLO_TAVASI", 1, "DASHED"),       # Kırmızı kablo tavası güzergahı
    ("AC_SARJ", 3, "CONTINUOUS"),        # Yeşil 22 kW AC şarj noktaları
    ("DC_SARJ", 5, "CONTINUOUS"),        # Mavi 120 kW DC hızlı şarj istasyonları
    ("TRAFO_VE_PANO", 4, "CONTINUOUS"),  # Camgöbeği trafo ve ana dağıtım panosu
    ("DLM_HABERLESME", 6, "DASHDOT"),    # Mor RS485/Modbus dinamik yük yönetimi hattı
    ("OLCU", 8, "CONTINUOUS"),
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
    if "EV_STYLE" not in doc.styles:
        doc.styles.add("EV_STYLE", font="arial.ttf")
    return doc

def yazi(msp, text, x, y, h=300, layer="YAZI", align=TextEntityAlignment.LEFT, rot=0, color=None):
    attr = {"layer": layer, "style": "EV_STYLE"}
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
    
    yazi(msp, "EV SARJ OTOPARKI ELEKTRIK DAGITIM PROJESI", x0 + 400, y0 + h - 1000, h=450, layer="ANTET")
    yazi(msp, pafta_adi, x0 + 400, y0 + h - 2200, h=400, layer="ANTET")
    yazi(msp, "Cizen : Hakan OGUZ", x0 + 400, y0 + h - 3300, h=400, layer="ANTET")
    yazi(msp, "Elektrik Elektronik Muhendisi", x0 + 400, y0 + h - 4400, h=380, layer="ANTET")
    
    xr = x0 + 9500
    msp.add_line((xr, y0 + 1400), (xr, y0), dxfattribs={"layer": "ANTET"})
    yazi(msp, "Tarih", xr + 300, y0 + 1000, h=300, layer="ANTET")
    yazi(msp, "2026-10-28", xr + 300, y0 + 400, h=350, layer="ANTET")
    
    xr2 = x0 + 12500
    msp.add_line((xr2, y0 + 1400), (xr2, y0), dxfattribs={"layer": "ANTET"})
    yazi(msp, "Olcek", xr2 + 300, y0 + 1000, h=300, layer="ANTET")
    yazi(msp, olcek, xr2 + 300, y0 + 400, h=350, layer="ANTET")


def ciz_otopark_yerlesimi():
    doc = yeni_doc()
    msp = doc.modelspace()

    # Çerçeve (55000 x 36000 mm)
    msp.add_lwpolyline([(0, 0), (55000, 0), (55000, 36000), (0, 36000)],
                       close=True, dxfattribs={"layer": "CERCEVE", "const_width": 50})

    yazi(msp, "20 AC (22 kW) + 4 DC (120 kW) EV SARJ OTOPARKI YERLESIM VE KABLO TAVASI PLANI", 2500, 34000, h=600, layer="YAZI")
    yazi(msp, "1000 kVA Kompakt Trafo Merkezi, 400x100 mm Agir Hizmet Tavalari, Dinamik Yuk Yonetimi (DLM)", 2500, 32800, h=380, layer="YAZI")

    # 1. Trafo ve Ana Dağıtım Merkezi (Sol Kenarda)
    tx, ty = 4000, 16000
    msp.add_lwpolyline([(tx, ty), (tx + 5000, ty), (tx + 5000, ty + 7000), (tx, ty + 7000)],
                       close=True, dxfattribs={"layer": "TRAFO_VE_PANO", "const_width": 40})
    yazi(msp, "KOMPAKT TRAFO", tx + 500, ty + 5500, h=350, layer="TRAFO_VE_PANO")
    yazi(msp, "MERKEZI (1000 kVA)", tx + 400, ty + 4600, h=300, layer="TRAFO_VE_PANO")
    yazi(msp, "34.5 / 0.4 kV Dyn11", tx + 500, ty + 3800, h=260, layer="TRAFO_VE_PANO")
    yazi(msp, "Ana AG Pano (1600A)", tx + 500, ty + 2400, h=300, layer="TRAFO_VE_PANO")
    yazi(msp, "+ DLM Kontrol Panosu", tx + 400, ty + 1600, h=260, layer="DLM_HABERLESME")

    # 2. Ana Kablo Tavası Omurgası (Trafodan sağa uzanan 400x100 mm tava)
    tava_y = ty + 3500
    msp.add_lwpolyline([(tx + 5000, tava_y), (48000, tava_y)], dxfattribs={"layer": "KABLO_TAVASI", "const_width": 40})
    yazi(msp, "ANA KABLO TAVASI 400x100 mm (Agir Hizmet Tipi Galvaniz Sac)", tx + 6000, tava_y + 400, h=320, layer="KABLO_TAVASI")

    # 3. Kuzey Otopark Sırası: 10 Adet 22 kW AC Şarj İstasyonu (Park Cep Boyutu: 2500 x 5000 mm)
    park_y_kuzey = tava_y + 4000
    for i in range(10):
        px = 12000 + i * 3200
        # Park cebi çizgisi
        msp.add_lwpolyline([(px, park_y_kuzey), (px + 2800, park_y_kuzey), (px + 2800, park_y_kuzey + 5000), (px, park_y_kuzey + 5000)],
                           close=True, dxfattribs={"layer": "OTOPARK_MIMARI"})
        yazi(msp, f"EV-{i+1}", px + 800, park_y_kuzey + 2200, h=300, layer="OTOPARK_MIMARI")
        
        # AC Şarj Kutusu Sembolü (Duvarda/Kaldırımda)
        msp.add_lwpolyline([(px + 900, park_y_kuzey + 4600), (px + 1900, park_y_kuzey + 4600), 
                            (px + 1900, park_y_kuzey + 5300), (px + 900, park_y_kuzey + 5300)],
                           close=True, dxfattribs={"layer": "AC_SARJ", "const_width": 20})
        yazi(msp, "22kW", px + 950, park_y_kuzey + 4800, h=220, layer="AC_SARJ")
        
        # Tavadan Şarj Cihazına İniş
        msp.add_line((px + 1400, tava_y), (px + 1400, park_y_kuzey + 4600), dxfattribs={"layer": "KABLO_TAVASI"})

    # 4. Güney Otopark Sırası: 10 Adet 22 kW AC Şarj İstasyonu
    park_y_guney = tava_y - 9000
    for i in range(10):
        px = 12000 + i * 3200
        msp.add_lwpolyline([(px, park_y_guney), (px + 2800, park_y_guney), (px + 2800, park_y_guney + 5000), (px, park_y_guney + 5000)],
                           close=True, dxfattribs={"layer": "OTOPARK_MIMARI"})
        yazi(msp, f"EV-{i+11}", px + 600, park_y_guney + 2200, h=300, layer="OTOPARK_MIMARI")
        
        msp.add_lwpolyline([(px + 900, park_y_guney - 300), (px + 1900, park_y_guney - 300), 
                            (px + 1900, park_y_guney + 400), (px + 900, park_y_guney + 400)],
                           close=True, dxfattribs={"layer": "AC_SARJ", "const_width": 20})
        yazi(msp, "22kW", px + 950, park_y_guney - 100, h=220, layer="AC_SARJ")
        
        msp.add_line((px + 1400, tava_y), (px + 1400, park_y_guney + 400), dxfattribs={"layer": "KABLO_TAVASI"})

    # 5. Batı/Doğu Kısmı: 4 Adet 120 kW DC CCS Hızlı Şarj İstasyonu (Geniş Araç Cepleri)
    dc_x0 = 46000
    for j in range(4):
        dc_y = 6000 + j * 6500
        # DC İstasyon Park Cebi (3500 x 6000 mm)
        msp.add_lwpolyline([(dc_x0, dc_y), (dc_x0 + 4000, dc_y), (dc_x0 + 4000, dc_y + 5500), (dc_x0, dc_y + 5500)],
                           close=True, dxfattribs={"layer": "OTOPARK_MIMARI"})
        yazi(msp, f"DC-{j+1}", dc_x0 + 1200, dc_y + 2500, h=350, layer="DC_SARJ")
        
        # DC Hızlı Şarj Kiosku
        msp.add_lwpolyline([(dc_x0 + 4200, dc_y + 1200), (dc_x0 + 5600, dc_y + 1200), 
                            (dc_x0 + 5600, dc_y + 4200), (dc_x0 + 4200, dc_y + 4200)],
                           close=True, dxfattribs={"layer": "DC_SARJ", "const_width": 30})
        yazi(msp, "120 kW", dc_x0 + 4350, dc_y + 2800, h=260, layer="DC_SARJ")
        yazi(msp, "CCS2", dc_x0 + 4450, dc_y + 2000, h=240, layer="DC_SARJ")

    # 6. Dinamik Yük Yönetimi (DLM) Açıklama Tablosu
    yazi(msp, "DINAMIK YUK YONETIMI (DLM) VE ESZAMANLILIK STRATEJISI:", 2500, 5500, h=350, layer="YAZI")
    notlar = [
        "1. Toplam Bagli Guc: 20x22 kW (AC) + 4x120 kW (DC) = 440 + 480 = 920 kW.",
        "2. Trafo Kapasitesi: 1000 kVA (Cos phi = 0.95 iken P_aktif_max = 950 kW).",
        "3. Eszamanlilik Faktoru: AC soketler icin k_es = 0.60, DC hizli sarj icin k_es = 0.85 -> Talep Gucu = 672 kW.",
        "4. DLM Mantigi: Trafo yuklenme orani %90'i astiginda (P > 850 kW), AC sarj istasyonlarinin akim limiti PLC/OCPP tarafindan 32A'den 16A'e dusurulur.",
        "5. Koruma ve RCD: Her AC sarj fiderinde Tip-B (6mA DC kacak algilayan) 30mA RCD ve 4P 40A C-Tipi MCB kullanilmistir.",
    ]
    for idx, n in enumerate(notlar):
        yazi(msp, n, 2500, 4800 - idx * 480, h=250, layer="YAZI")

    antet(msp, "EV SARJ OTOPARKI DAGITIM PLANI", "EV-01", "1/100", 38000.0, 500.0)

    dxf_path = os.path.join(OUT, "sarj-otoparki-yerlesimi.dxf")
    doc.saveas(dxf_path)
    return doc


def ciz_otopark_tek_hat():
    doc = yeni_doc()
    msp = doc.modelspace()

    # Çerçeve
    msp.add_lwpolyline([(0, 0), (55000, 0), (55000, 36000), (0, 36000)],
                       close=True, dxfattribs={"layer": "CERCEVE", "const_width": 50})

    yazi(msp, "1000 kVA TRAFO VE EV SARJ ANA DAGITIM PANOSU (ADP) TEK HAT SEMASI", 2500, 34000, h=650, layer="YAZI")
    yazi(msp, "1600 A Ana Bara, 4x200A DC Fiderleri, 4x(5x22kW) AC Alt Dagitim Gruplari, Tip B RCD", 2500, 32800, h=400, layer="YAZI")

    # Trafo Girişi (Sol Üst)
    tx, ty = 6000, 27500
    msp.add_circle((tx, ty + 1200), 1000, dxfattribs={"layer": "TRAFO_VE_PANO"})
    msp.add_circle((tx, ty), 1000, dxfattribs={"layer": "TRAFO_VE_PANO"})
    yazi(msp, "1000 kVA TRAFO", tx + 1400, ty + 800, h=380, layer="TRAFO_VE_PANO")
    yazi(msp, "34.5 / 0.4 kV, In=1443 A", tx + 1400, ty + 200, h=320, layer="TRAFO_VE_PANO")

    # Ana Giriş Şalteri (1600 A ACB - Havalı Şalter)
    msp.add_line((tx, ty - 1000), (tx, 22500), dxfattribs={"layer": "TRAFO_VE_PANO"})
    msp.add_lwpolyline([(tx - 800, 21000), (tx + 800, 21000), (tx + 800, 22500), (tx - 800, 22500)],
                       close=True, dxfattribs={"layer": "TRAFO_VE_PANO", "const_width": 30})
    msp.add_line((tx - 800, 21000), (tx + 800, 22500), dxfattribs={"layer": "TRAFO_VE_PANO"})
    yazi(msp, "QF1: 3P 1600A ACB (Havalı Şalter)", tx + 1200, 22000, h=380, layer="TRAFO_VE_PANO")
    yazi(msp, "Icu = 50 kA | Micrologic E Korumali", tx + 1200, 21300, h=300, layer="TRAFO_VE_PANO")

    # Ana Bakır Bara (2x Cu 80x10 mm / In = 1800 A)
    bx0, bx1 = 4000, 50000
    by = 17500
    msp.add_lwpolyline([(bx0, by), (bx1, by)], dxfattribs={"layer": "GUC_HAT", "const_width": 50})
    msp.add_lwpolyline([(bx0, by - 400), (bx1, by - 400)], dxfattribs={"layer": "GUC_HAT", "const_width": 30})
    msp.add_line((tx, 21000), (tx, by), dxfattribs={"layer": "GUC_HAT"})
    yazi(msp, "ANA BARA: 2x(Cu 80x10 mm) In = 1800 A - l_cw = 50 kA / 1s", bx0, by + 600, h=400, layer="GUC_HAT")

    # Fider Grupları: 4 DC Hızlı Şarj (Her biri 120 kW) + 4 Grup AC Pano (Her grup 5x22 kW)
    fiderler_ev = [
        {"x": 10000, "kod": "DC-1", "guc": "120 kW", "salter": "250A MCCB", "kablo": "3x150+70 mm2 NYY"},
        {"x": 15000, "kod": "DC-2", "guc": "120 kW", "salter": "250A MCCB", "kablo": "3x150+70 mm2 NYY"},
        {"x": 20000, "kod": "DC-3", "guc": "120 kW", "salter": "250A MCCB", "kablo": "3x150+70 mm2 NYY"},
        {"x": 25000, "kod": "DC-4", "guc": "120 kW", "salter": "250A MCCB", "kablo": "3x150+70 mm2 NYY"},
        {"x": 31000, "kod": "AC_GR1", "guc": "5x22 kW (110kW)", "salter": "200A MCCB", "kablo": "3x95+50 mm2 NYY"},
        {"x": 37000, "kod": "AC_GR2", "guc": "5x22 kW (110kW)", "salter": "200A MCCB", "kablo": "3x95+50 mm2 NYY"},
        {"x": 43000, "kod": "AC_GR3", "guc": "5x22 kW (110kW)", "salter": "200A MCCB", "kablo": "3x95+50 mm2 NYY"},
        {"x": 48000, "kod": "AC_GR4", "guc": "5x22 kW (110kW)", "salter": "200A MCCB", "kablo": "3x95+50 mm2 NYY"},
    ]

    for fe in fiderler_ev:
        fx = fe["x"]
        msp.add_line((fx, by), (fx, 14000), dxfattribs={"layer": "GUC_HAT"})
        # Şalter
        msp.add_lwpolyline([(fx - 500, 12600), (fx + 500, 12600), (fx + 500, 13800), (fx - 500, 13800)],
                           close=True, dxfattribs={"layer": "TRAFO_VE_PANO", "const_width": 20})
        msp.add_line((fx - 500, 12600), (fx + 500, 13800), dxfattribs={"layer": "TRAFO_VE_PANO"})
        
        # Çıkış kutusu
        msp.add_line((fx, 12600), (fx, 9000), dxfattribs={"layer": "GUC_HAT"})
        msp.add_lwpolyline([(fx - 700, 7800), (fx + 700, 7800), (fx + 700, 8800), (fx - 700, 8800)],
                           close=True, dxfattribs={"layer": "GUC_HAT"})
        
        yazi(msp, fe["kod"], fx - 600, 15000, h=300, layer="YAZI", rot=90)
        yazi(msp, fe["salter"], fx + 600, 13300, h=250, layer="TRAFO_VE_PANO")
        yazi(msp, fe["kablo"], fx + 200, 10800, h=230, layer="KABLO_TAVASI", rot=90)
        yazi(msp, fe["guc"], fx - 650, 8200, h=220, layer="YAZI")

    antet(msp, "EV SARJ OTOPARKI TEK HAT SEMASI", "EV-02", "1/50", 38000.0, 500.0)

    dxf_path = os.path.join(OUT, "sarj-otoparki-tek-hat.dxf")
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
    print("Sarj Otoparki Yerlesimi ciziliyor...")
    d1 = ciz_otopark_yerlesimi()
    render_png(d1, os.path.join(SEK, "sarj-otoparki-yerlesimi.png"))
    
    print("Sarj Otoparki Tek Hat Semasi ciziliyor...")
    d2 = ciz_otopark_tek_hat()
    render_png(d2, os.path.join(SEK, "sarj-otoparki-tek-hat.png"))
    
    print("TAMAMLANDI: 2 DXF ve 2 PNG uretildi.")

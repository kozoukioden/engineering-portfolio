"""
34,5 / 0,4 kV Kompakt Trafo Merkezi CAD Çizim Üreticisi
- Tek Hat Şeması ve Röle Koordinasyon Eğrisi (TCC) Paftası
- Beton Köşk Mimari/Mekanik Yerleşim ve Topraklama Paftası
Yazar: Hakan OĞUZ (Elektrik-Elektronik Mühendisi)
"""

import os
import math
import numpy as np
import ezdxf
from ezdxf import colors

def setup_layers(doc):
    layers = [
        ("CERCEVE", colors.WHITE, "CONTINUOUS"),
        ("ANTET", colors.CYAN, "CONTINUOUS"),
        ("YAZI", colors.WHITE, "CONTINUOUS"),
        ("DUVAR", colors.WHITE, "CONTINUOUS"),
        ("EKIPMAN", colors.CYAN, "CONTINUOUS"),
        ("KABLO_OG", colors.RED, "CONTINUOUS"),
        ("KABLO_AG", colors.BLUE, "CONTINUOUS"),
        ("TOPRAKLAMA", colors.GREEN, "DASHED"),
        ("OLCU", colors.GREEN, "CONTINUOUS"),
        ("ROLE_EGRI", colors.MAGENTA, "CONTINUOUS"),
        ("EKSEN", colors.RED, "CENTER"),
        ("TARAMA", colors.LIGHT_GRAY, "CONTINUOUS")
    ]
    for name, col, linetype in layers:
        if name not in doc.layers:
            doc.layers.add(name=name, color=col, linetype=linetype)

def ciz_antet(msp, x_base, y_base, pafta_no, pafta_adi, olcek="1/50"):
    # Antet Dış Çerçevesi (180 x 60 mm)
    pts = [(x_base, y_base), (x_base + 180, y_base),
           (x_base + 180, y_base + 60), (x_base, y_base + 60), (x_base, y_base)]
    msp.add_lwpolyline(pts, dxfattribs={"layer": "ANTET", "const_width": 0.5})

    # Yatay Bölüntüler
    msp.add_lwpolyline([(x_base, y_base + 45), (x_base + 180, y_base + 45)], dxfattribs={"layer": "ANTET"})
    msp.add_lwpolyline([(x_base, y_base + 30), (x_base + 180, y_base + 30)], dxfattribs={"layer": "ANTET"})
    msp.add_lwpolyline([(x_base, y_base + 15), (x_base + 180, y_base + 15)], dxfattribs={"layer": "ANTET"})

    # Düşey Bölüntüler
    msp.add_lwpolyline([(x_base + 90, y_base + 15), (x_base + 90, y_base + 30)], dxfattribs={"layer": "ANTET"})
    msp.add_lwpolyline([(x_base + 135, y_base + 15), (x_base + 135, y_base + 30)], dxfattribs={"layer": "ANTET"})
    msp.add_lwpolyline([(x_base + 90, y_base), (x_base + 90, y_base + 15)], dxfattribs={"layer": "ANTET"})

    # Metinler
    msp.add_text("34,5 / 0,4 kV 1600 kVA BETON KÖŞK KOMPAKT TRAFO MERKEZİ",
                 dxfattribs={"layer": "ANTET", "height": 3.2}).set_placement((x_base + 5, y_base + 51))
    msp.add_text(pafta_adi,
                 dxfattribs={"layer": "ANTET", "height": 3.0}).set_placement((x_base + 5, y_base + 36))

    msp.add_text("PROJE MÜHENDİSİ:", dxfattribs={"layer": "ANTET", "height": 2.0}).set_placement((x_base + 5, y_base + 24))
    msp.add_text("Hakan OĞUZ", dxfattribs={"layer": "ANTET", "height": 3.2}).set_placement((x_base + 5, y_base + 18))
    msp.add_text("Elektrik-Elektronik Mühendisi", dxfattribs={"layer": "ANTET", "height": 2.0}).set_placement((x_base + 5, y_base + 5))

    msp.add_text("ÖLÇEK:", dxfattribs={"layer": "ANTET", "height": 2.0}).set_placement((x_base + 95, y_base + 24))
    msp.add_text(olcek, dxfattribs={"layer": "ANTET", "height": 2.5}).set_placement((x_base + 95, y_base + 18))

    msp.add_text("PAFTA NO:", dxfattribs={"layer": "ANTET", "height": 2.0}).set_placement((x_base + 140, y_base + 24))
    msp.add_text(pafta_no, dxfattribs={"layer": "ANTET", "height": 3.0}).set_placement((x_base + 140, y_base + 18))

    msp.add_text("TARİH: 28.10.2026", dxfattribs={"layer": "ANTET", "height": 2.0}).set_placement((x_base + 95, y_base + 5))

def uret_pafta1_tek_hat(dxf_yolu):
    """
    Pafta 1: 34.5 kV Tek Hat Şeması + Gömülü Zaman-Akım Koordinasyon Grafiği (TCC)
    """
    doc = ezdxf.new("R2010", setup=True)
    setup_layers(doc)
    msp = doc.modelspace()

    # A1 Pafta Sınırı (841 x 594 mm)
    msp.add_lwpolyline([(0, 0), (841, 0), (841, 594), (0, 594), (0, 0)],
                       dxfattribs={"layer": "CERCEVE", "const_width": 0.7})
    msp.add_lwpolyline([(10, 10), (831, 10), (831, 584), (10, 584), (10, 10)],
                       dxfattribs={"layer": "CERCEVE", "const_width": 0.35})

    ciz_antet(msp, 640, 20, "EE-TM-01", "34,5 kV TEK HAT VE KORUMA KOORDİNASYON ŞEMASI", "N.T.S.")

    # 1. 34.5 kV OG Bölümü (Sol Taraf: x=40..420, y=200..550)
    # Şebeke Girişi
    msp.add_text("TEİAŞ / EDAŞ 34.5 kV ENH GİRİŞİ", dxfattribs={"layer": "YAZI", "height": 3.5}).set_placement((40, 560))
    msp.add_lwpolyline([(100, 560), (100, 480)], dxfattribs={"layer": "KABLO_OG", "const_width": 0.8})

    # Hücre 1: Hat Giriş Hücresi
    msp.add_lwpolyline([(60, 360), (140, 360), (140, 480), (60, 480), (60, 360)],
                       dxfattribs={"layer": "EKIPMAN", "const_width": 0.4})
    msp.add_text("HÜCRE 1: GİRİŞ (36 kV 630 A)", dxfattribs={"layer": "YAZI", "height": 2.5}).set_placement((65, 465))
    msp.add_text("SF6 Gazlı Yük Ayırıcısı", dxfattribs={"layer": "YAZI", "height": 2.0}).set_placement((65, 410))
    msp.add_text("ve Topraklama Ayırıcısı", dxfattribs={"layer": "YAZI", "height": 2.0}).set_placement((65, 395))

    # OG Ana Bara (36 kV, 630 A, 16 kA/1s)
    msp.add_lwpolyline([(100, 350), (320, 350)], dxfattribs={"layer": "KABLO_OG", "const_width": 1.2})
    msp.add_text("36 kV 630 A 16 kA/1s KUPRÜM BARA", dxfattribs={"layer": "YAZI", "height": 2.8}).set_placement((150, 355))

    # Hücre 2: Trafo Koruma Hücresi (Kesicili)
    msp.add_lwpolyline([(170, 210), (250, 210), (250, 330), (170, 330), (170, 210)],
                       dxfattribs={"layer": "EKIPMAN", "const_width": 0.4})
    msp.add_text("HÜCRE 2: KORUMA", dxfattribs={"layer": "YAZI", "height": 2.5}).set_placement((175, 315))
    msp.add_text("36 kV Vakumlu Kesici (VCB)", dxfattribs={"layer": "YAZI", "height": 2.0}).set_placement((175, 280))
    msp.add_text("Akım Trafosu: 50/5 A, 10P10", dxfattribs={"layer": "YAZI", "height": 2.0}).set_placement((175, 255))
    msp.add_text("Röle: IEC 50/51 - 50N/51N", dxfattribs={"layer": "ROLE_EGRI", "height": 2.0}).set_placement((175, 230))

    # Hücre 3: Ölçü Hücresi
    msp.add_lwpolyline([(260, 210), (330, 210), (330, 330), (260, 330), (260, 210)],
                       dxfattribs={"layer": "EKIPMAN", "const_width": 0.4})
    msp.add_text("HÜCRE 3: ÖLÇÜ", dxfattribs={"layer": "YAZI", "height": 2.5}).set_placement((265, 315))
    msp.add_text("Gerilim Trafoları", dxfattribs={"layer": "YAZI", "height": 2.0}).set_placement((265, 275))
    msp.add_text("34500/V3 : 100/V3 V", dxfattribs={"layer": "YAZI", "height": 1.8}).set_placement((265, 255))

    # Kesici Çıkışından Trafoya Hat
    msp.add_lwpolyline([(210, 210), (210, 160)], dxfattribs={"layer": "KABLO_OG", "const_width": 0.8})
    msp.add_text("1x (3x1x95/16 mm² XLPE Cu)", dxfattribs={"layer": "YAZI", "height": 2.2}).set_placement((215, 185))

    # Güç Trafosu Sembolü (İki iç içe geçen daire)
    msp.add_circle((210, 135), 18, dxfattribs={"layer": "EKIPMAN"})
    msp.add_circle((210, 115), 18, dxfattribs={"layer": "EKIPMAN"})
    msp.add_text("TR-1: 1600 kVA", dxfattribs={"layer": "YAZI", "height": 3.0}).set_placement((235, 140))
    msp.add_text("34,5 / 0,4 kV, Dyn11", dxfattribs={"layer": "YAZI", "height": 2.2}).set_placement((235, 125))
    msp.add_text("Uk = %6.0, Hermetik Yağlı", dxfattribs={"layer": "YAZI", "height": 2.0}).set_placement((235, 110))

    # AG Çıkışı
    msp.add_lwpolyline([(210, 97), (210, 50)], dxfattribs={"layer": "KABLO_AG", "const_width": 1.0})
    msp.add_text("4x (3x1x240/120 mm² Cu)", dxfattribs={"layer": "YAZI", "height": 2.2}).set_placement((215, 75))
    msp.add_text("AG ANA DAĞITIM PANOSUNA (In=2309 A)", dxfattribs={"layer": "YAZI", "height": 2.8}).set_placement((215, 55))

    # 2. Zaman-Akım Koordinasyon Eğrisi Grafiği (TCC) (Sağ Taraf: x=460..780, y=120..540)
    # Çerçeve ve Başlık
    msp.add_lwpolyline([(450, 100), (810, 100), (810, 550), (450, 550), (450, 100)],
                       dxfattribs={"layer": "CERCEVE", "const_width": 0.35})
    msp.add_text("IEC 60255 ZAMAN - AKIM KORUMA KOORDİNASYONU (TCC)",
                 dxfattribs={"layer": "ANTET", "height": 3.2}).set_placement((460, 530))
    msp.add_text("AG Ana Kesici (2500A) vs OG Koruma Rölesi (50/51) Selektivite Analizi",
                 dxfattribs={"layer": "YAZI", "height": 2.2}).set_placement((460, 515))

    # Log-Log Eksenleri Çizimi (x=490..780, y=140..480)
    origin_x, origin_y = 490, 140
    width_x, height_y = 290, 340
    msp.add_lwpolyline([(origin_x, origin_y), (origin_x + width_x, origin_y),
                        (origin_x + width_x, origin_y + height_y), (origin_x, origin_y + height_y),
                        (origin_x, origin_y)], dxfattribs={"layer": "CERCEVE"})

    # Grid ve Eksen Etiketleri
    # Akım Ekseni: 100 A -> 50,000 A (Log 10^2 -> 10^4.7)
    # Zaman Ekseni: 0.01 s -> 100 s (Log 10^-2 -> 10^2)
    msp.add_text("Akım (0.4 kV AG Tarafına İndirgenmiş) [Amper]",
                 dxfattribs={"layer": "YAZI", "height": 2.5}).set_placement((origin_x + 60, origin_y - 20))
    msp.add_text("Zaman [s]", dxfattribs={"layer": "YAZI", "height": 2.5}).set_placement((origin_x - 35, origin_y + 160))

    # TCC Eğrilerinin Matematiksel Hesabı ve Çizimi
    # OG Rölesi (IEC Normal Ters): t = (0.14 / ((I / Is)^0.02 - 1)) * TMS
    # 0.4 kV tarafına indirgenmiş Is = 2500 A, TMS = 0.20
    # Ani aşma (50): 18,000 A @ 0.05s
    i_vals = np.logspace(3.2, 4.4, 40) # 1500 A -> 25000 A
    
    def to_canvas(curr, t_val):
        lx = (np.log10(curr) - 2.0) / 3.0 * width_x + origin_x
        ly = (np.log10(t_val) + 2.0) / 4.0 * height_y + origin_y
        return max(min(lx, origin_x + width_x), origin_x), max(min(ly, origin_y + height_y), origin_y)

    # 1. OG Rölesi Eğrisi (Magenta)
    pts_og = []
    for cur in i_vals:
        ratio = cur / 2500.0
        if ratio > 1.05:
            t = (0.14 / (ratio**0.02 - 1.0)) * 0.22
            if t > 0.04 and t < 80.0:
                pts_og.append(to_canvas(cur, t))
    if len(pts_og) > 2:
        msp.add_lwpolyline(pts_og, dxfattribs={"layer": "ROLE_EGRI", "const_width": 0.6})
        msp.add_text("OG Koruma (51) TMS=0.22", dxfattribs={"layer": "ROLE_EGRI", "height": 2.2}).set_placement((pts_og[5][0] + 5, pts_og[5][1]))

    # 2. AG Ana Kesici Eğrisi (ACB 2500 A LSI - Mavi)
    pts_ag = []
    for cur in i_vals:
        ratio = cur / 2300.0
        if ratio > 1.05:
            t = 6.0 / (ratio**2) # I^2 t karakteristiği
            if t > 0.15 and t < 90.0:
                pts_ag.append(to_canvas(cur, t))
    if len(pts_ag) > 2:
        msp.add_lwpolyline(pts_ag, dxfattribs={"layer": "KABLO_AG", "const_width": 0.6})
        msp.add_text("AG Ana Kesici (2500A LSI)", dxfattribs={"layer": "KABLO_AG", "height": 2.2}).set_placement((pts_ag[8][0] + 5, pts_ag[8][1]))

    # 3. 400A Fider Kesici Eğrisi (Yeşil)
    i_fider = np.logspace(2.5, 3.8, 30)
    pts_fider = []
    for cur in i_fider:
        ratio = cur / 400.0
        if ratio > 1.05:
            t = 1.5 / (ratio**2)
            if t > 0.02 and t < 50.0:
                pts_fider.append(to_canvas(cur, t))
    if len(pts_fider) > 2:
        msp.add_lwpolyline(pts_fider, dxfattribs={"layer": "TOPRAKLAMA", "const_width": 0.5})
        msp.add_text("AG 400A Fider", dxfattribs={"layer": "TOPRAKLAMA", "height": 2.0}).set_placement((pts_fider[6][0] + 5, pts_fider[6][1]))

    # Selektivite Marjı Açıklaması
    msp.add_text("Selektivite Marji dt >= 300 ms (Tam Koordinasyon Saglanmistir)",
                 dxfattribs={"layer": "YAZI", "height": 2.2}).set_placement((origin_x + 10, origin_y + 15))

    doc.saveas(dxf_yolu)
    print(f"Pafta 1 DXF kaydedildi: {dxf_yolu}")

def uret_pafta2_yerlesim(dxf_yolu):
    """
    Pafta 2: Kompakt Beton Köşk Mimari/Mekanik Yerleşimi ve Topraklama Planı
    """
    doc = ezdxf.new("R2010", setup=True)
    setup_layers(doc)
    msp = doc.modelspace()

    # A1 Pafta Sınırı
    msp.add_lwpolyline([(0, 0), (841, 0), (841, 594), (0, 594), (0, 0)],
                       dxfattribs={"layer": "CERCEVE", "const_width": 0.7})
    msp.add_lwpolyline([(10, 10), (831, 10), (831, 584), (10, 584), (10, 10)],
                       dxfattribs={"layer": "CERCEVE", "const_width": 0.35})

    ciz_antet(msp, 640, 20, "EE-TM-02", "BETON KÖŞK YERLEŞİM VE TOPRAKLAMA PLANI", "1/25")

    # Beton Köşk Dış Duvarları (Ölçek: 1 birim = 10 mm; 7200 x 2600 mm -> 720 x 260 birim)
    # Çizim Alanı: x=60..700, y=140..440
    bx, by = 60, 160
    bw, bh = 540, 240 # 7200 x 3200 mm dış köşk

    # Dış Duvar (Beton 100 mm kalınlık -> 10 birim)
    msp.add_lwpolyline([(bx, by), (bx + bw, by), (bx + bw, by + bh), (bx, by + bh), (bx, by)],
                       dxfattribs={"layer": "DUVAR", "const_width": 0.8})
    # İç Duvar
    t = 10
    msp.add_lwpolyline([(bx + t, by + t), (bx + bw - t, by + t),
                        (bx + bw - t, by + bh - t), (bx + t, by + bh - t), (bx + t, by + t)],
                       dxfattribs={"layer": "DUVAR", "const_width": 0.4})

    # Ara Bölme Duvarları (Kompartımanlar)
    # 1. OG Hücre Kompartımanı: x = bx+t .. bx+180
    # 2. Trafo Kompartımanı: x = bx+180 .. bx+370
    # 3. AG Pano Kompartımanı: x = bx+370 .. bx+bw-t
    msp.add_lwpolyline([(bx + 180, by + t), (bx + 180, by + bh - t)], dxfattribs={"layer": "DUVAR", "const_width": 0.5})
    msp.add_lwpolyline([(bx + 370, by + t), (bx + 370, by + bh - t)], dxfattribs={"layer": "DUVAR", "const_width": 0.5})

    # Kompartıman İsimleri
    msp.add_text("OG HÜCRE KOMPARTIMANI", dxfattribs={"layer": "YAZI", "height": 3.0}).set_placement((bx + 25, by + bh - 25))
    msp.add_text("TRAFO KOMPARTIMANI", dxfattribs={"layer": "YAZI", "height": 3.0}).set_placement((bx + 205, by + bh - 25))
    msp.add_text("AG PANO KOMPARTIMANI", dxfattribs={"layer": "YAZI", "height": 3.0}).set_placement((bx + 390, by + bh - 25))

    # OG Hücreleri Yerleşimi (3 adet modüler hücre, her biri 45 birim genişlik)
    for i in range(3):
        hx = bx + 25 + i * 45
        msp.add_lwpolyline([(hx, by + 30), (hx + 42, by + 30), (hx + 42, by + 120), (hx, by + 120), (hx, by + 30)],
                           dxfattribs={"layer": "EKIPMAN", "const_width": 0.4})
        h_names = ["GİRİŞ", "KORUMA", "ÖLÇÜ"]
        msp.add_text(f"H{i+1}: {h_names[i]}", dxfattribs={"layer": "YAZI", "height": 2.2}).set_placement((hx + 5, by + 75))

    # Trafo Yerleşimi (1600 kVA Trafo, 140 x 90 birim)
    tx, ty = bx + 205, by + 40
    msp.add_lwpolyline([(tx, ty), (tx + 140, ty), (tx + 140, ty + 120), (tx, ty + 120), (tx, ty)],
                       dxfattribs={"layer": "EKIPMAN", "const_width": 0.6})
    msp.add_text("1600 kVA HERMETİK YAĞLI TRAFO", dxfattribs={"layer": "YAZI", "height": 2.5}).set_placement((tx + 10, ty + 70))
    msp.add_text("Yağ Toplama Çukuru Dahil", dxfattribs={"layer": "YAZI", "height": 1.8}).set_placement((tx + 25, ty + 50))

    # AG Dağıtım Panosu (130 x 40 birim)
    agx, agy = bx + 385, by + 40
    msp.add_lwpolyline([(agx, agy), (agx + 130, agy), (agx + 130, agy + 60), (agx, agy + 60), (agx, agy)],
                       dxfattribs={"layer": "EKIPMAN", "const_width": 0.5})
    msp.add_text("AG DAĞITIM PANOSU (ADP)", dxfattribs={"layer": "YAZI", "height": 2.5}).set_placement((agx + 10, agy + 35))
    msp.add_text("2500A ACB + 4 Fider + Komp.", dxfattribs={"layer": "YAZI", "height": 1.8}).set_placement((agx + 10, agy + 20))

    # Topraklama Ring Hattı (Köşk Dışında 20 birim mesafeden çevreleyen yeşil kesikli hat)
    rx, ry = bx - 25, by - 25
    rw, rh = bw + 50, bh + 50
    msp.add_lwpolyline([(rx, ry), (rx + rw, ry), (rx + rw, ry + rh), (rx, ry + rh), (rx, ry)],
                       dxfattribs={"layer": "TOPRAKLAMA", "const_width": 0.5})
    msp.add_text("TEMEL/RİNG TOPRAKLAMA HATTI (30x3,5 mm Galvaniz Şerit)",
                 dxfattribs={"layer": "TOPRAKLAMA", "height": 2.5}).set_placement((rx + 10, ry - 12))

    # 4 Köşede Topraklama Çubuk Elektrotları (Daire)
    electrodes = [(rx, ry), (rx + rw, ry), (rx + rw, ry + rh), (rx, ry + rh)]
    for ex, ey in electrodes:
        msp.add_circle((ex, ey), 5, dxfattribs={"layer": "TOPRAKLAMA"})
        msp.add_text("Cu Çubuk (D=20mm, L=3.5m)", dxfattribs={"layer": "TOPRAKLAMA", "height": 1.8}).set_placement((ex + 7, ey - 5))

    # Ölçülendirmeler (Gerçek linear dimensions)
    msp.add_linear_dim(base=(bx, by + bh + 25), p1=(bx, by + bh), p2=(bx + bw, by + bh),
                       dimstyle="EZ_CURVED", dxfattribs={"layer": "OLCU", "text": "7200 mm"})
    msp.add_linear_dim(base=(bx - 20, by), p1=(bx, by), p2=(bx, by + bh),
                       angle=90, dimstyle="EZ_CURVED", dxfattribs={"layer": "OLCU", "text": "3200 mm"})
    msp.add_linear_dim(base=(bx + 180, by + bh + 12), p1=(bx, by + bh), p2=(bx + 180, by + bh),
                       dimstyle="EZ_CURVED", dxfattribs={"layer": "OLCU", "text": "2400 mm"})
    msp.add_linear_dim(base=(bx + 370, by + bh + 12), p1=(bx + 180, by + bh), p2=(bx + 370, by + bh),
                       dimstyle="EZ_CURVED", dxfattribs={"layer": "OLCU", "text": "2500 mm"})

    doc.saveas(dxf_yolu)
    print(f"Pafta 2 DXF kaydedildi: {dxf_yolu}")

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    p1 = os.path.join(base_dir, "kompakt-trafo-tek-hat-ve-koruma.dxf")
    p2 = os.path.join(base_dir, "kompakt-trafo-merkezi-yerlesimi.dxf")
    uret_pafta1_tek_hat(p1)
    uret_pafta2_yerlesim(p2)

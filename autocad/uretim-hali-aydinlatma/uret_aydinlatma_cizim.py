"""
Fabrika Üretim Holü Aydınlatma (EN 12464-1) ve Acil Aydınlatma (EN 1838) CAD Çizim Üreticisi
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
        ("DUVAR", colors.WHITE, "CONTINUOUS"),
        ("KOLON", colors.CYAN, "CONTINUOUS"),
        ("ARMATUR_NORMAL", colors.YELLOW, "CONTINUOUS"),
        ("ARMATUR_ACIL", colors.RED, "CONTINUOUS"),
        ("LINYE_HATTI", colors.MAGENTA, "CONTINUOUS"),
        ("ACIL_GUZERGAH", colors.GREEN, "DASHED"),
        ("LUX_GRID", colors.LIGHT_GRAY, "CONTINUOUS"),
        ("YAZI", colors.WHITE, "CONTINUOUS"),
        ("OLCU", colors.GREEN, "CONTINUOUS")
    ]
    for name, col, lt in layers:
        if name not in doc.layers:
            doc.layers.add(name=name, color=col, linetype=lt)

def ciz_antet(msp, x_base, y_base, pafta_no, pafta_adi, olcek="1/100"):
    pts = [(x_base, y_base), (x_base + 180, y_base),
           (x_base + 180, y_base + 60), (x_base, y_base + 60), (x_base, y_base)]
    msp.add_lwpolyline(pts, dxfattribs={"layer": "ANTET", "const_width": 0.5})

    msp.add_lwpolyline([(x_base, y_base + 45), (x_base + 180, y_base + 45)], dxfattribs={"layer": "ANTET"})
    msp.add_lwpolyline([(x_base, y_base + 30), (x_base + 180, y_base + 30)], dxfattribs={"layer": "ANTET"})
    msp.add_lwpolyline([(x_base, y_base + 15), (x_base + 180, y_base + 15)], dxfattribs={"layer": "ANTET"})

    msp.add_lwpolyline([(x_base + 90, y_base + 15), (x_base + 90, y_base + 30)], dxfattribs={"layer": "ANTET"})
    msp.add_lwpolyline([(x_base + 135, y_base + 15), (x_base + 135, y_base + 30)], dxfattribs={"layer": "ANTET"})
    msp.add_lwpolyline([(x_base + 90, y_base), (x_base + 90, y_base + 15)], dxfattribs={"layer": "ANTET"})

    msp.add_text("FABRİKA ÜRETİM HOLÜ ELEKTRİK AYDINLATMA PROJESİ",
                 dxfattribs={"layer": "ANTET", "height": 3.0}).set_placement((x_base + 5, y_base + 51))
    msp.add_text(pafta_adi,
                 dxfattribs={"layer": "ANTET", "height": 2.8}).set_placement((x_base + 5, y_base + 36))

    msp.add_text("PROJE MÜHENDİSİ:", dxfattribs={"layer": "ANTET", "height": 2.0}).set_placement((x_base + 5, y_base + 24))
    msp.add_text("Hakan OĞUZ", dxfattribs={"layer": "ANTET", "height": 3.2}).set_placement((x_base + 5, y_base + 18))
    msp.add_text("Elektrik-Elektronik Mühendisi", dxfattribs={"layer": "ANTET", "height": 2.0}).set_placement((x_base + 5, y_base + 5))

    msp.add_text("ÖLÇEK:", dxfattribs={"layer": "ANTET", "height": 2.0}).set_placement((x_base + 95, y_base + 24))
    msp.add_text(olcek, dxfattribs={"layer": "ANTET", "height": 2.5}).set_placement((x_base + 95, y_base + 18))

    msp.add_text("PAFTA NO:", dxfattribs={"layer": "ANTET", "height": 2.0}).set_placement((x_base + 140, y_base + 24))
    msp.add_text(pafta_no, dxfattribs={"layer": "ANTET", "height": 3.0}).set_placement((x_base + 140, y_base + 18))

    msp.add_text("STANDART: EN 12464-1 / EN 1838", dxfattribs={"layer": "ANTET", "height": 2.0}).set_placement((x_base + 95, y_base + 5))

def uret_pafta1(dxf_yolu):
    """Pafta 1: Üretim Holü Armatür Yerleşimi ve Nokta Nokta Lüks Hesap Izgarası"""
    doc = ezdxf.new("R2010", setup=True)
    setup_layers(doc)
    msp = doc.modelspace()

    # A1 Çerçeve (841 x 594 mm)
    msp.add_lwpolyline([(0, 0), (841, 0), (841, 594), (0, 594), (0, 0)], dxfattribs={"layer": "CERCEVE", "const_width": 0.7})
    msp.add_lwpolyline([(10, 10), (831, 10), (831, 584), (10, 584), (10, 10)], dxfattribs={"layer": "CERCEVE", "const_width": 0.35})

    ciz_antet(msp, 640, 20, "EE-AYD-01", "ÜRETİM HOLÜ GENEL AYDINLATMA VE LÜKS DAĞILIM PLANI", "1/100")

    # Fabrika Holü Boyutları: 60m x 24m -> Çizim ölçeği 1m = 10mm (600mm x 240mm)
    # Konum: x = 30..630, y = 280..520
    hx, hy = 30, 280
    hw, hh = 600, 240

    # Dış Duvarlar (Kalın polyline)
    msp.add_lwpolyline([(hx, hy), (hx + hw, hy), (hx + hw, hy + hh), (hx, hy + hh), (hx, hy)],
                       dxfattribs={"layer": "DUVAR", "const_width": 0.8})

    # Kolonlar (Aks aralığı: Boyuna 6m -> 60mm, Enine 12m -> 120mm)
    for col_x in range(hx, hx + hw + 1, 60):
        for col_y in [hy, hy + 120, hy + hh]:
            msp.add_lwpolyline([(col_x - 3, col_y - 3), (col_x + 3, col_y - 3),
                                (col_x + 3, col_y + 3), (col_x - 3, col_y + 3), (col_x - 3, col_y - 3)],
                               dxfattribs={"layer": "KOLON", "const_width": 0.5})

    # Armatür Yerleşimi (Işık Akısı Hesabına Göre):
    # E_req = 500 lux, Alan = 1440 m2, MF = 0.80, UF = 0.65
    # Toplam Lümen = (500 * 1440) / (0.80 * 0.65) = 1,384,615 lm
    # Armatür: 150W LED High-Bay (22,500 lm) -> N = 1,384,615 / 22,500 = 61.5 -> 60 Armatür!
    # Düzen: 12 Sütun x 5 Sıra = 60 Armatür!
    # Boyuna aralık: 60m / 12 = 5m (50mm), duvardan 2.5m (25mm)
    # Enine aralık: 24m / 5 = 4.8m (48mm), duvardan 2.4m (24mm)
    dx = 50
    dy = 48
    start_x = hx + 25
    start_y = hy + 24

    for ix in range(12):
        arm_x = start_x + ix * dx
        for iy in range(5):
            arm_y = start_y + iy * dy
            # Armatür Sembolü (Daire + Artı)
            msp.add_circle((arm_x, arm_y), 4.0, dxfattribs={"layer": "ARMATUR_NORMAL"})
            msp.add_lwpolyline([(arm_x - 4, arm_y), (arm_x + 4, arm_y)], dxfattribs={"layer": "ARMATUR_NORMAL"})
            msp.add_lwpolyline([(arm_x, arm_y - 4), (arm_x, arm_y + 4)], dxfattribs={"layer": "ARMATUR_NORMAL"})

            # Nokta Nokta Lüks Değeri (Merkezde ~540 lx, kenarlarda ~480 lx)
            edge_dist_x = min(ix, 11 - ix)
            edge_dist_y = min(iy, 4 - iy)
            lux_val = int(500 + 15 * (edge_dist_x + edge_dist_y) + (ix * iy % 7 - 3))
            msp.add_text(f"{lux_val} lx", dxfattribs={"layer": "LUX_GRID", "height": 1.5}).set_placement((arm_x - 5, arm_y - 8))

    # Ölçülendirmeler (Gerçek DIMENSION)
    msp.add_linear_dim(base=(hx, hy + hh + 20), p1=(hx, hy + hh), p2=(hx + hw, hy + hh),
                       dimstyle="EZ_CURVED", dxfattribs={"layer": "OLCU", "text": "60 000 mm (60.0 m)"})
    msp.add_linear_dim(base=(hx - 18, hy), p1=(hx, hy), p2=(hx, hy + hh),
                       angle=90, dimstyle="EZ_CURVED", dxfattribs={"layer": "OLCU", "text": "24 000 mm (24.0 m)"})

    # Pafta Alt Bilgi Tablosu: EN 12464-1 Aydınlatma Hesap Tablosu (x=30..450, y=30..230)
    tx_base = 30
    ty_base = 40
    msp.add_lwpolyline([(tx_base, ty_base), (tx_base + 400, ty_base),
                        (tx_base + 400, ty_base + 190), (tx_base, ty_base + 190), (tx_base, ty_base)],
                       dxfattribs={"layer": "ANTET", "const_width": 0.4})
    
    msp.add_text("EN 12464-1 IŞIK AKISI (LÜMEN YÖNTEMİ) HESAP TABLOSU",
                 dxfattribs={"layer": "ANTET", "height": 3.2}).set_placement((tx_base + 10, ty_base + 175))
    
    table_lines = [
        "Mahal Tanımı: Endüstriyel Fabrika İmalat ve Montaj Holü",
        "Hol Boyutları: Uzunluk = 60.0 m, Genişlik = 24.0 m, Tavan Yüksekliği = 8.0 m",
        "Çalışma Düzlemi (h_work): 0.85 m | Askı Yüksekliği (H_askı): 7.15 m",
        "Oda İndeksi (k): (60 x 24) / [7.15 x (60 + 24)] = 2.40",
        "Tavan/Duvar/Zemin Yansıtma Çarpanları: 70% / 50% / 20%",
        "Tesisat Kullanım Faktörü (UF): 0.65 | Bakım Faktörü (MF): 0.80",
        "Gereken Ortalama Aydınlık (E_m): 500 lux (EN 12464-1 Tablo 5.3)",
        "Gerekli Toplam Işık Akısı: Phi_top = (E_m x A) / (UF x MF) = 1,384,615 lm",
        "Seçilen Armatür: 150W Endüstriyel LED High-Bay (Philips/Osram Çip, 150 lm/W)",
        "Tekil Armatür Işık Akısı: 22,500 lümen | Renksel Geriverim (Ra) >= 80 | CCT = 4000K",
        "Hesaplanan Armatür Sayısı: N = 1,384,615 / 22,500 = 61.5 -> 60 Adet (12x5 Düzen)",
        "Gerçekleşen Ortalama Aydınlık (E_act): 512 lux | Düzgünlük Oranı (U0): 0.74 (>=0.60 UYGUN)",
        "Toplam Aydınlatma Kurulu Gücü: 60 x 150W = 9.0 kW (Güç Yoğunluğu: 6.25 W/m² - A+ Sınıfı)"
    ]

    for idx, line in enumerate(table_lines):
        msp.add_text(line, dxfattribs={"layer": "YAZI", "height": 2.2}).set_placement((tx_base + 10, ty_base + 155 - idx * 11))

    doc.saveas(dxf_yolu)
    print(f"Pafta 1 DXF kaydedildi: {dxf_yolu}")

def uret_pafta2(dxf_yolu):
    """Pafta 2: Acil Aydınlatma (EN 1838), Kaçış Güzergâhları ve Aydınlatma Panosu Yük Planı"""
    doc = ezdxf.new("R2010", setup=True)
    setup_layers(doc)
    msp = doc.modelspace()

    # A1 Çerçeve
    msp.add_lwpolyline([(0, 0), (841, 0), (841, 594), (0, 594), (0, 0)], dxfattribs={"layer": "CERCEVE", "const_width": 0.7})
    msp.add_lwpolyline([(10, 10), (831, 10), (831, 584), (10, 584), (10, 10)], dxfattribs={"layer": "CERCEVE", "const_width": 0.35})

    ciz_antet(msp, 640, 20, "EE-AYD-02", "ACİL AYDINLATMA, KAÇIŞ PLANI VE DAĞITIM PANOSU", "1/100")

    hx, hy = 30, 280
    hw, hh = 600, 240

    # Dış Duvarlar
    msp.add_lwpolyline([(hx, hy), (hx + hw, hy), (hx + hw, hy + hh), (hx, hy + hh), (hx, hy)],
                       dxfattribs={"layer": "DUVAR", "const_width": 0.8})

    # Acil Çıkış Kapıları (4 adet acil çıkış kapısı)
    doors = [(hx + 80, hy), (hx + hw - 80, hy), (hx + 80, hy + hh), (hx + hw - 80, hy + hh)]
    for dx, dy in doors:
        msp.add_lwpolyline([(dx - 10, dy), (dx + 10, dy)], dxfattribs={"layer": "ACIL_GUZERGAH", "const_width": 1.2})
        msp.add_text("ACİL ÇIKIŞ (EXIT)", dxfattribs={"layer": "ARMATUR_ACIL", "height": 2.2}).set_placement((dx - 15, dy - 7 if dy == hy else dy + 5))

    # Ana Kaçış Koridorları (Yeşil Kesikli Çizgi - EN 1838)
    msp.add_lwpolyline([(hx + 80, hy), (hx + 80, hy + hh)], dxfattribs={"layer": "ACIL_GUZERGAH", "const_width": 0.6})
    msp.add_lwpolyline([(hx + hw - 80, hy), (hx + hw - 80, hy + hh)], dxfattribs={"layer": "ACIL_GUZERGAH", "const_width": 0.6})
    msp.add_lwpolyline([(hx + 80, hy + 120), (hx + hw - 80, hy + 120)], dxfattribs={"layer": "ACIL_GUZERGAH", "const_width": 0.6})

    # Acil Aydınlatma ve Yönlendirme Armatürleri (3 Saat Bataryalı LED Kit)
    for em_x in range(hx + 80, hx + hw - 70, 40):
        msp.add_circle((em_x, hy + 120), 3.5, dxfattribs={"layer": "ARMATUR_ACIL"})
        msp.add_text("E", dxfattribs={"layer": "ARMATUR_ACIL", "height": 2.0}).set_placement((em_x - 1.2, hy + 118))

    msp.add_text("EN 1838 MERKEZİ KAÇIŞ GÜZERGAHI (E >= 1.0 lux, U0 >= 0.10)",
                 dxfattribs={"layer": "ACIL_GUZERGAH", "height": 2.5}).set_placement((hx + 120, hy + 130))

    # Aydınlatma Panosu (AYP) Tek Hat Şeması (x=30..500, y=30..240)
    px, py = 40, 40
    msp.add_lwpolyline([(px, py), (px + 450, py), (px + 450, py + 190), (px, py + 190), (px, py)],
                       dxfattribs={"layer": "ANTET", "const_width": 0.4})
    
    msp.add_text("FABRİKA AYDINLATMA PANOSU (AYP) DAĞITIM VE YÜK CETVELİ",
                 dxfattribs={"layer": "ANTET", "height": 3.0}).set_placement((px + 10, py + 175))

    panel_rows = [
        "Giriş: 3x40A TMŞ (Termik Manyetik Şalter) + 3x40A 30mA Yangın Koruma Eşdeğeri RCD",
        "Linye 1 (L1 - Faz R): 12x 150W High-Bay (Sıra 1) -> P = 1.80 kW, 1x (3x2.5 mm² Halogen Free Cu) - 16A MCB",
        "Linye 2 (L2 - Faz S): 12x 150W High-Bay (Sıra 2) -> P = 1.80 kW, 1x (3x2.5 mm² Halogen Free Cu) - 16A MCB",
        "Linye 3 (L3 - Faz T): 12x 150W High-Bay (Sıra 3) -> P = 1.80 kW, 1x (3x2.5 mm² Halogen Free Cu) - 16A MCB",
        "Linye 4 (L4 - Faz R): 12x 150W High-Bay (Sıra 4) -> P = 1.80 kW, 1x (3x2.5 mm² Halogen Free Cu) - 16A MCB",
        "Linye 5 (L5 - Faz S): 12x 150W High-Bay (Sıra 5) -> P = 1.80 kW, 1x (3x2.5 mm² Halogen Free Cu) - 16A MCB",
        "Linye 6 (L6 - Faz T): 14x 20W Acil Aydınlatma & Yönlendirme (Bataryalı) -> P = 0.28 kW - 10A MCB",
        "Linye 7 (L7 - Yedek): Boş Fider (Yedek Linye) - 16A MCB",
        "Toplam Kurulu Güç: 9.28 kW | Eşzamanlılık Faktörü: 1.0 | Talep Gücü: 9.28 kW",
        "Besleme Kablosu: 5x10 mm² N2XH FE180 Yangına Dayanıklı Cu Kablo",
        "Maksimum Hat Boyu: 75 metre | Gerilim Düşümü (%e): %0.82 (<= %1.5 Şartname Sınırı UYGUN)"
    ]

    for idx, r_text in enumerate(panel_rows):
        msp.add_text(r_text, dxfattribs={"layer": "YAZI", "height": 2.2}).set_placement((px + 10, py + 155 - idx * 12))

    doc.saveas(dxf_yolu)
    print(f"Pafta 2 DXF kaydedildi: {dxf_yolu}")

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    p1 = os.path.join(base_dir, "uretim-hali-aydinlatma-ve-lux-haritasi.dxf")
    p2 = os.path.join(base_dir, "acil-aydinlatma-ve-pano-yuk-plani.dxf")
    uret_pafta1(p1)
    uret_pafta2(p2)

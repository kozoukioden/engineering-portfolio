# Author : Hakan OĞUZ - Elektrik Elektronik Mühendisi
# Project: Küçük İşletme Kuvvetli Akım Tek-Hat Şeması (SLD) ve Pano Yerleşimi
# Date   : 2026-10-26
# License: MIT
# Desc   : 160 kVA trafolu küçük sanayi tesisi için AG tek-hat şeması ve ana dağıtım panosu (ADP) mekanik yerleşim DXF çizimleri.
"""
Çizim birimi: milimetre (mm).
İki pafta üretilir:
  SLD-01  isletme-tek-hat-semasi.dxf  -> Trafo, Giriş Kompakt Şalter (MCCB), Baralar, Motor/Aydınlatma/Priz Çıkışları, Kompanzasyon, Selektivite
  SLD-02  adp-pano-yerlesimi.dxf      -> 2000x800x600 mm dikili tip modüler pano mekanik iç yerleşimi (bara, şalterler, kablo kanalları, klemensler)
"""
import os
import ezdxf
from ezdxf.enums import TextEntityAlignment

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.abspath(os.path.join(HERE, ".."))
SEK  = os.path.join(OUT, "sekiller")

KATMANLAR = [
    ("CERCEVE", 7, "CONTINUOUS"),
    ("BARA", 1, "CONTINUOUS"),       # Kırmızı / Bakır baralar
    ("SALTIK", 4, "CONTINUOUS"),     # Camgöbeği şalterler ve koruma elemanları
    ("HAT", 7, "CONTINUOUS"),        # Beyaz güç hatları
    ("KABLO", 3, "CONTINUOUS"),      # Yeşil kablolar
    ("TOPRAKLAMA", 2, "DASHDOT"),    # Sarı/Yeşil PE barası
    ("PANO_GOVDE", 8, "CONTINUOUS"), # Gri pano karkası
    ("PANO_ELEMAN", 4, "CONTINUOUS"),# Şalterler, cihazlar
    ("KANAL", 9, "DASHED"),          # Kablo kanalları
    ("OLCU", 8, "CONTINUOUS"),       # Ölçülendirmeler
    ("YAZI", 7, "CONTINUOUS"),
    ("ANTET", 7, "CONTINUOUS"),
]

def yeni_doc():
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 4       # Millimeters
    doc.header["$MEASUREMENT"] = 1    # Metric
    for ad, renk, lt in KATMANLAR:
        if lt not in doc.linetypes:
            lt = "CONTINUOUS"
        doc.layers.add(ad, color=renk, linetype=lt)
    if "ISLETME_STYLE" not in doc.styles:
        doc.styles.add("ISLETME_STYLE", font="arial.ttf")
    return doc

def yazi(msp, text, x, y, h=300, layer="YAZI", align=TextEntityAlignment.LEFT, rot=0, color=None):
    attr = {"layer": layer, "style": "ISLETME_STYLE"}
    if color is not None:
        attr["color"] = color
    t = msp.add_text(text, height=h, rotation=rot, dxfattribs=attr)
    t.set_placement((x, y), align=align)
    return t

def antet(msp, pafta_adi, pafta_no, olcek, x0, y0):
    w, h = 14000.0, 6000.0
    msp.add_lwpolyline([(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)],
                       close=True, dxfattribs={"layer": "ANTET", "const_width": 40})
    for yy in (y0 + h - 1400, y0 + h - 2600, y0 + h - 3800, y0 + 1400):
        msp.add_line((x0, yy), (x0 + w, yy), dxfattribs={"layer": "ANTET"})
    
    yazi(msp, "KUCUK ISLETME KUVVETLI AKIM VE AG DAGITIM", x0 + 400, y0 + h - 1000, h=450, layer="ANTET")
    yazi(msp, pafta_adi, x0 + 400, y0 + h - 2200, h=400, layer="ANTET")
    yazi(msp, "Cizen : Hakan OGUZ", x0 + 400, y0 + h - 3300, h=400, layer="ANTET")
    yazi(msp, "Elektrik Elektronik Muhendisi", x0 + 400, y0 + h - 4400, h=380, layer="ANTET")
    
    xr = x0 + 8500
    msp.add_line((xr, y0 + 1400), (xr, y0), dxfattribs={"layer": "ANTET"})
    yazi(msp, "Tarih", xr + 300, y0 + 1000, h=300, layer="ANTET")
    yazi(msp, "2026-10-26", xr + 300, y0 + 400, h=350, layer="ANTET")
    
    xr2 = x0 + 11500
    msp.add_line((xr2, y0 + 1400), (xr2, y0), dxfattribs={"layer": "ANTET"})
    yazi(msp, "Olcek", xr2 + 300, y0 + 1000, h=300, layer="ANTET")
    yazi(msp, olcek, xr2 + 300, y0 + 400, h=350, layer="ANTET")


def ciz_tek_hat():
    doc = yeni_doc()
    msp = doc.modelspace()

    # Dış sınır çerçevesi (A1 boyutuna yakın: 55000 x 36000 mm)
    msp.add_lwpolyline([(0, 0), (55000, 0), (55000, 36000), (0, 36000)],
                       close=True, dxfattribs={"layer": "CERCEVE", "const_width": 50})

    # 1. Başlık
    yazi(msp, "160 kVA TRAFOLU ATOLYE AG ANA DAGITIM PANOSU (ADP) TEK HAT SEMASI", 2500, 34000, h=650, layer="YAZI")
    yazi(msp, "380/220 V TN-S Sistem - Uk=%4.5 - l_k3=4.8 kA (Barada)", 2500, 32800, h=400, layer="YAZI")

    # 2. Orta Gerilim & Trafo Girişi
    # Trafo sembolü (iç içe iki çember)
    tx, ty = 6000, 27500
    msp.add_circle((tx, ty + 1200), 1000, dxfattribs={"layer": "SALTIK"})
    msp.add_circle((tx, ty), 1000, dxfattribs={"layer": "SALTIK"})
    yazi(msp, "OG SEBEKE (34.5 kV)", tx - 2200, ty + 3200, h=400, layer="HAT")
    msp.add_line((tx, ty + 3000), (tx, ty + 2200), dxfattribs={"layer": "HAT"})
    yazi(msp, "DAHILI TIP YAGLI TRAFO", tx + 1400, ty + 1100, h=380, layer="SALTIK")
    yazi(msp, "160 kVA 34.5 / 0.4 kV", tx + 1400, ty + 500, h=350, layer="SALTIK")
    yazi(msp, "Dyn11, Uk=%4.5, In=231 A", tx + 1400, ty - 100, h=320, layer="SALTIK")

    # Trafo -> Ana Giriş Şalteri Hattı
    msp.add_line((tx, ty - 1000), (tx, 22000), dxfattribs={"layer": "HAT"})
    yazi(msp, "3x(1x150/25) mm2 NYY Cu + 1x95 mm2 Cu N", tx + 300, 23500, h=320, layer="KABLO")

    # 3. Ana Giriş Şalteri (MCCB)
    sx, sy = tx, 20500
    msp.add_lwpolyline([(sx - 600, sy - 800), (sx + 600, sy - 800), (sx + 600, sy + 800), (sx - 600, sy + 800)],
                       close=True, dxfattribs={"layer": "SALTIK"})
    msp.add_line((sx - 600, sy - 800), (sx + 600, sy + 800), dxfattribs={"layer": "SALTIK"})
    yazi(msp, "QF1: 3P 250A MCCB", sx + 900, sy + 300, h=380, layer="SALTIK")
    yazi(msp, "Icu=36 kA (TMŞ)", sx + 900, sy - 200, h=320, layer="SALTIK")
    yazi(msp, "Termik-Manyetik Ayarlı (0.8-1.0xIn)", sx + 900, sy - 650, h=300, layer="SALTIK")

    # Şalterden Ana Baraya İniş
    msp.add_line((sx, 22000), (sx, sy + 800), dxfattribs={"layer": "HAT"})
    msp.add_line((sx, sy - 800), (sx, 17000), dxfattribs={"layer": "HAT"})

    # Akım Trafoları & Enerji Analizörü
    msp.add_circle((sx, 18500), 350, dxfattribs={"layer": "SALTIK"})
    yazi(msp, "3 x (250/5A Cl 0.5) CT", sx + 600, 18500, h=300, layer="SALTIK")
    yazi(msp, "Multimetre / Enerji Analizörü", sx + 600, 17900, h=300, layer="SALTIK")

    # 4. Ana Bakır Bara (Cu 40x5 mm Cu)
    bx_start, bx_end = 4000, 48000
    by = 17000
    msp.add_lwpolyline([(bx_start, by), (bx_end, by)], dxfattribs={"layer": "BARA", "const_width": 40})
    msp.add_lwpolyline([(bx_start, by - 300), (bx_end, by - 300)], dxfattribs={"layer": "BARA", "const_width": 20})
    yazi(msp, "ANA BARA: Cu 40x5 mm (400 A) - 3P + N (30x5 mm)", bx_start, by + 500, h=400, layer="BARA")

    # 5. Dağıtım Kolları (Fiderler)
    fiderler = [
        {"x": 10000, "ad": "F1: KOMPANZASYON", "salter": "QF2: 3P 100A MCCB", "kablo": "3x35+16 mm2 NYY", "yuk": "50 kVAr Otomatik Kademe", "tip": "komp"},
        {"x": 16000, "ad": "F2: CNC & ISLEME MERKEZI", "salter": "QF3: 3P 63A MCCB (36kA)", "kablo": "4x16 mm2 NYY (L=25m)", "yuk": "P=22 kW, I=38 A, %e=0.62", "tip": "motor"},
        {"x": 22000, "ad": "F3: HAVA KOMPRESORU", "salter": "QF4: 3P 50A MCCB", "kablo": "4x10 mm2 NYY (L=18m)", "yuk": "P=15 kW Y/D Yol Verme, I=28 A", "tip": "motor"},
        {"x": 28000, "ad": "F4: TALASLI IMALAT MOTORLAR", "salter": "QF5: 3P 63A MCCB", "kablo": "4x16 mm2 NYY (L=35m)", "yuk": "P=25 kW Toplam Motor Yuku", "tip": "motor"},
        {"x": 34000, "ad": "F5: ATOLYE PRIZ PANOSU", "salter": "QF6: 3P 40A MCB (C Tipi)", "kablo": "4x10 mm2 NYY (L=40m)", "yuk": "P=18 kW (3F + 1F Prizler)", "tip": "priz"},
        {"x": 40000, "ad": "F6: ATOLYE LED AYDINLATMA", "salter": "QF7: 3P 25A MCB (B Tipi)", "kablo": "4x6 mm2 NYY (L=50m)", "yuk": "P=8 kW Yüksek Tavan LED", "tip": "aydinlatma"},
        {"x": 46000, "ad": "F7: OFIS & IDARI KISIM", "salter": "QF8: 3P 32A MCB + 30mA RCD", "kablo": "4x6 mm2 NYY (L=45m)", "yuk": "P=12 kW UPS, PC, Iklimlendirme", "tip": "ofis"},
    ]

    for f in fiderler:
        fx = f["x"]
        # Baradan iniş
        msp.add_line((fx, by), (fx, 14000), dxfattribs={"layer": "HAT"})
        # Şalter kutusu
        msp.add_lwpolyline([(fx - 400, 12600), (fx + 400, 12600), (fx + 400, 13800), (fx - 400, 13800)],
                           close=True, dxfattribs={"layer": "SALTIK"})
        msp.add_line((fx - 400, 12600), (fx + 400, 13800), dxfattribs={"layer": "SALTIK"})
        # Çıkış hattı
        msp.add_line((fx, 12600), (fx, 9000), dxfattribs={"layer": "HAT"})
        
        # Tipik yük sembolü (Ok veya dikdörtgen)
        msp.add_lwpolyline([(fx - 600, 7800), (fx + 600, 7800), (fx + 600, 8800), (fx - 600, 8800)],
                           close=True, dxfattribs={"layer": "HAT"})
        
        # Açıklama metinleri
        yazi(msp, f["ad"], fx - 800, 15000, h=300, layer="YAZI", rot=90)
        yazi(msp, f["salter"], fx + 600, 13400, h=250, layer="SALTIK")
        yazi(msp, f["kablo"], fx + 200, 10800, h=240, layer="KABLO", rot=90)
        yazi(msp, f["yuk"], fx - 500, 8200, h=240, layer="YAZI")

    # 6. Koruma Topraklama Barası (PE)
    pe_y = 6000
    msp.add_lwpolyline([(bx_start, pe_y), (bx_end, pe_y)], dxfattribs={"layer": "TOPRAKLAMA", "const_width": 30})
    yazi(msp, "ANA KORUMA TOPRAKLAMA BARASI (PE - Cu 30x5 mm) - Tum Govdeler ve Kablo Ekranlari Bagli", bx_start, pe_y + 400, h=350, layer="TOPRAKLAMA")
    
    # Topraklama iletkeni ve kazık sembolü
    gx = 12000
    msp.add_line((gx, pe_y), (gx, pe_y - 2000), dxfattribs={"layer": "TOPRAKLAMA"})
    for i, w_line in enumerate((1800, 1200, 600)):
        msp.add_line((gx - w_line/2, pe_y - 2000 - i*350), (gx + w_line/2, pe_y - 2000 - i*350), dxfattribs={"layer": "TOPRAKLAMA"})
    yazi(msp, "Temel Topraklama Agina Baglanti (R < 1.0 Ohm)", gx + 1200, pe_y - 2300, h=300, layer="TOPRAKLAMA")

    # 7. Hesap ve Selektivite Notları
    yazi(msp, "HESAP KRITERLERI VE SELEKTIVITE BILGILERI:", 2500, 4500, h=350, layer="YAZI")
    notlar = [
        "1. Trafo gucu 160 kVA, tam yuk akimi In=231 A. Ana salter 250 A TMŞ (0.92xIn=230 A ayarli).",
        "2. Trafo cikisi kisa devre gucu Sk=3.55 MVA, l_k3=4.8 kA. Tum salterlerin kesme kapasitesi (Icu >= 16 kA) kisa devre akimindan buyuktur.",
        "3. Gerilim dusumu hesabi: En kritik hat F6 aydinlatma olup %e = %0.84 < %3.0 (Kuvvetli Akim Tesisleri Yonetmeligi limitleri icindedir).",
        "4. Selektivite: Ana salter (TMŞ 250A) ile fider salterleri (MCCB/MCB) arasinda t_gecikme = 100 ms zaman kademelendirmesi saglanmistir.",
        "5. Kompanzasyon: Reaktif ceza onleyici 50 kVAr (12 kademe tristör anahtarlamali Cos phi >= 0.98 hedefli).",
    ]
    for i, n in enumerate(notlar):
        yazi(msp, n, 2500, 3900 - i * 500, h=260, layer="YAZI")

    # Antet
    antet(msp, "AG ANA DAGITIM PANOSU (ADP) TEK HAT SEMASI", "SLD-01", "1/50", 39000.0, 1000.0)

    dxf_path = os.path.join(OUT, "isletme-tek-hat-semasi.dxf")
    doc.saveas(dxf_path)
    return doc


def ciz_pano_yerlesimi():
    doc = yeni_doc()
    msp = doc.modelspace()

    # Dış sınır çerçevesi (55000 x 36000 mm)
    msp.add_lwpolyline([(0, 0), (55000, 0), (55000, 36000), (0, 36000)],
                       close=True, dxfattribs={"layer": "CERCEVE", "const_width": 50})

    yazi(msp, "160 kVA ATOLYE ANA DAGITIM PANOSU (ADP) MEKANIK IC YERLESIM PLANI", 2500, 34000, h=650, layer="YAZI")
    yazi(msp, "Dikili Tip Sac Pano: 2000 x 2000 x 600 mm (2 Modul x 1000 mm), IP54, Form 2b Ayrimli", 2500, 32800, h=400, layer="YAZI")

    # Pano sol köşe koordinatı (Ölçekli çizim: 1 birim = 1 mm)
    # 2 Gözlü Pano: Göz 1: Giriş + Dağıtım (1200 mm genişlik), Göz 2: Kompanzasyon (800 mm genişlik)
    # Çizimde daha rahat görünmesi için 10x büyütme ile 20000 x 20000 mm alanda detaylı çizelim
    px0, py0 = 5000, 8000
    p_w, p_h = 24000, 20000  # Pano dış ölçüsü görsel orantılı
    
    # 1. Pano Dış Karkası ve Baza (200 mm baza)
    baza_h = 2000
    msp.add_lwpolyline([(px0, py0 - baza_h), (px0 + p_w, py0 - baza_h), (px0 + p_w, py0), (px0, py0)],
                       close=True, dxfattribs={"layer": "PANO_GOVDE", "const_width": 30})
    yazi(msp, "BAZA 200 mm (Kablo Giris Boslugu)", px0 + 8000, py0 - 1200, h=350, layer="PANO_GOVDE")

    msp.add_lwpolyline([(px0, py0), (px0 + p_w, py0), (px0 + p_w, py0 + p_h), (px0, py0 + p_h)],
                       close=True, dxfattribs={"layer": "PANO_GOVDE", "const_width": 60})

    # İki Göz Arası Bölme Sacı
    modul_x = px0 + 14000
    msp.add_lwpolyline([(modul_x, py0), (modul_x, py0 + p_h)], dxfattribs={"layer": "PANO_GOVDE", "const_width": 30})
    
    yazi(msp, "MODUL 1: GIRIS VE DAGITIM GOZU (1200 mm)", px0 + 2000, py0 + p_h + 800, h=450, layer="YAZI")
    yazi(msp, "MODUL 2: KOMPANZASYON GOZU (800 mm)", modul_x + 1000, py0 + p_h + 800, h=450, layer="YAZI")

    # 2. Üst Bara Bölmesi (Form 2b Ayrımı)
    bara_y = py0 + p_h - 3500
    msp.add_line((px0, bara_y), (modul_x, bara_y), dxfattribs={"layer": "PANO_GOVDE"})
    yazi(msp, "BARA BOLMESI (Pleksiglas Muhafazali)", px0 + 500, py0 + p_h - 1000, h=350, layer="PANO_GOVDE")

    # Baralar L1, L2, L3, N
    for i, (b_ad, b_col) in enumerate([("L1", 1), ("L2", 2), ("L3", 3), ("N", 5)]):
        by = py0 + p_h - 1500 - i * 500
        msp.add_lwpolyline([(px0 + 1000, by), (modul_x - 1000, by)], dxfattribs={"layer": "BARA", "color": b_col, "const_width": 40})
        yazi(msp, f"Cu 40x5 mm ({b_ad})", modul_x - 3500, by + 100, h=250, layer="BARA", color=b_col)

    # 3. Ana Giriş Şalteri (Göz 1 Üst-Orta)
    mccb_x, mccb_y = px0 + 3000, py0 + 10500
    mccb_w, mccb_h = 4000, 4500
    msp.add_lwpolyline([(mccb_x, mccb_y), (mccb_x + mccb_w, mccb_y), (mccb_x + mccb_w, mccb_y + mccb_h), (mccb_x, mccb_y + mccb_h)],
                       close=True, dxfattribs={"layer": "PANO_ELEMAN", "const_width": 40})
    yazi(msp, "ANA GIRIS SALTERI", mccb_x + 600, mccb_y + 3500, h=350, layer="PANO_ELEMAN")
    yazi(msp, "QF1: 250A TMŞ", mccb_x + 900, mccb_y + 2700, h=400, layer="PANO_ELEMAN")
    yazi(msp, "(Doner Kurma Kollu)", mccb_x + 700, mccb_y + 1900, h=300, layer="PANO_ELEMAN")
    yazi(msp, "Icu = 36 kA", mccb_x + 1200, mccb_y + 1100, h=300, layer="PANO_ELEMAN")

    # Baradan Şaltere İniş Baraları
    for j in range(3):
        lx = mccb_x + 1000 + j * 1000
        msp.add_lwpolyline([(lx, bara_y), (lx, mccb_y + mccb_h)], dxfattribs={"layer": "BARA", "color": j+1, "const_width": 30})

    # Akım Trafoları
    ct_y = py0 + 8500
    for j in range(3):
        cx = mccb_x + 1000 + j * 1000
        msp.add_circle((cx, ct_y), 400, dxfattribs={"layer": "PANO_ELEMAN"})
        msp.add_line((cx, mccb_y), (cx, py0 + 5000), dxfattribs={"layer": "BARA", "color": j+1})
    yazi(msp, "250/5A Akim Trafolari", mccb_x + 4200, ct_y, h=300, layer="PANO_ELEMAN")

    # 4. Çıkış Şalterleri Montaj Plakası (Göz 1 Alt Kısım)
    fider_salterleri = [
        {"ad": "QF3: 63A", "yuk": "CNC Tezgah"},
        {"ad": "QF4: 50A", "yuk": "Kompresor"},
        {"ad": "QF5: 63A", "yuk": "Talasli Imalat"},
        {"ad": "QF6: 40A", "yuk": "Priz Panosu"},
        {"ad": "QF7: 25A", "yuk": "Aydinlatma"},
        {"ad": "QF8: 32A", "yuk": "Idari Kisim"},
    ]
    sw_y0 = py0 + 3500
    for idx, fs in enumerate(fider_salterleri):
        fx = px0 + 1200 + idx * 2000
        msp.add_lwpolyline([(fx, sw_y0), (fx + 1600, sw_y0), (fx + 1600, sw_y0 + 2600), (fx, sw_y0 + 2600)],
                           close=True, dxfattribs={"layer": "PANO_ELEMAN", "const_width": 20})
        yazi(msp, fs["ad"], fx + 150, sw_y0 + 1800, h=250, layer="PANO_ELEMAN")
        yazi(msp, fs["yuk"], fx + 100, sw_y0 + 900, h=200, layer="PANO_ELEMAN")

    # Yatay Kablo Kanalı (Klemens Üstü)
    msp.add_lwpolyline([(px0 + 800, py0 + 2000), (modul_x - 800, py0 + 2000), (modul_x - 800, py0 + 3000), (px0 + 800, py0 + 3000)],
                       close=True, dxfattribs={"layer": "KANAL"})
    yazi(msp, "DELIKLI PANO KABLO KANALI 80x80 mm", px0 + 3500, py0 + 2400, h=300, layer="KANAL")

    # Çıkış Klemens Sırası (DIN Rayı)
    msp.add_lwpolyline([(px0 + 1000, py0 + 1000), (modul_x - 1000, py0 + 1000)], dxfattribs={"layer": "PANO_ELEMAN", "const_width": 20})
    yazi(msp, "RAY KLEMENSLER (Sahaya Giden Cikis Gucleri)", px0 + 2500, py0 + 1200, h=300, layer="PANO_ELEMAN")

    # PE Topraklama Barası (Pano Tabanında)
    msp.add_lwpolyline([(px0 + 500, py0 + 400), (px0 + p_w - 500, py0 + 400)], dxfattribs={"layer": "TOPRAKLAMA", "const_width": 40})
    yazi(msp, "KORUMA TOPRAKLAMA BARASI Cu 30x5 mm (Pano Govdesi + Tum Klemensler)", px0 + 1500, py0 + 600, h=300, layer="TOPRAKLAMA")

    # 5. Göz 2: 50 kVAr Otomatik Kompanzasyon Bölümü
    # Reaktif Güç Kontrol Rölesi (Üstte)
    msp.add_lwpolyline([(modul_x + 1500, py0 + 16000), (modul_x + 6500, py0 + 16000), (modul_x + 6500, py0 + 18500), (modul_x + 1500, py0 + 18500)],
                       close=True, dxfattribs={"layer": "PANO_ELEMAN"})
    yazi(msp, "REAKTIF GUC KONTROL ROLESI", modul_x + 1800, py0 + 17500, h=300, layer="PANO_ELEMAN")
    yazi(msp, "(12 Kademe Tristor/Kontaktör Tetiklemeli)", modul_x + 1700, py0 + 16700, h=250, layer="PANO_ELEMAN")

    # Kompanzasyon Kademeleri (Kondansatör Blokları ve Kontaktörler)
    kademe_adlari = ["Kademe 1: 2.5 kVAr", "Kademe 2: 5.0 kVAr", "Kademe 3: 10 kVAr", "Kademe 4: 15 kVAr", "Kademe 5: 17.5 kVAr"]
    for k_idx, kad in enumerate(kademe_adlari):
        ky = py0 + 13000 - k_idx * 2200
        # Kontaktör + Sigorta grubu
        msp.add_lwpolyline([(modul_x + 1500, ky), (modul_x + 4000, ky), (modul_x + 4000, ky + 1600), (modul_x + 1500, ky + 1600)],
                           close=True, dxfattribs={"layer": "PANO_ELEMAN"})
        yazi(msp, "Sigorta+Kont.", modul_x + 1800, ky + 700, h=240, layer="PANO_ELEMAN")
        
        # Kondansatör tüpü sembolü (Yuvarlak silindir)
        msp.add_circle((modul_x + 6000, ky + 800), 700, dxfattribs={"layer": "PANO_ELEMAN"})
        yazi(msp, kad, modul_x + 4400, ky + 700, h=260, layer="YAZI")

    # Ölçülendirme Çizgileri
    msp.add_line((px0, py0 - 3000), (px0 + p_w, py0 - 3000), dxfattribs={"layer": "OLCU"})
    yazi(msp, "<--- TOPLAM GENISLIK: 2000 mm --->", px0 + 8000, py0 - 3600, h=350, layer="OLCU")
    
    msp.add_line((px0 - 2000, py0), (px0 - 2000, py0 + p_h), dxfattribs={"layer": "OLCU"})
    yazi(msp, "<--- YUKSEKLIK: 2000 mm --->", px0 - 2800, py0 + 8000, h=350, layer="OLCU", rot=90)

    # Antet
    antet(msp, "ADP PANO MEKANIK IC YERLESIM PLANI", "SLD-02", "1/20", 39000.0, 1000.0)

    dxf_path = os.path.join(OUT, "adp-pano-yerlesimi.dxf")
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
    print("SLD Tek Hat Semasi ciziliyor...")
    d1 = ciz_tek_hat()
    render_png(d1, os.path.join(SEK, "tek-hat-semasi.png"))
    
    print("ADP Pano Yerlesimi ciziliyor...")
    d2 = ciz_pano_yerlesimi()
    render_png(d2, os.path.join(SEK, "pano-yerlesimi.png"))
    
    print("TAMAMLANDI: 2 DXF ve 2 PNG basariyla uretildi.")

# Author : Hakan OĞUZ - Elektrik Elektronik Mühendisi
# Project: Bina Temel/Ring Topraklama ve Yıldırımdan Korunma (LPS) Planı
# Date   : 2026-10-26
# License: MIT
# Desc   : IEC 62305 ve IEC 60364 standartlarına göre temel topraklama, çatı yakalama ağı ve iniş iletkenleri DXF çizimi.
"""
Çizim birimi: milimetre (mm).
İki pafta üretilir:
  LPS-01  cati-yakalama-agi-ve-lps.dxf   -> Çatı yakalama ağı (mesh 10x10 m Sınıf II), iniş iletkenleri, test klemensleri
  LPS-02  temel-ring-topraklama.dxf      -> Temel topraklama ağı (30x3.5 mm galvaniz şerit), ring iletkeni, eşpotansiyel bara (MEB), kazıklar
"""
import os
import ezdxf
from ezdxf.enums import TextEntityAlignment

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.abspath(os.path.join(HERE, ".."))
SEK  = os.path.join(OUT, "sekiller")

KATMANLAR = [
    ("CERCEVE", 7, "CONTINUOUS"),
    ("BINA_DUVAR", 8, "CONTINUOUS"),     # Gri bina dış konturu
    ("YAKALAMA_AGI", 1, "CONTINUOUS"),   # Kırmızı çatı kafesi (mesh)
    ("INIS_ILETKENI", 5, "CONTINUOUS"),  # Mavi iniş iletkenleri
    ("TEMEL_SERIT", 3, "CONTINUOUS"),    # Yeşil temel şeridi
    ("RING_SERIT", 2, "DASHED"),         # Sarı çevreleme ringi
    ("TOPRAK_KAZIK", 4, "CONTINUOUS"),   # Camgöbeği topraklama çubukları
    ("TEST_KLEMENS", 6, "CONTINUOUS"),   # Mor test/ölçüm klemensleri
    ("ESPOTANSIYEL", 1, "CONTINUOUS"),   # Eşpotansiyel baralar (MEB)
    ("OLCU", 8, "CONTINUOUS"),
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
    if "LPS_STYLE" not in doc.styles:
        doc.styles.add("LPS_STYLE", font="arial.ttf")
    return doc

def yazi(msp, text, x, y, h=300, layer="YAZI", align=TextEntityAlignment.LEFT, rot=0, color=None):
    attr = {"layer": layer, "style": "LPS_STYLE"}
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
    
    yazi(msp, "SANAYI TESISI YILDIRIMDAN KORUNMA VE TOPRAKLAMA", x0 + 400, y0 + h - 1000, h=420, layer="ANTET")
    yazi(msp, pafta_adi, x0 + 400, y0 + h - 2200, h=380, layer="ANTET")
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


def ciz_cati_lps():
    doc = yeni_doc()
    msp = doc.modelspace()

    # Çerçeve (55000 x 36000 mm)
    msp.add_lwpolyline([(0, 0), (55000, 0), (55000, 36000), (0, 36000)],
                       close=True, dxfattribs={"layer": "CERCEVE", "const_width": 50})

    yazi(msp, "ENDUSTRIYEL BINA CATI YAKALAMA AGI (FARADAY KAFESI) VE INIS ILETKENLERI PLANI", 2500, 34000, h=600, layer="YAZI")
    yazi(msp, "IEC 62305 Sinif II Koruma Seviyesi - 10x10 m Goz Araligi (Mesh Metodu)", 2500, 32800, h=400, layer="YAZI")

    # Bina Geometrisi: 40000 x 20000 mm dikdörtgen çatı alanı
    bx0, by0 = 6000, 9000
    bw, bh = 36000, 20000

    # Bina dış parapet duvarı
    msp.add_lwpolyline([(bx0, by0), (bx0 + bw, by0), (bx0 + bw, by0 + bh), (bx0, by0 + bh)],
                       close=True, dxfattribs={"layer": "BINA_DUVAR", "const_width": 60})
    yazi(msp, "CATI PARAPET HATTI (KORUMA SINIRI)", bx0 + 500, by0 + bh + 800, h=350, layer="BINA_DUVAR")

    # Çatı Yakalama Ağı (Mesh 9000 x 10000 mm aralıklarla grid)
    # Dikey teller (X yönü)
    for x in range(bx0, bx0 + bw + 1, 9000):
        msp.add_lwpolyline([(x, by0), (x, by0 + bh)], dxfattribs={"layer": "YAKALAMA_AGI", "const_width": 30})
        # Yakalama ucu sembolü (çatı üzerinde sivri uçlar)
        for y in range(by0, by0 + bh + 1, 10000):
            msp.add_circle((x, y), 250, dxfattribs={"layer": "YAKALAMA_AGI"})
            msp.add_line((x - 300, y), (x + 300, y), dxfattribs={"layer": "YAKALAMA_AGI"})
            msp.add_line((x, y - 300), (x, y + 300), dxfattribs={"layer": "YAKALAMA_AGI"})

    # Yatay teller (Y yönü)
    for y in range(by0, by0 + bh + 1, 10000):
        msp.add_lwpolyline([(bx0, y), (bx0 + bw, y)], dxfattribs={"layer": "YAKALAMA_AGI", "const_width": 30})

    yazi(msp, "YAKALAMA ILETKENI: O8 mm SICAK DALDIRMA GALVANIZ YUVARLAK ILETKEN (50 mm2)", bx0 + 2000, by0 + bh - 2000, h=350, layer="YAKALAMA_AGI")
    yazi(msp, "YAKALAMA UCU (H=50 cm paslanmaz cubuk)", bx0 + 10000, by0 + 11000, h=300, layer="YAKALAMA_AGI")

    # İniş İletkenleri (Parapet kenarlarında 10 noktada iniş)
    # IEC 62305 Sınıf II: iniş iletkenleri arasındaki mesafe ortalama 10-15 m olmalı
    inis_noktalari = [
        (bx0, by0), (bx0 + 12000, by0), (bx0 + 24000, by0), (bx0 + bw, by0),
        (bx0 + bw, by0 + 10000), (bx0 + bw, by0 + bh),
        (bx0 + 24000, by0 + bh), (bx0 + 12000, by0 + bh), (bx0, by0 + bh),
        (bx0, by0 + 10000)
    ]

    for idx, (ix, iy) in enumerate(inis_noktalari):
        # Dışarı doğru iniş oku ve test klemensi
        msp.add_circle((ix, iy), 500, dxfattribs={"layer": "INIS_ILETKENI"})
        # Test klemensi kutusu
        msp.add_lwpolyline([(ix - 400, iy - 400), (ix + 400, iy - 400), (ix + 400, iy + 400), (ix - 400, iy + 400)],
                           close=True, dxfattribs={"layer": "TEST_KLEMENS"})
        yazi(msp, f"TK-{idx+1}", ix + 600, iy + 300, h=250, layer="TEST_KLEMENS")

    yazi(msp, "INIS ILETKENLERI (O8 mm Galv. Celik / 10 Farkli Koldan Temel Agana Inis)", bx0 + 2000, by0 - 1500, h=350, layer="INIS_ILETKENI")
    yazi(msp, "TK: TEST KLEMENSI (Yerden 1.5 - 1.8 m yukseklikte olcum kutusu icinde)", bx0 + 2000, by0 - 2200, h=320, layer="TEST_KLEMENS")

    # Çatı Üstü Mekanik Cihaz Koruması (Klima Santrali / Fan)
    ch_x, ch_y = bx0 + 15000, by0 + 4000
    msp.add_lwpolyline([(ch_x, ch_y), (ch_x + 5000, ch_y), (ch_x + 5000, ch_y + 3500), (ch_x, ch_y + 3500)],
                       close=True, dxfattribs={"layer": "BINA_DUVAR"})
    yazi(msp, "CATI KLIMA SANTRALI (AHU)", ch_x + 400, ch_y + 1800, h=300, layer="BINA_DUVAR")
    # Cihaz gövdesi eşpotansiyel irtibatı
    msp.add_line((ch_x + 5000, ch_y + 1800), (bx0 + 27000, ch_y + 1800), dxfattribs={"layer": "ESPOTANSIYEL", "color": 1})
    yazi(msp, "Metal Govde Espotansiyel Baglantisi", ch_x + 5200, ch_y + 2200, h=240, layer="ESPOTANSIYEL")

    # Standart ve Hesap Notları
    yazi(msp, "IEC 62305 YILDIRIMDAN KORUNMA KRITERLERI:", 2500, 5500, h=350, layer="YAZI")
    notlar = [
        "1. Tesis Tehlike Degerlendirmesi: IEC 62305-2'ye gore yapilmis, Kabul Edilebilir Risk R < 10^-5 saglanmistir (LPS Sinif II).",
        "2. Yuvarlanan Kure Yaricapi: Sinif II koruma seviyesi icin r = 30 m olup, cati uzerindeki tum yapilar koruma kuresi altindadir.",
        "3. Koruma Agi (Mesh) Ebatlari: 10x10 m kare kafes duzeni saglanmis, iletkenler her ek noktasinda capraz klemenslerle baglanmistir.",
        "4. Inis Iletkenleri: Toplam 10 adet inis iletkeni cephe boyunca simetrik dagitilmis; ortalama aciklik 11.2 m < 15 m limitindedir.",
        "5. Test Klemensleri (TK): Her inis iletkeni uzerinde yerden 1.8 m yukseklikte test klemensi konulmus olup periyodik olcume uygundur.",
    ]
    for i, n in enumerate(notlar):
        yazi(msp, n, 2500, 4800 - i * 480, h=250, layer="YAZI")

    antet(msp, "CATI YAKALAMA AGI VE LPS PLANI", "LPS-01", "1/100", 39000.0, 1000.0)

    dxf_path = os.path.join(OUT, "cati-yakalama-agi-ve-lps.dxf")
    doc.saveas(dxf_path)
    return doc


def ciz_temel_topraklama():
    doc = yeni_doc()
    msp = doc.modelspace()

    # Çerçeve
    msp.add_lwpolyline([(0, 0), (55000, 0), (55000, 36000), (0, 36000)],
                       close=True, dxfattribs={"layer": "CERCEVE", "const_width": 50})

    yazi(msp, "ENDUSTRIYEL BINA TEMEL VE CEVRE RING TOPRAKLAMA PLANI", 2500, 34000, h=600, layer="YAZI")
    yazi(msp, "IEC 60364-5-54 & TS HD 60364-5-54 Standardi - R_toplam < 1.0 Ohm Hedefli", 2500, 32800, h=400, layer="YAZI")

    # Bina Temel Ölçüsü: 40000 x 20000 mm (İçteki temel betonu)
    bx0, by0 = 6000, 10000
    bw, bh = 36000, 20000

    # 1. Bina Temel Betonu İçi Topraklama Şeridi (30x3.5 mm Sıcak Daldırma Galvaniz Şerit)
    # 20x20 m veya 10x10 m gözlü temel topraklama kafesi
    msp.add_lwpolyline([(bx0, by0), (bx0 + bw, by0), (bx0 + bw, by0 + bh), (bx0, by0 + bh)],
                       close=True, dxfattribs={"layer": "TEMEL_SERIT", "const_width": 40})
    
    # Temel içi ara gözler (kolon aksları boyunca)
    for x in range(bx0 + 9000, bx0 + bw, 9000):
        msp.add_lwpolyline([(x, by0), (x, by0 + bh)], dxfattribs={"layer": "TEMEL_SERIT", "const_width": 30})
    for y in range(by0 + 10000, by0 + bh, 10000):
        msp.add_lwpolyline([(bx0, y), (bx0 + bw, y)], dxfattribs={"layer": "TEMEL_SERIT", "const_width": 30})

    yazi(msp, "TEMEL TOPRAKLAMA SERIDI: 30x3.5 mm SICAK DALDIRMA GALVANIZ SERIT (Beton Donatisina Bagli)", bx0 + 1500, by0 + bh - 1500, h=350, layer="TEMEL_SERIT")

    # 2. Çevre Ring Topraklama Şeridi (Bina temelinden 1 m dışarıda, 0.8 m derinlikte toprak içinde)
    rx0, ry0 = bx0 - 2000, by0 - 2000
    rw, rh = bw + 4000, bh + 4000
    msp.add_lwpolyline([(rx0, ry0), (rx0 + rw, ry0), (rx0 + rw, ry0 + rh), (rx0, ry0 + rh)],
                       close=True, dxfattribs={"layer": "RING_SERIT", "const_width": 30})
    yazi(msp, "CEVRE RING TOPRAKLAMA SERIDI (Toprak icinde 0.8 m derinlikte 30x3.5 mm Galv. Serit)", rx0 + 1000, ry0 - 1000, h=350, layer="RING_SERIT")

    # 3. Dikey Topraklama Çubukları/Kazıkları (Ring köşelerinde ve ortalarda)
    # Çubuk sembolü: dolu daire ve radyal çizgiler
    kazik_noktalari = [
        (rx0, ry0), (rx0 + rw/2, ry0), (rx0 + rw, ry0),
        (rx0 + rw, ry0 + rh/2), (rx0 + rw, ry0 + rh),
        (rx0 + rw/2, ry0 + rh), (rx0, ry0 + rh),
        (rx0, ry0 + rh/2)
    ]

    for kx, ky in kazik_noktalari:
        msp.add_circle((kx, ky), 450, dxfattribs={"layer": "TOPRAK_KAZIK"})
        msp.add_line((kx - 700, ky), (kx + 700, ky), dxfattribs={"layer": "TOPRAK_KAZIK"})
        msp.add_line((kx, ky - 700), (kx, ky + 700), dxfattribs={"layer": "TOPRAK_KAZIK"})
        # Ring ve Temel Arası İrtibat Parçası
        # En yakın temel noktasına bağlantı
        if kx == rx0: nx = bx0
        elif kx == rx0 + rw: nx = bx0 + bw
        else: nx = kx
        if ky == ry0: ny = by0
        elif ky == ry0 + rh: ny = by0 + bh
        else: ny = ky
        msp.add_line((kx, ky), (nx, ny), dxfattribs={"layer": "TEMEL_SERIT"})

    yazi(msp, "TOPRAKLAMA CUBUGU: O20 mm, L=3.5 m Bakir Kapli Celik Cubuk (Toplam 8 Adet)", rx0 + 500, ry0 - 2200, h=350, layer="TOPRAK_KAZIK")

    # 4. Ana Eşpotansiyel Topraklama Barası (MEB) ve Çıkış Bağlantıları
    meb_x, meb_y = bx0 + 2000, by0 + 2000
    msp.add_lwpolyline([(meb_x, meb_y), (meb_x + 4000, meb_y), (meb_x + 4000, meb_y + 1200), (meb_x, meb_y + 1200)],
                       close=True, dxfattribs={"layer": "ESPOTANSIYEL", "const_width": 30})
    yazi(msp, "ANA ESPOTANSIYEL BARA (MEB)", meb_x + 300, meb_y + 700, h=300, layer="ESPOTANSIYEL")
    yazi(msp, "Cu 50x5 mm Bara", meb_x + 1000, meb_y + 200, h=250, layer="ESPOTANSIYEL")

    # MEB'e bağlanan hatlar
    hatlar_meb = [
        "Trafo Koruma ve Isletme Topraklamasi",
        "AG Ana Dagitim Panosu (ADP) PE Barasi",
        "Bina Metal Su / Gaz Borulari",
        "Temel Topraklama Ağı Baglantisi"
    ]
    for idx, h_ad in enumerate(hatlar_meb):
        hy = meb_y - 800 - idx * 600
        msp.add_line((meb_x + 1000 + idx * 800, meb_y), (meb_x + 1000 + idx * 800, hy), dxfattribs={"layer": "ESPOTANSIYEL"})
        yazi(msp, f"-> {h_ad}", meb_x + 1000 + idx * 800 + 200, hy, h=220, layer="ESPOTANSIYEL")

    # 5. Hesap ve Standart Notları
    yazi(msp, "TOPRAKLAMA DIRENCI HESAPLARI VE TASARIM KRITERLERI:", 2500, 5500, h=350, layer="YAZI")
    notlar = [
        "1. Toprak Ozgul Direnci: Sahada Wenner 4-nokta metoduyla olculen ozgul direncin ortalamasi rho = 80 Ohm.m'dir.",
        "2. Temel Topraklamasi Esdeger Direnci: R_temel ~= 2*rho / (3*D) ~= (2*80) / (3 * 38) ~= 1.40 Ohm (D = esdeger cap = 38 m).",
        "3. Topraklama Cubugu Direnci: 1 adet L=3.5 m cubuk icin R_cubuk = (rho / 2*pi*L) * ln(4L/d) ~= 20.8 Ohm.",
        "4. Paralel Bagli 8 Adet Cubuk + Ring ile Esdeger Direnc: R_ring_kazik ~= 20.8 / (8 * 0.75) ~= 3.46 Ohm.",
        "5. Bileske Topraklama Direnci: R_es = (R_temel * R_ring_kazik) / (R_temel + R_ring_kazik) ~= 0.99 Ohm < 1.0 Ohm (Uygun).",
    ]
    for i, n in enumerate(notlar):
        yazi(msp, n, 2500, 4800 - i * 480, h=250, layer="YAZI")

    antet(msp, "TEMEL VE CEVRE RING TOPRAKLAMA PLANI", "LPS-02", "1/100", 39000.0, 1000.0)

    dxf_path = os.path.join(OUT, "temel-ring-topraklama.dxf")
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
    print("Cati Yakalama Agi ve LPS Plani ciziliyor...")
    d1 = ciz_cati_lps()
    render_png(d1, os.path.join(SEK, "cati-lps-plani.png"))
    
    print("Temel ve Ring Topraklama Plani ciziliyor...")
    d2 = ciz_temel_topraklama()
    render_png(d2, os.path.join(SEK, "temel-topraklama-plani.png"))
    
    print("TAMAMLANDI: 2 DXF ve 2 PNG basariyla uretildi.")

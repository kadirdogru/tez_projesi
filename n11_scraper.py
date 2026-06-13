"""
N11 Yorum Scraper — Standardize versiyon
Sütunlar: platform, kategori, urun, urun_url, sira, yorum, kullanici, tarih, yildiz
URL formatı: https://www.n11.com/product-reviews/XXXXXXXX
"""

from scrapling.fetchers import StealthyFetcher
from datetime import datetime
import pandas as pd
import time
import random
import re


def n11_tarihi_iso_yap(tarih_str):
    """'04/05/2026' → '2026-05-04'"""
    if not tarih_str:
        return ''
    try:
        tarih_str = tarih_str.strip()
        parcalar = tarih_str.split('/')
        if len(parcalar) != 3:
            return ''
        gun = parcalar[0].zfill(2)
        ay = parcalar[1].zfill(2)
        yil = parcalar[2]
        return f"{yil}-{ay}-{gun}"
    except:
        return ''


def n11_yorumlari_cek(url, kategori, urun_adi):
    """
    N11'den tüm yorumları çeker (infinite scroll).

    Args:
        url: Yorum sayfası URL'i (https://www.n11.com/product-reviews/XXXXXXXX)
        kategori: 'klima', 'mont', 'sirt_cantasi', 'robot_supurge', 'parfum'
        urun_adi: Ürünün okunabilir adı

    Returns:
        Excel dosya yolu
    """
    print(f"\n{'='*60}")
    print(f"🛒 N11: {urun_adi}")
    print(f"📁 Kategori: {kategori}")
    print(f"{'='*60}")

    def scroll_ve_yukle(page):
        import time as t
        onceki = 0
        deneme = 0
        sayfa_no = 0
        while deneme < 30:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            t.sleep(2.5)
            yeni = page.evaluate("document.body.scrollHeight")
            # Yüklenen yorum sayısını takip et
            yuklenen = page.evaluate(
                "document.querySelectorAll('.review-cart-wrapper__list .card-wrapper.review-card').length"
            )
            sayfa_no += 1
            print(f"   🔄 Scroll {sayfa_no} | Yüklenen yorum: {yuklenen}")
            if yeni == onceki:
                deneme += 1
                t.sleep(1)
            else:
                deneme = 0
                onceki = yeni
        print(f"   ✅ Scroll tamamlandı. Toplam yorum: {yuklenen}")
        return page

    bekleme = random.uniform(5, 10)
    print(f"💭 {bekleme:.1f}s bekleme...")
    time.sleep(bekleme)

    print(f"🌐 Sayfa açılıyor (scroll ile tüm yorumlar yüklenecek)...")
    sayfa = StealthyFetcher.fetch(
        url, headless=True, network_idle=True,
        google_search=True, wait=5000,
        page_action=scroll_ve_yukle
    )

    yorum_kartlari = sayfa.css('.review-cart-wrapper__list .card-wrapper.review-card')
    print(f"📦 {len(yorum_kartlari)} yorum bulundu")

    if len(yorum_kartlari) == 0:
        print("⚠️  Yorum çekilemedi!")
        return None

    yorumlar = []

    for i, kart in enumerate(yorum_kartlari, 1):
        # Yorum metni
        yorum_metni = ''
        icerik = kart.css('.card-detail__contents::text').get()
        if icerik:
            yorum_metni = icerik.strip()

        # Kullanıcı
        kullanici = ''
        kullanici_span = kart.css('.card-detail__name::text').get()
        if kullanici_span:
            kullanici = kullanici_span.strip()

        # Tarih (GG/AA/YYYY → ISO)
        tarih_raw = ''
        tarih_span = kart.css('.star-date__date::text').get()
        if tarih_span:
            tarih_raw = tarih_span.strip()
        tarih_iso = n11_tarihi_iso_yap(tarih_raw)

        # Yıldız — clipPath içindeki rect width=12 olanlar dolu yıldız
        yildiz = 0
        rating_div = kart.css('.rating')
        if rating_div:
            rects = rating_div[0].css('clipPath rect')
            dolu = sum(1 for r in rects if r.attrib.get('width', '0') == '12')
            yildiz = min(5, dolu)

        yorumlar.append({
            'platform': 'n11',
            'kategori': kategori,
            'urun': urun_adi,
            'urun_url': url,
            'sira': i,
            'yorum': yorum_metni,
            'kullanici': kullanici,
            'tarih': tarih_iso,
            'yildiz': yildiz
        })

    df = pd.DataFrame(yorumlar)

    # İstatistik
    print(f"\n📊 {len(df)} tekil yorum")
    print(f"⭐ Yıldız dağılımı: {dict(df['yildiz'].value_counts().sort_index())}")
    print(f"📅 Tarih: {df['tarih'].min()} → {df['tarih'].max()}")
    print(f"💬 Metinli yorum: {(df['yorum'] != '').sum()}/{len(df)}")
    print(f"📅 Tarih dolu: {(df['tarih'] != '').sum()}/{len(df)}")

    # Kaydet
    zaman = datetime.now().strftime('%Y%m%d_%H%M%S')
    urun_temiz = re.sub(r'[^a-zA-Z0-9]', '_', urun_adi)[:30]
    dosya_adi = f"n11_{kategori}_{urun_temiz}_{zaman}.xlsx"
    df.to_excel(dosya_adi, index=False, engine='openpyxl')
    print(f"💾 {dosya_adi} kaydedildi")

    return dosya_adi


# ============ KULLANIM ============
if __name__ == "__main__":

    URUNLER = [
        ('https://www.n11.com/product-reviews/681049355', 'Bargello 384 Floral Kadin Parfum EDP 50 ML'),
        ('https://www.n11.com/product-reviews/227506198', 'Avon Perceive Kadin Parfum EDP 50 ML'),
        ('https://www.n11.com/product-reviews/227504416', 'Avon Rare Pearls Kadin Parfum EDP 50 ML'),
        ('https://www.n11.com/product-reviews/743469311', 'Avon Celebre Kadin Parfum EDT 50 ML'),
        ('https://www.n11.com/product-reviews/435654370', 'Burberry Classic Erkek Parfum EDT 100 ML'),
        ('https://www.n11.com/product-reviews/567566628', 'Davidoff Cool Water Erkek Parfum EDT 125 ML'),
        ('https://www.n11.com/product-reviews/528137309', 'Bargello 709 Oriental Erkek Parfum EDP 50 ML'),
        ('https://www.n11.com/product-reviews/227506193', 'Avon Wish of Love Kadin Parfum EDT 50 ML'),
        ('https://www.n11.com/product-reviews/320275065', 'Kimyagerden E-24 Erkek Parfum EDP 50 ML'),
        ('https://www.n11.com/product-reviews/389248529', 'Bargello 122 Oryantal Kadin Parfum EDP 50 ML'),
        ('https://www.n11.com/product-reviews/639691283', 'Avon Perceive Erkek Parfum EDT 100 ML'),
        ('https://www.n11.com/product-reviews/227499666', 'Avon Individual Blue Erkek Parfum EDT 100 ML'),
        ('https://www.n11.com/product-reviews/389252176', 'Bargello 561 Erkek Parfum EDP 50 ML'),
        ('https://www.n11.com/product-reviews/741051035', 'Avon Incandessence Kadin Parfum EDP 50 ML'),
        ('https://www.n11.com/product-reviews/642053219', 'Avon Musk Marine Erkek Parfum EDT 75 ML'),
        ('https://www.n11.com/product-reviews/404375656', 'Calvin Klein Euphoria Kadin Parfum EDP 100 ML'),
        ('https://www.n11.com/product-reviews/227506185', 'Avon Full Speed Erkek Parfum EDT 100 ML'),
        ('https://www.n11.com/product-reviews/748431129', 'Joop Homme Erkek Parfum EDT 125 ML'),
        ('https://www.n11.com/product-reviews/722349264', 'Avon Pur Blanca Kadin Parfum EDT 50 ML'),
    ]

    basarili = []
    basarisiz = []

    for i, (url, urun_adi) in enumerate(URUNLER, 1):
        print(f"\n{'#'*60}")
        print(f"# ÜRÜN {i}/{len(URUNLER)}: {urun_adi}")
        print(f"{'#'*60}")
        try:
            dosya = n11_yorumlari_cek(url=url, kategori='parfum', urun_adi=urun_adi)
            if dosya:
                basarili.append(urun_adi)
            else:
                basarisiz.append(urun_adi)
        except Exception as e:
            print(f"❌ HATA: {e}")
            basarisiz.append(urun_adi)

        # Son ürün değilse bekle
        if i < len(URUNLER):
            bekleme = random.uniform(30, 60)
            print(f"\n⏳ Sonraki ürün için {bekleme:.0f}s bekleniyor...")
            time.sleep(bekleme)

    print(f"\n{'='*60}")
    print(f"✅ Başarılı: {len(basarili)}/{len(URUNLER)}")
    print(f"❌ Başarısız: {basarisiz if basarisiz else 'Yok'}")
    print(f"{'='*60}")
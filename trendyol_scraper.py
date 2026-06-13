"""
Trendyol Yorum Scraper — Standardize versiyon
Sütunlar: platform, kategori, urun, urun_url, sira, yorum, kullanici, tarih, yildiz
"""

from scrapling.fetchers import StealthyFetcher
from datetime import datetime
import pandas as pd
import time
import random
import re

# Türkçe ay adları → ISO ay numaraları
TURKCE_AY = {
    'Ocak': '01', 'Şubat': '02', 'Mart': '03', 'Nisan': '04',
    'Mayıs': '05', 'Haziran': '06', 'Temmuz': '07', 'Ağustos': '08',
    'Eylül': '09', 'Ekim': '10', 'Kasım': '11', 'Aralık': '12'
}


def turkce_tarihi_iso_yap(turkce_tarih):
    """'26 Ağustos 2024' → '2024-08-26'"""
    if not turkce_tarih:
        return ''
    try:
        parcalar = turkce_tarih.strip().split()
        if len(parcalar) != 3:
            return ''
        gun = parcalar[0].zfill(2)
        ay = TURKCE_AY.get(parcalar[1], '')
        yil = parcalar[2]
        if not ay:
            return ''
        return f"{yil}-{ay}-{gun}"
    except:
        return ''


def trendyol_yorumlari_cek(url, kategori, urun_adi):
    """
    Trendyol'dan tüm yorumları çeker.

    Args:
        url: Yorum sayfası URL'i (sonu /yorumlar olmalı)
        kategori: 'klima', 'mont', 'sirt_cantasi', 'robot_supurge', 'parfum'
        urun_adi: Ürünün okunabilir adı

    Returns:
        Excel dosya yolu
    """
    print(f"\n{'='*60}")
    print(f"🛒 TRENDYOL: {urun_adi}")
    print(f"📁 Kategori: {kategori}")
    print(f"{'='*60}")

    PADDING_PER_YILDIZ = 16.7143

    def scroll_ve_yukle(page):
        import time as t
        onceki = 0
        deneme = 0
        sayac = 0
        yuklenen = 0
        while deneme < 30:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            t.sleep(2.5)
            yeni = page.evaluate("document.body.scrollHeight")
            yuklenen = page.evaluate("document.querySelectorAll('.review').length")
            sayac += 1
            print(f"   🔄 Scroll {sayac} | Yüklenen yorum: {yuklenen}")
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

    yorum_kartlari = sayfa.css('.review')
    print(f"📦 {len(yorum_kartlari)} yorum bulundu")

    if len(yorum_kartlari) == 0:
        print("⚠️  Yorum çekilemedi!")
        return None

    yorumlar = []

    for i, kart in enumerate(yorum_kartlari, 1):
        # Yorum metni
        yorum_metni = ''
        spans = kart.css('.review-comment span::text').getall()
        if spans:
            yorum_metni = max(spans, key=len).strip()

        # Kullanıcı
        kullanici = ''
        info = kart.css('.review-info ::text').getall()
        for m in info:
            m = m.strip()
            if m and len(m) < 50:
                kullanici = m
                break

        # Tarih (Türkçe → ISO)
        tarih_turkce = ''
        tarih_div = kart.css('.detail-item.date')
        if tarih_div:
            parcalar = tarih_div[0].css('span::text').getall()
            if parcalar:
                tarih_turkce = ' '.join([p.strip() for p in parcalar if p.strip()])

        tarih_iso = turkce_tarihi_iso_yap(tarih_turkce)

        # Yıldız
        yildiz = 0
        full_star = kart.css('.star-rating-full-star')
        if full_star:
            style = full_star[0].attrib.get('style', '')
            m = re.search(r'padding-inline-end:\s*([\d.]+)px', style)
            if m:
                padding = float(m.group(1))
                yildiz = round(5 - (padding / PADDING_PER_YILDIZ))
                yildiz = max(1, min(5, yildiz))

        yorumlar.append({
            'platform': 'trendyol',
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
    dosya_adi = f"trendyol_{kategori}_{urun_temiz}_{zaman}.xlsx"
    df.to_excel(dosya_adi, index=False, engine='openpyxl')
    print(f"💾 {dosya_adi} kaydedildi")

    return dosya_adi


# ============ KULLANIM ============
if __name__ == "__main__":

    URUNLER = [
        ('https://www.trendyol.com/mad-parfum/mad-v112-selective-50-ml-kadin-parfum-p-762581409/yorumlar', 'Mad Parfum V112 Selective 50 ML Kadin'),
        ('https://www.trendyol.com/mad-parfum/mad-z101-selective-50-ml-kadin-parfum-p-358492333/yorumlar', 'Mad Parfum Z101 Selective 50 ML Kadin'),
        ('https://www.trendyol.com/bargello/122-oriental-edp-50-ml-kadin-parfum-p-34117164/yorumlar', 'Bargello 122 Oriental EDP 50 ML Kadin'),
        ('https://www.trendyol.com/avon/wish-of-love-kadin-parfum-edt-50-ml-ikili-set-p-37119229/yorumlar', 'Avon Wish of Love Kadin EDT 50 ML'),
        ('https://www.trendyol.com/bargello/erkek-parfum-561-fresh-50-ml-edp-8691841304531-p-32332095/yorumlar', 'Bargello 561 Fresh EDP 50 ML Erkek'),
        ('https://www.trendyol.com/mad-parfum/mad-h105-selective-50-ml-kadin-parfum-p-354100348/yorumlar', 'Mad Parfum H105 Selective 50 ML Kadin'),
        ('https://www.trendyol.com/lumenascent/liora-kadin-parfum-floral-edp-50-ml-p-971347342/yorumlar', 'Lumenascent Liora Kadin Floral EDP 50 ML'),
        ('https://www.trendyol.com/aqua-di-polo-1987/la-rocca-sense-edp-kadin-parfum-50-ml-ciceksi-oryantal-portakal-cicegi-kahve-yasemin-vanilya-p-88741299/yorumlar', 'Aqua di Polo La Rocca Sense EDP 50 ML'),
        ('https://www.trendyol.com/bargello/384-kadin-50-ml-parfum-edp-floral-p-93595097/yorumlar', 'Bargello 384 Floral EDP 50 ML Kadin'),
        ('https://www.trendyol.com/tdrs/narcotic-100-ml-bergamot-ozel-seri-uzun-sure-kalici-erkek-parfum-p-729812633/yorumlar', 'TDRS Narcotic 100 ML Bergamot Erkek'),
        ('https://www.trendyol.com/avon/perceive-erkek-parfum-edt-100-ml-p-1206454/yorumlar', 'Avon Perceive Erkek EDT 100 ML'),
        ('https://www.trendyol.com/bargello/228-kadin-50-ml-parfum-edp-oriental-p-113818622/yorumlar', 'Bargello 228 Oriental EDP 50 ML Kadin'),
    ]

    basarili = []
    basarisiz = []

    for i, (url, urun_adi) in enumerate(URUNLER, 1):
        print(f"\n{'#'*60}")
        print(f"# ÜRÜN {i}/{len(URUNLER)}: {urun_adi}")
        print(f"{'#'*60}")
        try:
            dosya = trendyol_yorumlari_cek(url=url, kategori='parfum', urun_adi=urun_adi)
            if dosya:
                basarili.append(urun_adi)
            else:
                basarisiz.append(urun_adi)
        except Exception as e:
            print(f"❌ HATA: {e}")
            basarisiz.append(urun_adi)

        if i < len(URUNLER):
            bekleme = random.uniform(30, 60)
            print(f"\n⏳ Sonraki ürün için {bekleme:.0f}s bekleniyor...")
            time.sleep(bekleme)

    print(f"\n{'='*60}")
    print(f"✅ Başarılı: {len(basarili)}/{len(URUNLER)}")
    print(f"❌ Başarısız: {basarisiz if basarisiz else 'Yok'}")
    print(f"{'='*60}")
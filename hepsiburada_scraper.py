"""
Hepsiburada Yorum Scraper — Standardize versiyon
Sütunlar: platform, kategori, urun, urun_url, sira, yorum, kullanici, tarih, yildiz
"""

from scrapling.fetchers import StealthyFetcher
from scrapling.parser import Selector
from datetime import datetime
import pandas as pd
import time
import random


def hepsiburada_yorumlari_cek(url, kategori, urun_adi):
    """
    Hepsiburada'dan tüm yorumları çeker (pagination ile).
    
    Args:
        url: Yorum sayfası URL'i (sonu /yorumlari olmalı, "i" ile)
        kategori: 'klima', 'mont', 'sirt_cantasi', 'robot_supurge', 'parfum'
        urun_adi: Ürünün okunabilir adı
    
    Returns:
        Excel dosya yolu
    """
    print(f"\n{'='*60}")
    print(f"🛒 HEPSİBURADA: {urun_adi}")
    print(f"📁 Kategori: {kategori}")
    print(f"{'='*60}")
    
    TUM_SAYFA_HTMLLERI = []
    
    def sayfalari_gez(page):
        import time as t

        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        t.sleep(3)
        
        # İlk sayfa
        TUM_SAYFA_HTMLLERI.append(page.content())
        print("   📄 Sayfa 1 alındı")
        
        butonlar = page.query_selector_all('div[class*="paginationBarHolder"] li[class*="PageHolder"]')
        if not butonlar:
            return page
        
        sayfa_numaralari = []
        for btn in butonlar:
            try:
                metin = btn.inner_text().strip()
                if metin.isdigit():
                    sayfa_numaralari.append(int(metin))
            except:
                continue
        
        if not sayfa_numaralari:
            return page
        
        toplam_sayfa = max(sayfa_numaralari)
        print(f"   📊 Toplam {toplam_sayfa} sayfa\n")
        
        su_anki_sayfa = 1
        
        while su_anki_sayfa < toplam_sayfa:
            hedef_sayfa = su_anki_sayfa + 1
            
            try:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                t.sleep(1.0)
                
                butonlar = page.query_selector_all('div[class*="paginationBarHolder"] li[class*="PageHolder"]')
                
                tiklandi = False
                for btn in butonlar:
                    try:
                        metin = btn.inner_text().strip()
                        if metin == str(hedef_sayfa):
                            btn.scroll_into_view_if_needed()
                            t.sleep(0.7)
                            btn.click()
                            tiklandi = True
                            break
                    except:
                        continue
                
                if not tiklandi:
                    # Hedef görünmüyor, en yüksek görünen numaraya atla
                    en_yuksek_btn = None
                    en_yuksek_no = 0
                    for btn in butonlar:
                        try:
                            metin = btn.inner_text().strip()
                            if metin.isdigit() and int(metin) > su_anki_sayfa:
                                if int(metin) > en_yuksek_no:
                                    en_yuksek_no = int(metin)
                                    en_yuksek_btn = btn
                        except:
                            continue
                    
                    if en_yuksek_btn:
                        en_yuksek_btn.scroll_into_view_if_needed()
                        t.sleep(0.7)
                        en_yuksek_btn.click()
                        hedef_sayfa = en_yuksek_no
                        tiklandi = True
                        print(f"   ⏭️  Sayfa {su_anki_sayfa+1} görünmüyor, sayfa {hedef_sayfa}'e atlandı")
                
                if not tiklandi:
                    print(f"   ❌ Hiçbir buton bulunamadı, durduruyoruz")
                    break
                
                t.sleep(random.uniform(3.5, 5.0))
                
                TUM_SAYFA_HTMLLERI.append(page.content())
                su_anki_sayfa = hedef_sayfa
                print(f"   📄 Sayfa {su_anki_sayfa} alındı")
                
            except Exception as e:
                print(f"   ❌ Sayfa {hedef_sayfa} hatası: {str(e)[:80]}")
                su_anki_sayfa = hedef_sayfa
        
        return page
    
    bekleme = random.uniform(5, 10)
    print(f"💭 {bekleme:.1f}s bekleme...")
    time.sleep(bekleme)
    
    print(f"🌐 Sayfa açılıyor...\n")
    
    sayfa = StealthyFetcher.fetch(
        url, headless=True, network_idle=True,
        google_search=True, wait=5000,
        page_action=sayfalari_gez
    )
    
    print(f"\n✅ Toplam {len(TUM_SAYFA_HTMLLERI)} sayfa biriktirildi")
    print("📥 Yorumlar parse ediliyor...\n")
    
    yorumlar = []
    
    # Her sayfa için, o sayfanın HTML'ini parse et
    # NOT: Sayfa 1'in HTML'i tüm sayfalar görünür haliyle bekleyebilir, 
    # bu yüzden 1. HTML'den ilk 10 yorumu, 2. HTML'den 11-20 arası... 
    # ALTERNATİF: Tüm HTML'lerden tüm yorumları al, duplikatlarda hangi sayfadan 
    # geldiği bilgisini koru. İlk gözüktüğü sayfa = gerçek sayfası.
    
    gorulen = set()  # (kullanici, tarih) tuple'ları
    
    for sayfa_no, html in enumerate(TUM_SAYFA_HTMLLERI, 1):
        selector = Selector(html)
        yorum_kartlari = selector.css('div[class*="ReviewCard-module-dY_oaYMIo"]')
        
        for kart in yorum_kartlari:
            # Yorum metni — SADECE text-align:start span (yedek mantık YOK)
            yorum_metni = ''
            yorum_span = kart.css('span[style*="text-align"]::text').get()
            if yorum_span:
                yorum_metni = yorum_span.strip()
            
            # Tarih (content attribute, ISO)
            tarih = ''
            tarih_span = kart.css('span[content]')
            if tarih_span:
                tarih = tarih_span[0].attrib.get('content', '')
            
            # Kullanıcı
            kullanici = ''
            kullanici_span = kart.css('span[class*="ooww5HUv"]::text').get()
            if kullanici_span:
                kullanici = kullanici_span.strip()
            
            if not kullanici:
                spanlar = kart.css('span::text').getall()
                for s in spanlar:
                    s = s.strip()
                    if '*' in s and len(s) < 30:
                        kullanici = s
                        break
            
            # Yıldız
            full_stars = kart.css('div.star')
            yildiz = len(full_stars) if full_stars else 0
            yildiz = min(5, yildiz)
            
            # Tekrar tespiti — bu yorum daha önce gözüktü mü?
            anahtar = (kullanici, tarih, yorum_metni)  # tam metin
            if anahtar in gorulen:
                continue  # bu yorum zaten kaydedildi (önceki sayfada gözüktü)
            gorulen.add(anahtar)
            
            yorumlar.append({
                'platform': 'hepsiburada',
                'kategori': kategori,
                'urun': urun_adi,
                'urun_url': url,
                'sira': sayfa_no,  # Hepsiburada'da sayfa numarası
                'yorum': yorum_metni,
                'kullanici': kullanici,
                'tarih': tarih,
                'yildiz': yildiz
            })
    
    df = pd.DataFrame(yorumlar)
    
    if len(df) == 0:
        print("⚠️  Yorum çekilemedi, sayfa yönlendirilmiş olabilir (301).")
        return None

    print(f"📊 {len(df)} tekil yorum")
    if 'yildiz' in df.columns and df['yildiz'].notna().any():
        print(f"⭐ Yıldız dağılımı: {dict(df['yildiz'].value_counts().sort_index())}")
    tarihli = df[df['tarih'] != '']
    if len(tarihli) > 0:
        print(f"📅 Tarih: {tarihli['tarih'].min()} → {tarihli['tarih'].max()}")
    print(f"💬 Metinli yorum: {(df['yorum'] != '').sum()}/{len(df)}")
    print(f"📅 Tarih dolu: {(df['tarih'] != '').sum()}/{len(df)}")
    
    # Kaydet
    zaman = datetime.now().strftime('%Y%m%d_%H%M%S')
    import re
    urun_temiz = re.sub(r'[^a-zA-Z0-9]', '_', urun_adi)[:30]
    dosya_adi = f"hepsiburada_{kategori}_{urun_temiz}_{zaman}.xlsx"
    df.to_excel(dosya_adi, index=False, engine='openpyxl')
    print(f"💾 {dosya_adi} kaydedildi")
    
    return dosya_adi


# ============ KULLANIM ============
if __name__ == "__main__":

    URUNLER = [
        ('https://www.hepsiburada.com/calvin-klein-euphoria-edp-100-ml-kadin-parfum-p-SGCK056023040-yorumlari', 'Calvin Klein Euphoria EDP 100 ML Kadin'),
        ('https://www.hepsiburada.com/bargello-561-erkek-parfum-edp-50-ml-fresh-p-HBV00000N6KGG-yorumlari', 'Bargello 561 Fresh EDP 50 ML Erkek'),
        ('https://www.hepsiburada.com/calvin-klein-one-edt-200-ml-unisex-parfum-p-SGCK0560743-yorumlari', 'Calvin Klein One EDT 200 ML Unisex'),
        ('https://www.hepsiburada.com/avon-perceive-edt-100-ml-erkek-parfum-p-SGAVONZF008G-yorumlari', 'Avon Perceive EDT 100 ML Erkek'),
        ('https://www.hepsiburada.com/davidoff-cool-water-edt-125-ml-erkek-parfum-p-SGDAV0580153-yorumlari', 'Davidoff Cool Water EDT 125 ML Erkek'),
        ('https://www.hepsiburada.com/joop-homme-bay-parfum-125-ml-p-SGJOP054211-yorumlari', 'Joop Homme Erkek Parfum 125 ML'),
        ('https://www.hepsiburada.com/burberry-classic-kadin-parfumu-edp-100-ml-odunsu-meyvemsi-ciceksi-koku-ile-zarif-bir-secim-p-SGSBW9001-yorumlari', 'Burberry Classic EDP 100 ML Kadin'),
        ('https://www.hepsiburada.com/bargello-709-50-ml-erkek-parfum-edp-odunsu-koku-ile-modern-hediye-secenegi-p-HBV00000QYSCQ-yorumlari', 'Bargello 709 EDP 50 ML Erkek'),
        ('https://www.hepsiburada.com/avon-incandessence-edp-50-ml-kadin-parfum-p-SGAVONPARFUM0014-yorumlari', 'Avon Incandessence EDP 50 ML Kadin'),
        ('https://www.hepsiburada.com/farmasi-shooter-s-man-edp-100-ml-erkek-parfumu-odunsu-ve-baharatli-koku-ile-hediye-secenegi-p-HBV000006UPNG-yorumlari', 'Farmasi Shooters Man EDP 100 ML Erkek'),
        ('https://www.hepsiburada.com/bargello-kadin-parfum-122-oriental-50-ml-edp-odunsu-koku-gunluk-kullanima-uygun-p-HBV00000ONJ70-yorumlari', 'Bargello 122 Oriental EDP 50 ML Kadin'),
        ('https://www.hepsiburada.com/avon-wish-of-love-kadin-parfum-edt-50-ml-p-SGAVONPARFUM0305-yorumlari', 'Avon Wish of Love EDT 50 ML Kadin'),
        ('https://www.hepsiburada.com/versace-eros-edt-100-ml-erkek-parfum-odunsu-turuncgil-koku-ile-tutkulu-ve-guclu-p-SGTK8011003809219-yorumlari', 'Versace Eros EDT 100 ML Erkek'),
        ('https://www.hepsiburada.com/burberry-classic-100-ml-erkek-parfum-edt-odunsu-ve-ciceksi-koku-ile-sik-ve-sofistike-p-SGSBM8001-yorumlari', 'Burberry Classic EDT 100 ML Erkek'),
    ]

    basarili = []
    basarisiz = []

    for i, (url, urun_adi) in enumerate(URUNLER, 1):
        print(f"\n{'#'*60}")
        print(f"# ÜRÜN {i}/{len(URUNLER)}: {urun_adi}")
        print(f"{'#'*60}")
        try:
            dosya = hepsiburada_yorumlari_cek(url=url, kategori='parfum', urun_adi=urun_adi)
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
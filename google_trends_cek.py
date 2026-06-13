import pandas as pd
from pytrends.request import TrendReq
import time
import os

# Sadece eksik 3 kategori
KATEGORILER = {
    'sirt_cantasi': 'sırt çantası',
    'robot_supurge': 'robot süpürge',
    'parfum': 'parfüm'
}

CIKTI_KLASOR = r'C:\Users\MONSTER\OneDrive\Desktop\tez_projesi'
BASLIK = '2023-06-01 2026-05-04'

pytrends = TrendReq(hl='tr-TR', tz=180)

tum_veriler = []

for dosya_adi, arama_kelimesi in KATEGORILER.items():
    print(f"Çekiliyor: {arama_kelimesi} ...")
    
    basari = False
    deneme = 0
    
    while not basari and deneme < 3:
        try:
            pytrends.build_payload(
                kw_list=[arama_kelimesi],
                cat=0,
                timeframe=BASLIK,
                geo='TR',
                gprop=''
            )
            
            df = pytrends.interest_over_time()
            
            if df.empty:
                print(f"  UYARI: {arama_kelimesi} için veri gelmedi!")
                break
            
            df = df.drop(columns=['isPartial'], errors='ignore')
            df = df.reset_index()
            df.columns = ['tarih', 'trends_skoru']
            df['kategori'] = dosya_adi
            df['arama_kelimesi'] = arama_kelimesi
            
            tum_veriler.append(df)
            print(f"  OK: {len(df)} hafta çekildi")
            basari = True
            
        except Exception as e:
            deneme += 1
            print(f"  HATA (deneme {deneme}/3): {e}")
            if deneme < 3:
                bekleme = 60 * deneme  # 60s, 120s, 180s
                print(f"  {bekleme} saniye bekleniyor...")
                time.sleep(bekleme)
    
    if basari:
        print(f"  Sonraki kategori için 45 saniye bekleniyor...")
        time.sleep(45)

# Mevcut dosyaya ekle
cikti_yolu = os.path.join(CIKTI_KLASOR, 'google_trends_haftalik.xlsx')

if tum_veriler:
    yeni_veri = pd.concat(tum_veriler, ignore_index=True)
    
    # Varolan dosya varsa üstüne ekle
    if os.path.exists(cikti_yolu):
        mevcut = pd.read_excel(cikti_yolu)
        sonuc = pd.concat([mevcut, yeni_veri], ignore_index=True)
        print(f"\nMevcut dosyaya eklendi.")
    else:
        sonuc = yeni_veri
    
    sonuc.to_excel(cikti_yolu, index=False)
    print(f"Kaydedildi: {cikti_yolu}")
    print(f"Toplam satır: {len(sonuc)}")
    print(sonuc.groupby('kategori')['tarih'].count())
else:
    print("Hiç veri çekilemedi — biraz bekleyip tekrar dene.")
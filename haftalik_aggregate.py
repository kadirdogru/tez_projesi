import pandas as pd
import os

KLASOR = r'C:\Users\MONSTER\OneDrive\Desktop\tez_projesi'

KATEGORILER = ['klima', 'mont', 'sirt_cantasi', 'robot_supurge', 'parfum']

tum_veriler = []

for kategori in KATEGORILER:
    dosya = os.path.join(KLASOR, f'{kategori}_master.xlsx')
    print(f"Yükleniyor: {kategori} ...")
    
    df = pd.read_excel(dosya)
    df['tarih'] = pd.to_datetime(df['tarih'])
    
    # Analiz filtresi
    df = df[(df['tarih'] >= '2023-06-01') & (df['tarih'] <= '2026-05-04') & (df['yildiz'] > 0)]
    
    # Haftalık aggregate (Pazartesi bazlı)
    df['hafta'] = df['tarih'].dt.to_period('W-MON').apply(lambda x: x.start_time)
    
    haftalik = df.groupby('hafta').agg(
        yorum_sayisi=('yorum', 'count'),
        ort_yildiz=('yildiz', 'mean')
    ).reset_index()
    
    haftalik['kategori'] = kategori
    tum_veriler.append(haftalik)
    print(f"  OK: {len(haftalik)} hafta, {len(df)} yorum")

sonuc = pd.concat(tum_veriler, ignore_index=True)

# Kaydet
cikti = os.path.join(KLASOR, 'haftalik_yorum_aggregate.xlsx')
sonuc.to_excel(cikti, index=False)
print(f"\nKaydedildi: {cikti}")
print(f"Toplam satır: {len(sonuc)}")
print(sonuc.groupby('kategori')['hafta'].count())
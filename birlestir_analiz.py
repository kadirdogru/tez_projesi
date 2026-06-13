import pandas as pd
import os

KLASOR = r'C:\Users\MONSTER\OneDrive\Desktop\tez_projesi'

trends = pd.read_excel(os.path.join(KLASOR, 'google_trends_haftalik.xlsx'))
yorumlar = pd.read_excel(os.path.join(KLASOR, 'haftalik_yorum_aggregate.xlsx'))

trends['tarih'] = pd.to_datetime(trends['tarih'])
yorumlar['hafta'] = pd.to_datetime(yorumlar['hafta'])

# İkisini de o haftanın Pazartesi'sine normalize et
trends['hafta'] = trends['tarih'] - pd.to_timedelta(trends['tarih'].dt.dayofweek, unit='D')
yorumlar['hafta'] = yorumlar['hafta'] - pd.to_timedelta(yorumlar['hafta'].dt.dayofweek, unit='D')

df = pd.merge(
    yorumlar,
    trends[['hafta', 'kategori', 'trends_skoru']],
    on=['hafta', 'kategori'],
    how='inner'
)

df = df.sort_values(['kategori', 'hafta']).reset_index(drop=True)

cikti = os.path.join(KLASOR, 'analiz_dataset.xlsx')
df.to_excel(cikti, index=False)

print(f"Kaydedildi: {cikti}")
print(f"Toplam satır: {len(df)}")
print(df.groupby('kategori')['hafta'].count())
print()
print(df.head())
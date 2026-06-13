import pandas as pd
import os

KLASOR = r'C:\Users\MONSTER\OneDrive\Desktop\tez_projesi'
KATEGORILER = ['klima', 'mont', 'sirt_cantasi', 'robot_supurge', 'parfum']

toplam = 0
for kategori in KATEGORILER:
    df = pd.read_excel(os.path.join(KLASOR, f'{kategori}_master.xlsx'))
    df['tarih'] = pd.to_datetime(df['tarih'])
    filtreli = df[(df['tarih'] >= '2023-06-01') & (df['tarih'] <= '2026-05-04') & (df['yildiz'] > 0)]
    print(f"{kategori:15} Ham: {len(df):6}  Filtreli: {len(filtreli):6}")
    toplam += len(filtreli)

print(f"\nToplam ham: 294.403")
print(f"Toplam filtreli (analizde kullanılan): {toplam}")
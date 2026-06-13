import pandas as pd
import os

KLASOR = r'C:\Users\MONSTER\OneDrive\Desktop\tez_projesi'

trends = pd.read_excel(os.path.join(KLASOR, 'google_trends_haftalik.xlsx'))
yorumlar = pd.read_excel(os.path.join(KLASOR, 'haftalik_yorum_aggregate.xlsx'))

print("=== TRENDS ===")
print(trends.dtypes)
print(trends['tarih'].head(3))
print()
print("=== YORUMLAR ===")
print(yorumlar.dtypes)
print(yorumlar['hafta'].head(3))
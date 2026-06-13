import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_percentage_error
import warnings
import os
warnings.filterwarnings('ignore')

KLASOR = r'C:\Users\MONSTER\OneDrive\Desktop\tez_projesi'
df = pd.read_excel(os.path.join(KLASOR, 'analiz_dataset.xlsx'))
df['hafta'] = pd.to_datetime(df['hafta'])

KATEGORILER = ['klima', 'mont', 'sirt_cantasi', 'robot_supurge', 'parfum']

# Son 20 hafta test, geri kalan train
TEST_HAFTA = 20

sonuclar = []

for kategori in KATEGORILER:
    print(f"\n{'='*50}")
    print(f"ARIMA — {kategori.upper()}")
    
    veri = df[df['kategori'] == kategori].sort_values('hafta')
    y = veri['yorum_sayisi'].values.astype(float)
    
    train = y[:-TEST_HAFTA]
    test = y[-TEST_HAFTA:]
    
    # En iyi (p,d,q) kombinasyonunu ara
    en_iyi_aic = np.inf
    en_iyi_order = (1, 1, 1)
    
    for p in range(0, 4):
        for d in range(0, 2):
            for q in range(0, 4):
                try:
                    model = ARIMA(train, order=(p, d, q))
                    fit = model.fit()
                    if fit.aic < en_iyi_aic:
                        en_iyi_aic = fit.aic
                        en_iyi_order = (p, d, q)
                except:
                    continue
    
    print(f"En iyi order: {en_iyi_order} (AIC={en_iyi_aic:.2f})")
    
    # Final model
    model = ARIMA(train, order=en_iyi_order)
    fit = model.fit()
    tahmin = fit.forecast(steps=TEST_HAFTA)
    
    mape = mean_absolute_percentage_error(test, tahmin) * 100
    mae = np.mean(np.abs(test - tahmin))
    
    print(f"MAPE: {mape:.2f}%")
    print(f"MAE:  {mae:.2f}")
    
    sonuclar.append({
        'kategori': kategori,
        'model': 'ARIMA',
        'order': str(en_iyi_order),
        'mape': round(mape, 2),
        'mae': round(mae, 2)
    })

# Kaydet
ozet = pd.DataFrame(sonuclar)
print(f"\n{'='*50}")
print("ÖZET")
print(ozet.to_string(index=False))

ozet.to_excel(os.path.join(KLASOR, 'arima_sonuclari.xlsx'), index=False)
print(f"\nKaydedildi: arima_sonuclari.xlsx")
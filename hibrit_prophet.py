import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_absolute_percentage_error
import warnings
import os
warnings.filterwarnings('ignore')

KLASOR = r'C:\Users\MONSTER\OneDrive\Desktop\tez_projesi'
df = pd.read_excel(os.path.join(KLASOR, 'analiz_dataset.xlsx'))
df['hafta'] = pd.to_datetime(df['hafta'])

KATEGORILER = ['klima', 'mont', 'sirt_cantasi', 'robot_supurge', 'parfum']
TEST_HAFTA = 20

sonuclar = []

for kategori in KATEGORILER:
    print(f"\n{'='*50}")
    print(f"HİBRİT PROPHET — {kategori.upper()}")
    
    veri = df[df['kategori'] == kategori].sort_values('hafta').reset_index(drop=True)
    
    prophet_df = veri[['hafta', 'yorum_sayisi', 'trends_skoru']].rename(
        columns={'hafta': 'ds', 'yorum_sayisi': 'y'}
    )
    
    train = prophet_df.iloc[:-TEST_HAFTA]
    test = prophet_df.iloc[-TEST_HAFTA:]
    
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_mode='multiplicative'
    )
    
    # Trends skoru regressor olarak eklendi
    model.add_regressor('trends_skoru')
    model.fit(train)
    
    future = test[['ds', 'trends_skoru']].copy()
    forecast = model.predict(future)
    
    tahmin = np.maximum(forecast['yhat'].values, 0)
    gercek = test['y'].values
    
    mape = mean_absolute_percentage_error(gercek, tahmin) * 100
    mae = np.mean(np.abs(gercek - tahmin))
    
    print(f"MAPE: {mape:.2f}%")
    print(f"MAE:  {mae:.2f}")
    
    sonuclar.append({
        'kategori': kategori,
        'model': 'Prophet Hibrit',
        'mape': round(mape, 2),
        'mae': round(mae, 2)
    })

# Baseline ile karşılaştır
baseline = pd.read_excel(os.path.join(KLASOR, 'prophet_sonuclari.xlsx'))
hibrit = pd.DataFrame(sonuclar)

print(f"\n{'='*50}")
print("PROPHET vs HİBRİT PROPHET KARŞILAŞTIRMA")
print(f"{'='*50}")

for kategori in KATEGORILER:
    b_mape = baseline[baseline['kategori'] == kategori]['mape'].values[0]
    h_mape = hibrit[hibrit['kategori'] == kategori]['mape'].values[0]
    fark = b_mape - h_mape
    yon = '✓ İYİLEŞTİ' if fark > 0 else '✗ KÖTÜLEŞTI'
    print(f"{kategori:15} Baseline: {b_mape:6.2f}%  Hibrit: {h_mape:6.2f}%  Fark: {fark:+.2f}% {yon}")

hibrit.to_excel(os.path.join(KLASOR, 'prophet_hibrit_sonuclari.xlsx'), index=False)
print(f"\nKaydedildi: prophet_hibrit_sonuclari.xlsx")
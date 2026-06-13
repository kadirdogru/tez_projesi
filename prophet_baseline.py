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
    print(f"PROPHET — {kategori.upper()}")
    
    veri = df[df['kategori'] == kategori].sort_values('hafta')
    
    # Prophet ds/y formatı
    prophet_df = veri[['hafta', 'yorum_sayisi']].rename(
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
    
    model.fit(train)
    
    future = model.make_future_dataframe(periods=TEST_HAFTA, freq='W')
    forecast = model.predict(future)
    
    tahmin = forecast.tail(TEST_HAFTA)['yhat'].values
    tahmin = np.maximum(tahmin, 0)  # negatif tahmin olmasın
    gercek = test['y'].values
    
    mape = mean_absolute_percentage_error(gercek, tahmin) * 100
    mae = np.mean(np.abs(gercek - tahmin))
    
    print(f"MAPE: {mape:.2f}%")
    print(f"MAE:  {mae:.2f}")
    
    sonuclar.append({
        'kategori': kategori,
        'model': 'Prophet',
        'mape': round(mape, 2),
        'mae': round(mae, 2)
    })

ozet = pd.DataFrame(sonuclar)
print(f"\n{'='*50}")
print("ÖZET")
print(ozet.to_string(index=False))

ozet.to_excel(os.path.join(KLASOR, 'prophet_sonuclari.xlsx'), index=False)
print(f"\nKaydedildi: prophet_sonuclari.xlsx")
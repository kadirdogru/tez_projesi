import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import grangercausalitytests, adfuller
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
from sklearn.metrics import mean_absolute_percentage_error
import warnings
import os
warnings.filterwarnings('ignore')

KLASOR = r'C:\Users\MONSTER\OneDrive\Desktop\tez_projesi'

# Yükle
platform_df = pd.read_excel(os.path.join(KLASOR, 'platform_haftalik_aggregate.xlsx'))
trends = pd.read_excel(os.path.join(KLASOR, 'google_trends_haftalik.xlsx'))

platform_df['hafta'] = pd.to_datetime(platform_df['hafta'])
trends['tarih'] = pd.to_datetime(trends['tarih'])

# Pazartesi normalize
trends['hafta'] = trends['tarih'] - pd.to_timedelta(trends['tarih'].dt.dayofweek, unit='D')
platform_df['hafta'] = platform_df['hafta'] - pd.to_timedelta(platform_df['hafta'].dt.dayofweek, unit='D')

KATEGORILER = ['klima', 'mont', 'sirt_cantasi', 'robot_supurge', 'parfum']
PLATFORMLAR = ['trendyol', 'hepsiburada', 'n11']
TEST_HAFTA = 20
MAX_LAG = 8

granger_sonuclar = []
model_sonuclar = []

for kategori in KATEGORILER:
    trends_veri = trends[trends['kategori'] == kategori][['hafta', 'trends_skoru']]
    
    for platform in PLATFORMLAR:
        print(f"\n{'='*50}")
        print(f"{kategori.upper()} — {platform.upper()}")
        
        veri = platform_df[
            (platform_df['kategori'] == kategori) &
            (platform_df['platform'] == platform)
        ].sort_values('hafta')
        
        # Trends ile birleştir
        veri = pd.merge(veri, trends_veri, on='hafta', how='inner')
        
        if len(veri) < 40:
            print(f"  ATLANDI: yeterli veri yok ({len(veri)} hafta)")
            continue
        
        print(f"  {len(veri)} hafta veri")
        
        y = veri['yorum_sayisi'].values.astype(float)
        t = veri['trends_skoru'].values.astype(float)

        # --- GRANGER ---
        def adf_duragan(seri):
            return adfuller(seri.dropna())[1] < 0.05
        
        y_g, t_g = y.copy(), t.copy()
        if not adf_duragan(pd.Series(y_g)):
            y_g = np.diff(y_g)
            t_g = np.diff(t_g)
        
        try:
            test = grangercausalitytests(
                pd.DataFrame({'y': y_g, 't': t_g}), maxlag=MAX_LAG, verbose=False
            )
            en_iyi_p = min(test[lag][0]['ssr_ftest'][1] for lag in range(1, MAX_LAG+1))
            en_iyi_lag = min(range(1, MAX_LAG+1), key=lambda l: test[l][0]['ssr_ftest'][1])
            anlamli = en_iyi_p < 0.05
            print(f"  Granger: p={en_iyi_p:.4f} lag={en_iyi_lag} {'ANLAMLı' if anlamli else 'ANLAMSIZ'}")
        except:
            en_iyi_p, en_iyi_lag, anlamli = 1.0, 0, False
        
        granger_sonuclar.append({
            'kategori': kategori, 'platform': platform,
            'en_iyi_lag': en_iyi_lag, 'p_degeri': round(en_iyi_p, 4), 'anlamli': anlamli
        })

        # --- PROPHET BASELINE vs HİBRİT ---
        train = veri.iloc[:-TEST_HAFTA]
        test_veri = veri.iloc[-TEST_HAFTA:]
        gercek = test_veri['yorum_sayisi'].values

        # Baseline
        try:
            m = Prophet(yearly_seasonality=True, weekly_seasonality=False,
                       daily_seasonality=False, seasonality_mode='multiplicative')
            m.fit(train[['hafta','yorum_sayisi']].rename(columns={'hafta':'ds','yorum_sayisi':'y'}))
            fc = m.predict(m.make_future_dataframe(periods=TEST_HAFTA, freq='W'))
            tahmin_b = np.maximum(fc.tail(TEST_HAFTA)['yhat'].values, 0)
            mape_b = mean_absolute_percentage_error(gercek, tahmin_b) * 100
        except:
            mape_b = np.nan

        # Hibrit
        try:
            m2 = Prophet(yearly_seasonality=True, weekly_seasonality=False,
                        daily_seasonality=False, seasonality_mode='multiplicative')
            m2.add_regressor('trends_skoru')
            train_p = train[['hafta','yorum_sayisi','trends_skoru']].rename(
                columns={'hafta':'ds','yorum_sayisi':'y'})
            m2.fit(train_p)
            future = test_veri[['hafta','trends_skoru']].rename(columns={'hafta':'ds'})
            fc2 = m2.predict(future)
            tahmin_h = np.maximum(fc2['yhat'].values, 0)
            mape_h = mean_absolute_percentage_error(gercek, tahmin_h) * 100
        except:
            mape_h = np.nan

        iyilesme = round(mape_b - mape_h, 2) if not np.isnan(mape_b) and not np.isnan(mape_h) else np.nan
        print(f"  Prophet Baseline: {mape_b:.2f}%  Hibrit: {mape_h:.2f}%  Fark: {iyilesme:+.2f}%")

        model_sonuclar.append({
            'kategori': kategori, 'platform': platform,
            'prophet_baseline_mape': round(mape_b, 2),
            'prophet_hibrit_mape': round(mape_h, 2),
            'iyilesme': iyilesme
        })

# Kaydet
granger_df = pd.DataFrame(granger_sonuclar)
model_df = pd.DataFrame(model_sonuclar)

granger_df.to_excel(os.path.join(KLASOR, 'platform_granger_sonuclari.xlsx'), index=False)
model_df.to_excel(os.path.join(KLASOR, 'platform_model_sonuclari.xlsx'), index=False)

print(f"\n{'='*60}")
print("GRANGER ÖZET")
print(granger_df.to_string(index=False))
print(f"\n{'='*60}")
print("MODEL ÖZET")
print(model_df.to_string(index=False))
print("\nKaydedildi: platform_granger_sonuclari.xlsx, platform_model_sonuclari.xlsx")
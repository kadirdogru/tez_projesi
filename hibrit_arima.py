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
TEST_HAFTA = 20

# Baseline ARIMA order'ları — önceki sonuçtan
ORDERS = {
    'klima': (1, 1, 2),
    'mont': (2, 0, 1),
    'sirt_cantasi': (1, 1, 3),
    'robot_supurge': (1, 1, 1),
    'parfum': (3, 1, 1)
}

sonuclar = []

for kategori in KATEGORILER:
    print(f"\n{'='*50}")
    print(f"HİBRİT ARIMA — {kategori.upper()}")
    
    veri = df[df['kategori'] == kategori].sort_values('hafta').reset_index(drop=True)
    
    y = veri['yorum_sayisi'].values.astype(float)
    trends = veri['trends_skoru'].values.astype(float)
    
    train_y = y[:-TEST_HAFTA]
    train_trends = trends[:-TEST_HAFTA]
    test_y = y[-TEST_HAFTA:]
    test_trends = trends[-TEST_HAFTA:]
    
    order = ORDERS[kategori]
    
    # ARIMAX — exog olarak Trends skoru eklendi
    try:
        model = ARIMA(train_y, exog=train_trends, order=order)
        fit = model.fit()
        tahmin = fit.forecast(steps=TEST_HAFTA, exog=test_trends)
        tahmin = np.maximum(tahmin, 0)
        
        mape = mean_absolute_percentage_error(test_y, tahmin) * 100
        mae = np.mean(np.abs(test_y - tahmin))
        
        print(f"MAPE: {mape:.2f}%")
        print(f"MAE:  {mae:.2f}")
        
        sonuclar.append({
            'kategori': kategori,
            'model': 'ARIMAX (Hibrit)',
            'mape': round(mape, 2),
            'mae': round(mae, 2)
        })
        
    except Exception as e:
        print(f"HATA: {e}")

# Baseline ile karşılaştır
baseline = pd.read_excel(os.path.join(KLASOR, 'arima_sonuclari.xlsx'))
hibrit = pd.DataFrame(sonuclar)

print(f"\n{'='*50}")
print("ARIMA vs ARIMAX (HİBRİT) KARŞILAŞTIRMA")
print(f"{'='*50}")

for kategori in KATEGORILER:
    b_mape = baseline[baseline['kategori'] == kategori]['mape'].values[0]
    h_mape = hibrit[hibrit['kategori'] == kategori]['mape'].values[0]
    fark = b_mape - h_mape
    yon = '✓ İYİLEŞTİ' if fark > 0 else '✗ KÖTÜLEŞTI'
    print(f"{kategori:15} Baseline: {b_mape:6.2f}%  Hibrit: {h_mape:6.2f}%  Fark: {fark:+.2f}% {yon}")

hibrit.to_excel(os.path.join(KLASOR, 'arimax_sonuclari.xlsx'), index=False)
print(f"\nKaydedildi: arimax_sonuclari.xlsx")
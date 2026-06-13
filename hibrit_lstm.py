import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_percentage_error
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import warnings
import os
warnings.filterwarnings('ignore')

KLASOR = r'C:\Users\MONSTER\OneDrive\Desktop\tez_projesi'
df = pd.read_excel(os.path.join(KLASOR, 'analiz_dataset.xlsx'))
df['hafta'] = pd.to_datetime(df['hafta'])

KATEGORILER = ['klima', 'mont', 'sirt_cantasi', 'robot_supurge', 'parfum']
TEST_HAFTA = 20
LOOKBACK = 12

def veri_hazirla(y_scaled, trends_scaled, lookback):
    X, y = [], []
    for i in range(lookback, len(y_scaled)):
        # Her adımda hem yorum hem trends penceresi
        pencere_y = y_scaled[i-lookback:i]
        pencere_t = trends_scaled[i-lookback:i]
        X.append(np.column_stack([pencere_y, pencere_t]))
        y.append(y_scaled[i])
    return np.array(X), np.array(y)

sonuclar = []

for kategori in KATEGORILER:
    print(f"\n{'='*50}")
    print(f"HİBRİT LSTM — {kategori.upper()}")
    
    veri = df[df['kategori'] == kategori].sort_values('hafta').reset_index(drop=True)
    
    y_raw = veri['yorum_sayisi'].values.astype(float).reshape(-1, 1)
    t_raw = veri['trends_skoru'].values.astype(float).reshape(-1, 1)
    
    # Ayrı scaler
    scaler_y = MinMaxScaler()
    scaler_t = MinMaxScaler()
    
    y_scaled = scaler_y.fit_transform(y_raw).flatten()
    t_scaled = scaler_t.fit_transform(t_raw).flatten()
    
    train_y = y_scaled[:-TEST_HAFTA]
    train_t = t_scaled[:-TEST_HAFTA]
    test_y_raw = y_raw[-TEST_HAFTA:].flatten()
    test_t = t_scaled[-TEST_HAFTA:]
    
    X_train, y_train = veri_hazirla(train_y, train_t, LOOKBACK)
    # (samples, lookback, 2 feature)
    
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(LOOKBACK, 2)),
        Dropout(0.2),
        LSTM(32),
        Dropout(0.2),
        Dense(1)
    ])
    
    model.compile(optimizer='adam', loss='mse')
    model.fit(X_train, y_train, epochs=100, batch_size=16, verbose=0, validation_split=0.1)
    
    # Tahmin — adım adım
    son_y = list(train_y[-LOOKBACK:])
    son_t = list(train_t[-LOOKBACK:])
    tahminler = []
    
    for i in range(TEST_HAFTA):
        pencere = np.column_stack([son_y[-LOOKBACK:], son_t[-LOOKBACK:]]).reshape(1, LOOKBACK, 2)
        tahmin = model.predict(pencere, verbose=0)[0][0]
        tahminler.append(tahmin)
        son_y.append(tahmin)
        # Gerçek Trends değerini kullan (test döneminde biliniyor)
        son_t.append(test_t[i])
    
    tahmin_gercek = scaler_y.inverse_transform(np.array(tahminler).reshape(-1, 1)).flatten()
    tahmin_gercek = np.maximum(tahmin_gercek, 0)
    
    mape = mean_absolute_percentage_error(test_y_raw, tahmin_gercek) * 100
    mae = np.mean(np.abs(test_y_raw - tahmin_gercek))
    
    print(f"MAPE: {mape:.2f}%")
    print(f"MAE:  {mae:.2f}")
    
    sonuclar.append({
        'kategori': kategori,
        'model': 'LSTM Hibrit',
        'mape': round(mape, 2),
        'mae': round(mae, 2)
    })

# Baseline ile karşılaştır
baseline = pd.read_excel(os.path.join(KLASOR, 'lstm_sonuclari.xlsx'))
hibrit = pd.DataFrame(sonuclar)

print(f"\n{'='*50}")
print("LSTM vs HİBRİT LSTM KARŞILAŞTIRMA")
print(f"{'='*50}")

for kategori in KATEGORILER:
    b_mape = baseline[baseline['kategori'] == kategori]['mape'].values[0]
    h_mape = hibrit[hibrit['kategori'] == kategori]['mape'].values[0]
    fark = b_mape - h_mape
    yon = '✓ İYİLEŞTİ' if fark > 0 else '✗ KÖTÜLEŞTI'
    print(f"{kategori:15} Baseline: {b_mape:6.2f}%  Hibrit: {h_mape:6.2f}%  Fark: {fark:+.2f}% {yon}")

hibrit.to_excel(os.path.join(KLASOR, 'lstm_hibrit_sonuclari.xlsx'), index=False)
print(f"\nKaydedildi: lstm_hibrit_sonuclari.xlsx")
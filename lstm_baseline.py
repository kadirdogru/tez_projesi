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
LOOKBACK = 12  # 12 haftalık pencere

def veri_hazirla(seri, lookback):
    X, y = [], []
    for i in range(lookback, len(seri)):
        X.append(seri[i-lookback:i])
        y.append(seri[i])
    return np.array(X), np.array(y)

sonuclar = []

for kategori in KATEGORILER:
    print(f"\n{'='*50}")
    print(f"LSTM — {kategori.upper()}")
    
    veri = df[df['kategori'] == kategori].sort_values('hafta')
    y_raw = veri['yorum_sayisi'].values.astype(float).reshape(-1, 1)
    
    # Normalize
    scaler = MinMaxScaler()
    y_scaled = scaler.fit_transform(y_raw)
    
    # Train/test split
    train_scaled = y_scaled[:-TEST_HAFTA]
    
    # Pencereli veri
    X_train, y_train = veri_hazirla(train_scaled.flatten(), LOOKBACK)
    X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
    
    # Model
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(LOOKBACK, 1)),
        Dropout(0.2),
        LSTM(32),
        Dropout(0.2),
        Dense(1)
    ])
    
    model.compile(optimizer='adam', loss='mse')
    
    model.fit(
        X_train, y_train,
        epochs=100,
        batch_size=16,
        verbose=0,
        validation_split=0.1
    )
    
    # Tahmin — adım adım ilerle
    son_pencere = train_scaled[-LOOKBACK:].flatten().tolist()
    tahminler = []
    
    for _ in range(TEST_HAFTA):
        pencere = np.array(son_pencere[-LOOKBACK:]).reshape(1, LOOKBACK, 1)
        tahmin = model.predict(pencere, verbose=0)[0][0]
        tahminler.append(tahmin)
        son_pencere.append(tahmin)
    
    # Ters normalize
    tahmin_gercek = scaler.inverse_transform(np.array(tahminler).reshape(-1, 1)).flatten()
    tahmin_gercek = np.maximum(tahmin_gercek, 0)
    gercek = y_raw[-TEST_HAFTA:].flatten()
    
    mape = mean_absolute_percentage_error(gercek, tahmin_gercek) * 100
    mae = np.mean(np.abs(gercek - tahmin_gercek))
    
    print(f"MAPE: {mape:.2f}%")
    print(f"MAE:  {mae:.2f}")
    
    sonuclar.append({
        'kategori': kategori,
        'model': 'LSTM',
        'mape': round(mape, 2),
        'mae': round(mae, 2)
    })

ozet = pd.DataFrame(sonuclar)
print(f"\n{'='*50}")
print("ÖZET")
print(ozet.to_string(index=False))

ozet.to_excel(os.path.join(KLASOR, 'lstm_sonuclari.xlsx'), index=False)
print(f"\nKaydedildi: lstm_sonuclari.xlsx")
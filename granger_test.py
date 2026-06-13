import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import grangercausalitytests
from statsmodels.tsa.stattools import adfuller
import os
import warnings
warnings.filterwarnings('ignore')

KLASOR = r'C:\Users\MONSTER\OneDrive\Desktop\tez_projesi'
df = pd.read_excel(os.path.join(KLASOR, 'analiz_dataset.xlsx'))
df['hafta'] = pd.to_datetime(df['hafta'])

KATEGORILER = ['klima', 'mont', 'sirt_cantasi', 'robot_supurge', 'parfum']
MAX_LAG = 8  # 8 haftaya kadar gecikme test edilecek

def adf_test(seri, isim):
    sonuc = adfuller(seri.dropna())
    duragan = sonuc[1] < 0.05
    print(f"  ADF {isim}: p={sonuc[1]:.4f} → {'DURAĞAN ✓' if duragan else 'DURAĞAN DEĞİL — fark alınacak'}")
    return duragan

print("=" * 60)
print("GRANGER NEDENSELLİK TESTİ")
print("H0: Trends skoru, yorum sayısını Granger-öncülemez")
print("p < 0.05 → H0 reddedilir → Trends öncüdür")
print("=" * 60)

sonuclar = []

for kategori in KATEGORILER:
    print(f"\n{'='*60}")
    print(f"KATEGORİ: {kategori.upper()}")
    
    veri = df[df['kategori'] == kategori].sort_values('hafta').copy()
    
    yorum = veri['yorum_sayisi'].values.astype(float)
    trends = veri['trends_skoru'].values.astype(float)
    
    # Durağanlık kontrolü
    print("Durağanlık (ADF):")
    yorum_duragan = adf_test(pd.Series(yorum), 'yorum_sayisi')
    trends_duragan = adf_test(pd.Series(trends), 'trends_skoru')
    
    # Durağan değilse fark al
    if not yorum_duragan:
        yorum = np.diff(yorum)
        trends = np.diff(trends)
        print("  → Her iki seri farklandırıldı (d=1)")
    
    # Granger testi
    data = pd.DataFrame({'yorum': yorum, 'trends': trends})
    
    print(f"Granger testi (lag 1-{MAX_LAG}):")
    try:
        test_sonuc = grangercausalitytests(data[['yorum', 'trends']], maxlag=MAX_LAG, verbose=False)
        
        en_iyi_lag = None
        en_iyi_p = 1.0
        
        for lag in range(1, MAX_LAG + 1):
            p_val = test_sonuc[lag][0]['ssr_ftest'][1]
            isaretci = '✓ ANLAMLı' if p_val < 0.05 else ''
            print(f"  Lag {lag}: p = {p_val:.4f} {isaretci}")
            
            if p_val < en_iyi_p:
                en_iyi_p = p_val
                en_iyi_lag = lag
        
        sonuclar.append({
            'kategori': kategori,
            'en_iyi_lag': en_iyi_lag,
            'en_iyi_p': round(en_iyi_p, 4),
            'anlamli': en_iyi_p < 0.05
        })
        
    except Exception as e:
        print(f"  HATA: {e}")

# Özet tablo
print(f"\n{'='*60}")
print("ÖZET")
print(f"{'='*60}")
ozet = pd.DataFrame(sonuclar)
print(ozet.to_string(index=False))

ozet.to_excel(os.path.join(KLASOR, 'granger_sonuclari.xlsx'), index=False)
print(f"\nKaydedildi: granger_sonuclari.xlsx")
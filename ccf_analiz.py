import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import ccf
import os

KLASOR = r'C:\Users\MONSTER\OneDrive\Desktop\tez_projesi'
df = pd.read_excel(os.path.join(KLASOR, 'analiz_dataset.xlsx'))
df['hafta'] = pd.to_datetime(df['hafta'])

KATEGORILER = ['klima', 'mont', 'sirt_cantasi', 'robot_supurge', 'parfum']
KAT_LABELS = ['Klima', 'Mont', 'Sırt Çantası', 'Robot Süpürge', 'Parfüm']
MAX_LAG = 12

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle('CCF Analizi — Trends → Yorum Yoğunluğu Çapraz Korelasyonu\n(pozitif lag = Trends öncü)',
             fontsize=13, fontweight='bold')
axes = axes.flatten()

sonuclar = []

for i, (kategori, label) in enumerate(zip(KATEGORILER, KAT_LABELS)):
    ax = axes[i]

    veri = df[df['kategori'] == kategori].sort_values('hafta')

    trends = (veri['trends_skoru'] - veri['trends_skoru'].mean()) / veri['trends_skoru'].std()
    yorumlar = (veri['yorum_sayisi'] - veri['yorum_sayisi'].mean()) / veri['yorum_sayisi'].std()

    # CCF — nlags=12 → 12 eleman döner (lag 1'den 12'ye)
    ccf_degerler = ccf(yorumlar.values, trends.values, nlags=MAX_LAG, alpha=None)
    lags = np.arange(1, MAX_LAG + 1)  # 12 eleman

    n = len(veri)
    guven = 1.96 / np.sqrt(n)

    renkler = ['tomato' if abs(c) > guven else 'steelblue' for c in ccf_degerler]

    ax.bar(lags, ccf_degerler, color=renkler, edgecolor='white', alpha=0.85)
    ax.axhline(y=guven, color='red', linestyle='--', linewidth=1, alpha=0.7, label=f'%95 GA (±{guven:.2f})')
    ax.axhline(y=-guven, color='red', linestyle='--', linewidth=1, alpha=0.7)
    ax.axhline(y=0, color='black', linewidth=0.8)

    en_guclu_lag = int(np.argmax(np.abs(ccf_degerler))) + 1
    en_guclu_ccf = ccf_degerler[en_guclu_lag - 1]

    ax.set_title(f'{label}\n(En güçlü: Lag {en_guclu_lag}, r={en_guclu_ccf:.3f})', fontweight='bold')
    ax.set_xlabel('Lag (hafta)')
    ax.set_ylabel('Korelasyon')
    ax.set_xticks(lags)
    ax.set_ylim(-1, 1)
    ax.legend(fontsize=8)
    ax.grid(axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    sonuclar.append({
        'kategori': kategori,
        'en_guclu_lag': en_guclu_lag,
        'en_guclu_ccf': round(float(en_guclu_ccf), 3),
        'guven_esigi': round(guven, 3)
    })

    print(f"{label}: En güçlü lag={en_guclu_lag}, r={en_guclu_ccf:.3f}, güven eşiği=±{guven:.3f}")

axes[5].set_visible(False)

plt.tight_layout()
cikti = os.path.join(KLASOR, 'ccf_analiz.png')
plt.savefig(cikti, dpi=150, bbox_inches='tight')
print(f"\nKaydedildi: {cikti}")
plt.show()

ozet = pd.DataFrame(sonuclar)
print("\n=== CCF ÖZET ===")
print(ozet.to_string(index=False))
ozet.to_excel(os.path.join(KLASOR, 'ccf_sonuclari.xlsx'), index=False)
print("Kaydedildi: ccf_sonuclari.xlsx")
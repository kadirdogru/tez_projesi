import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

KLASOR = r'C:\Users\MONSTER\OneDrive\Desktop\tez_projesi'
df = pd.read_excel(os.path.join(KLASOR, 'analiz_dataset.xlsx'))
df['hafta'] = pd.to_datetime(df['hafta'])

KATEGORILER = ['klima', 'mont', 'sirt_cantasi', 'robot_supurge', 'parfum']
LAGLAR = [1, 2, 3, 4]

sonuclar = []

for kategori in KATEGORILER:
    veri = df[df['kategori'] == kategori].sort_values('hafta').reset_index(drop=True)
    
    for lag in LAGLAR:
        # Trends bu hafta arttı mı?
        trends_yon = np.sign(veri['trends_skoru'].diff())
        # lag hafta sonra yorum arttı mı?
        yorum_yon = np.sign(veri['yorum_sayisi'].diff().shift(-lag))
        
        # İkisi de aynı yönde mi?
        tutarli = (trends_yon == yorum_yon)
        
        # Sıfır değişimleri çıkar
        maske = (trends_yon != 0) & (yorum_yon != 0)
        tutarlilik = tutarli[maske].mean() * 100
        n = maske.sum()
        
        sonuclar.append({
            'kategori': kategori,
            'lag': lag,
            'tutarlilik_pct': round(tutarlilik, 1),
            'n': n
        })
        
        print(f"{kategori:15} Lag {lag}: %{tutarlilik:.1f} tutarlı ({n} gözlem)")

# Pivot tablo
ozet = pd.DataFrame(sonuclar)
pivot = ozet.pivot(index='kategori', columns='lag', values='tutarlilik_pct')
pivot.columns = [f'Lag {c} hafta' for c in pivot.columns]

print("\n=== YÖN TUTARLILIĞI TABLOSU ===")
print(pivot.to_string())

# Görsel
fig, ax = plt.subplots(figsize=(10, 6))

renkler = ['#2196F3', '#4CAF50', '#FF9800', '#E91E63']
x = np.arange(len(KATEGORILER))
width = 0.2

for i, lag in enumerate(LAGLAR):
    degerler = [ozet[(ozet['kategori']==k) & (ozet['lag']==lag)]['tutarlilik_pct'].values[0] 
                for k in KATEGORILER]
    bars = ax.bar(x + i*width, degerler, width, label=f'Lag {lag} hafta', color=renkler[i], alpha=0.85)

# %50 referans çizgisi (rastlantısal)
ax.axhline(y=50, color='red', linestyle='--', linewidth=1.5, label='%50 (rastlantısal)')

ax.set_xlabel('Kategori')
ax.set_ylabel('Yön Tutarlılığı (%)')
ax.set_title('Trends Artışı → Yorum Artışı Yön Tutarlılığı\n(>%50 = Trends yönü anlamlı)', fontweight='bold')
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels([k.replace('_', '\n') for k in KATEGORILER])
ax.set_ylim(0, 100)
ax.legend()
ax.grid(axis='y', alpha=0.3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
cikti = os.path.join(KLASOR, 'yon_tutarliligi.png')
plt.savefig(cikti, dpi=150, bbox_inches='tight')
print(f"\nKaydedildi: {cikti}")
plt.show()

ozet.to_excel(os.path.join(KLASOR, 'yon_tutarliligi_sonuclari.xlsx'), index=False)
print("Kaydedildi: yon_tutarliligi_sonuclari.xlsx")
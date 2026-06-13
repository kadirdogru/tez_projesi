import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

KLASOR = r'C:\Users\MONSTER\OneDrive\Desktop\tez_projesi'

# Tüm sonuçları yükle
arima = pd.read_excel(os.path.join(KLASOR, 'arima_sonuclari.xlsx'))
arimax = pd.read_excel(os.path.join(KLASOR, 'arimax_sonuclari.xlsx'))
prophet = pd.read_excel(os.path.join(KLASOR, 'prophet_sonuclari.xlsx'))
prophet_h = pd.read_excel(os.path.join(KLASOR, 'prophet_hibrit_sonuclari.xlsx'))
lstm = pd.read_excel(os.path.join(KLASOR, 'lstm_sonuclari.xlsx'))
lstm_h = pd.read_excel(os.path.join(KLASOR, 'lstm_hibrit_sonuclari.xlsx'))

KATEGORILER = ['klima', 'mont', 'sirt_cantasi', 'robot_supurge', 'parfum']
LABELS = ['Klima', 'Mont', 'Sırt\nÇantası', 'Robot\nSüpürge', 'Parfüm']

def mape_al(df, kategori):
    return df[df['kategori'] == kategori]['mape'].values[0]

# Veriyi derle
data = {
    'ARIMA': [mape_al(arima, k) for k in KATEGORILER],
    'ARIMAX\n(Hibrit)': [mape_al(arimax, k) for k in KATEGORILER],
    'Prophet': [mape_al(prophet, k) for k in KATEGORILER],
    'Prophet\nHibrit': [mape_al(prophet_h, k) for k in KATEGORILER],
    'LSTM': [mape_al(lstm, k) for k in KATEGORILER],
    'LSTM\nHibrit': [mape_al(lstm_h, k) for k in KATEGORILER],
}

fig, axes = plt.subplots(1, 5, figsize=(18, 6), sharey=False)
fig.suptitle('Model Karşılaştırması — MAPE % (düşük = iyi)', fontsize=13, fontweight='bold', y=1.02)

RENKLER = ['#5B9BD5', '#2E75B6', '#70AD47', '#375623', '#FF7043', '#BF360C']

for i, (kategori, label) in enumerate(zip(KATEGORILER, LABELS)):
    ax = axes[i]
    modeller = list(data.keys())
    degerler = [data[m][i] for m in modeller]
    
    bars = ax.bar(range(len(modeller)), degerler, color=RENKLER, width=0.6, edgecolor='white')
    
    # En iyi modeli vurgula
    en_iyi = np.argmin(degerler)
    bars[en_iyi].set_edgecolor('gold')
    bars[en_iyi].set_linewidth(2.5)
    
    # Değerleri bar üstüne yaz
    for j, (bar, val) in enumerate(zip(bars, degerler)):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{val:.0f}%', ha='center', va='bottom', fontsize=7, fontweight='bold')
    
    ax.set_title(label, fontweight='bold', fontsize=11)
    ax.set_xticks(range(len(modeller)))
    ax.set_xticklabels(modeller, fontsize=7)
    ax.set_ylabel('MAPE %' if i == 0 else '')
    ax.grid(axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# Legend
patches = [mpatches.Patch(color=RENKLER[i], label=list(data.keys())[i]) for i in range(len(data))]
fig.legend(handles=patches, loc='lower center', ncol=6, fontsize=9,
           bbox_to_anchor=(0.5, -0.08), frameon=False)

plt.tight_layout()
cikti = os.path.join(KLASOR, 'ozet_model_karsilastirma.png')
plt.savefig(cikti, dpi=150, bbox_inches='tight')
print(f"Kaydedildi: {cikti}")
plt.show()
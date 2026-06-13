import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

KLASOR = r'C:\Users\MONSTER\OneDrive\Desktop\tez_projesi'

granger = pd.read_excel(os.path.join(KLASOR, 'platform_granger_sonuclari.xlsx'))
model = pd.read_excel(os.path.join(KLASOR, 'platform_model_sonuclari.xlsx'))

KATEGORILER = ['klima', 'mont', 'sirt_cantasi', 'robot_supurge', 'parfum']
PLATFORMLAR = ['trendyol', 'hepsiburada', 'n11']
PLATFORM_RENKLER = {'trendyol': '#F27A1A', 'hepsiburada': '#FF6B35', 'n11': '#4A90D9'}
KAT_LABELS = ['Klima', 'Mont', 'Sırt\nÇantası', 'Robot\nSüpürge', 'Parfüm']

fig, axes = plt.subplots(2, 1, figsize=(16, 12))
fig.suptitle('Platform Bazlı Analiz Sonuçları', fontsize=14, fontweight='bold')

# --- GRAFİK 1: Granger p-değerleri ---
ax1 = axes[0]
ax1.set_title('Granger Nedensellik — p-değerleri (< 0.05 = ANLAMLı)', fontweight='bold')

x = np.arange(len(KATEGORILER))
width = 0.25

for i, platform in enumerate(PLATFORMLAR):
    p_vals = []
    for kat in KATEGORILER:
        row = granger[(granger['kategori'] == kat) & (granger['platform'] == platform)]
        p_vals.append(row['p_degeri'].values[0] if len(row) > 0 else 1.0)
    
    bars = ax1.bar(x + i*width, p_vals, width, label=platform.capitalize(),
                   color=PLATFORM_RENKLER[platform], alpha=0.85, edgecolor='white')
    
    for bar, pv in zip(bars, p_vals):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                f'{pv:.3f}', ha='center', va='bottom', fontsize=7)

ax1.axhline(y=0.05, color='red', linestyle='--', linewidth=1.5, label='p=0.05 eşiği')
ax1.set_xticks(x + width)
ax1.set_xticklabels(KAT_LABELS)
ax1.set_ylabel('p-değeri')
ax1.set_ylim(0, 0.6)
ax1.legend()
ax1.grid(axis='y', alpha=0.3)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

# --- GRAFİK 2: Model iyileşme (Prophet Baseline → Hibrit) ---
ax2 = axes[1]
ax2.set_title('Prophet Hibrit İyileşmesi — MAPE Farkı % (+ = iyileşti)', fontweight='bold')

for i, platform in enumerate(PLATFORMLAR):
    iyilesme = []
    for kat in KATEGORILER:
        row = model[(model['kategori'] == kat) & (model['platform'] == platform)]
        iyilesme.append(row['iyilesme'].values[0] if len(row) > 0 else 0)
    
    bars = ax2.bar(x + i*width, iyilesme, width, label=platform.capitalize(),
                   color=PLATFORM_RENKLER[platform], alpha=0.85, edgecolor='white')
    
    for bar, val in zip(bars, iyilesme):
        ypos = bar.get_height() + 0.5 if val >= 0 else bar.get_height() - 3
        ax2.text(bar.get_x() + bar.get_width()/2, ypos,
                f'{val:+.1f}', ha='center', va='bottom', fontsize=7)

ax2.axhline(y=0, color='black', linewidth=1)
ax2.set_xticks(x + width)
ax2.set_xticklabels(KAT_LABELS)
ax2.set_ylabel('MAPE Farkı %')
ax2.legend()
ax2.grid(axis='y', alpha=0.3)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

plt.tight_layout()
cikti = os.path.join(KLASOR, 'platform_analiz_grafik.png')
plt.savefig(cikti, dpi=150, bbox_inches='tight')
print(f"Kaydedildi: {cikti}")
plt.show()
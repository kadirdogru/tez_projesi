import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

KLASOR = r'C:\Users\MONSTER\OneDrive\Desktop\tez_projesi'
df = pd.read_excel(os.path.join(KLASOR, 'analiz_dataset.xlsx'))
df['hafta'] = pd.to_datetime(df['hafta'])

KATEGORILER = ['klima', 'mont', 'sirt_cantasi', 'robot_supurge', 'parfum']

fig, axes = plt.subplots(5, 1, figsize=(14, 20))
fig.suptitle('Google Trends vs Haftalık Yorum Yoğunluğu', fontsize=14, fontweight='bold', y=1.01)

for i, kategori in enumerate(KATEGORILER):
    ax1 = axes[i]
    ax2 = ax1.twinx()
    
    veri = df[df['kategori'] == kategori].sort_values('hafta')
    
    ax1.fill_between(veri['hafta'], veri['yorum_sayisi'], alpha=0.3, color='steelblue')
    ax1.plot(veri['hafta'], veri['yorum_sayisi'], color='steelblue', linewidth=1.5, label='Yorum Sayısı')
    
    ax2.plot(veri['hafta'], veri['trends_skoru'], color='tomato', linewidth=1.5, linestyle='--', label='Trends Skoru')
    
    ax1.set_ylabel('Yorum Sayısı', color='steelblue', fontsize=9)
    ax2.set_ylabel('Trends Skoru', color='tomato', fontsize=9)
    ax1.set_title(kategori.replace('_', ' ').title(), fontweight='bold')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=8)

plt.tight_layout()
cikti = os.path.join(KLASOR, 'eda_grafik.png')
plt.savefig(cikti, dpi=150, bbox_inches='tight')
print(f"Kaydedildi: {cikti}")
plt.show()
"""
Birleştirme Scripti
- Her kategori için ayrı xlsx (klima_master.xlsx, mont_master.xlsx, ...)
- Tüm kategorileri içeren master_dataset.xlsx
"""

import pandas as pd
import glob
import os

# Tüm xlsx dosyalarını bul (master dosyaları hariç)
dosyalar = [f for f in glob.glob('*.xlsx') if 'master' not in f.lower()]
print(f"📂 {len(dosyalar)} dosya bulundu\n")

df_liste = []
hatalar = []

for dosya in sorted(dosyalar):
    try:
        df = pd.read_excel(dosya, engine='openpyxl')
        df_liste.append(df)
        print(f"✅ {dosya} — {len(df)} satır")
    except Exception as e:
        print(f"❌ {dosya} — HATA: {e}")
        hatalar.append(dosya)

if not df_liste:
    print("⚠️  Hiç dosya yüklenemedi!")
    exit()

# Hepsini birleştir
master = pd.concat(df_liste, ignore_index=True)

print(f"\n{'='*60}")
print(f"📊 TOPLAM: {len(master)} yorum")
print(f"\n🏪 Platform dağılımı:")
for platform, sayi in master['platform'].value_counts().items():
    print(f"   {platform}: {sayi}")
print(f"\n📁 Kategori dağılımı:")
for kategori, sayi in master['kategori'].value_counts().items():
    print(f"   {kategori}: {sayi}")
print(f"\n⭐ Yıldız dağılımı: {dict(master['yildiz'].value_counts().sort_index())}")
print(f"📅 Tarih aralığı: {master['tarih'].min()} → {master['tarih'].max()}")
print(f"{'='*60}\n")

# 1. Kategori bazlı dosyalar
kategoriler = master['kategori'].unique()
for kategori in sorted(kategoriler):
    df_kat = master[master['kategori'] == kategori].copy()
    dosya_adi = f"{kategori}_master.xlsx"
    df_kat.to_excel(dosya_adi, index=False, engine='openpyxl')
    print(f"💾 {dosya_adi} — {len(df_kat)} yorum")
    # Platform bazlı özet
    for platform, sayi in df_kat['platform'].value_counts().items():
        print(f"   └─ {platform}: {sayi}")

# 2. Master dataset
master.to_excel('master_dataset.xlsx', index=False, engine='openpyxl')
print(f"\n💾 master_dataset.xlsx — {len(master)} yorum (tümü)")

if hatalar:
    print(f"\n⚠️  Yüklenemeyen dosyalar: {hatalar}")

print("\n✅ Birleştirme tamamlandı!")

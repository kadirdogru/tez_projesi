# 📈 Google Trends Verisiyle E-Ticaret Yorum Sayısı Tahmini

> **🎓 Lisans / Yüksek Lisans Tez Projesi** > *E-ticaret platformlarındaki ürün yorumları, Google Trends arama verileriyle tahmin edilebilir mi?*

---

## 🎯 Projenin Amacı

Bu proje, **Google Trends** üzerindeki arama ilgisinin Türkiye'deki büyük e-ticaret platformlarında (Trendyol, N11, Hepsiburada) yapılan **ürün yorumlarını önceden tahmin edip edemeyeceğini** araştırmaktadır.

**💡 Temel Fikir:** Bir ürüne yönelik internet araması arttığında, kısa süre sonra o ürünün satın alma ve dolayısıyla yorumlanma oranlarında öngörülebilir bir artış yaşanıyor mu?

---

## ❓ Araştırma Sorusu

> *"Google Trends arama verisi, e-ticaret platformlarındaki haftalık yorum sayılarını istatistiksel olarak önceleyen (Granger-cause eden) bir sinyal olarak kullanılabilir mi? Bu sinyalin tahmin modellerine eklenmesi, model performansını artırır mı?"*

---

## 📦 İncelenen Ürün Kategorileri

Farklı tüketici davranışlarını gözlemleyebilmek adına çeşitli kategoriler ve popüler markalar seçilmiştir:

| Kategori | Örnek Marka / Ürünler |
| :--- | :--- |
| ❄️ **Klima** | Airfel, Arçelik, Baymak, Samsung, Bosch |
| 🧥 **Mont** | Mavi, Bershka, Bianco Lucci, Çeşitli Markalar |
| 🎒 **Sırt Çantası** | Nike, Puma, Hummel, Relaxion |
| 🤖 **Robot Süpürge** | Roborock, Xiaomi, Dreame, Philips |
| ✨ **Parfüm** | Calvin Klein, Avon, Bargello, Versace, Burberry |

---

## 🛠 Veri Toplama Süreci

Projenin veri seti iki ana ayaktan oluşmaktadır:

### 1. E-Ticaret Yorumları (Web Scraping)
Türkiye'nin en büyük üç e-ticaret platformundan otomatik veri çekme (scraping) işlemi gerçekleştirilmiştir. Toplanan veriler; platform, kategori, ürün adı, kullanıcı bilgisi, tarih, yıldız puanı ve yorum metnini içerir.
* 🟠 **Trendyol** (`trendyol_scraper.py`)
* 🔴 **N11** (`n11_scraper.py`)
* 🟠 **Hepsiburada** (`hepsiburada_scraper.py`)

### 2. Google Trends Verisi
`pytrends` kütüphanesi kullanılarak, belirlenen ürün/marka anahtar kelimeleri için Türkiye lokasyonlu haftalık arama ilgisi (0–100 arası skor) çekilmiştir. 
* 📅 **Kapsanan Dönem:** Haziran 2023 – Mayıs 2026

---

## ⚙️ Analiz Boru Hattı (Pipeline)

```text
Ham Yorum Verileri
       ↓
 1. birlestir.py            → Tüm platformları tek dosyada birleştirir
       ↓
 2. haftalik_aggregate.py   → Yorumları haftalık periyotlarda toplar
       ↓
 3. birlestir_analiz.py     → Yorum verisini Google Trends verisiyle birleştirir
       ↓
 4. eda_grafik.py           → Keşifsel Veri Analizi (EDA) ve görselleştirme
       ↓
 5. ccf_analiz.py           → Çapraz Korelasyon (En güçlü zaman gecikmesinin tespiti)
       ↓
 6. granger_test.py         → Granger Nedensellik Testi
       ↓
 7. Tahmin Modelleri        → 6 farklı zaman serisi modelinin eğitimi ve kıyası
```

---

## 🧠 Kullanılan Modeller

Projede **3 temel (baseline) model** ve bu modellerin **Google Trends verisiyle güçlendirilmiş hibrit (çok değişkenli) versiyonları** karşılaştırılmıştır. 

*(Modeller son 20 haftalık test seti üzerinde **MAPE** ve **MAE** metrikleriyle değerlendirilmiştir.)*

| Model Tipi | Model Adı | Açıklama | Kaynak Dosya |
| :--- | :--- | :--- | :--- |
| **Temel Modeller** | 📉 **ARIMA** | Klasik istatistiksel zaman serisi | `arima_baseline.py` |
| | 🧠 **LSTM** | Derin öğrenme tabanlı ağ (Sadece geçmiş yorum) | `lstm_baseline.py` |
| | 🔮 **Prophet** | Meta (Facebook) tabanlı tahmin modeli | `prophet_baseline.py` |
| **Hibrit Modeller** | 📈 **Hibrit ARIMA (ARIMAX)** | ARIMA + Trends Sinyali | `hibrit_arima.py` |
| | 🌐 **Hibrit LSTM** | LSTM + Trends Sinyali | `hibrit_lstm.py` |
| | 🚀 **Hibrit Prophet** | Prophet + Trends Sinyali | `hibrit_prophet.py` |

---

## 📊 İstatistiksel Testler

* 🔍 **Granger Nedensellik Testi:** Google Trends skorunun, yorum sayısını istatistiksel olarak *önceden* haber verip vermediğini (H₀ reddi) sınar.
* ⏱️ **Çapraz Korelasyon Analizi (CCF):** Arama hacmindeki artışın, yorumlara yansıması arasındaki zaman gecikmesini (lag) ölçer.
* 📏 **ADF Durağanlık Testi:** Zaman serilerinin modellemeye ve testlere uygunluğunu (durağanlığını) kontrol eder.

---

## 📂 Proje Dosya Yapısı

```text
tez_projesi/
├── Veri Toplama/
│   ├── trendyol_scraper.py
│   ├── n11_scraper.py
│   └── hepsiburada_scraper.py
│
├── Veri Hazırlama/
│   ├── birlestir.py
│   ├── haftalik_aggregate.py
│   ├── birlestir_analiz.py
│   ├── google_trends_cek.py
│   └── platform_bazli_aggregate.py
│
├── Analiz/
│   ├── eda_grafik.py
│   ├── ccf_analiz.py
│   ├── granger_test.py
│   ├── platform_bazli_analiz.py
│   └── yon_tutarliligi.py
│
├── Tahmin Modelleri/
│   ├── arima_baseline.py
│   ├── lstm_baseline.py
│   ├── prophet_baseline.py
│   ├── hibrit_arima.py
│   ├── hibrit_lstm.py
│   └── hibrit_prophet.py
│
├── Çıktı Dosyaları/
│   ├── analiz_dataset.xlsx
│   ├── master_dataset.xlsx
│   └── [Model & Test Sonuçları .xlsx dosyaları]
│
└── Grafikler/
    ├── eda_grafik.png
    ├── ccf_analiz.png
    └── ozet_model_karsilastirma.png
```

---

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
Projenin çalışması için bilgisayarınızda **Python 3.9 veya üzeri** bir sürüm kurulu olmalıdır. Gerekli kütüphaneleri yüklemek için:

```bash
pip install pandas numpy matplotlib statsmodels scikit-learn tensorflow prophet pytrends openpyxl scrapling
```

### Adım Adım Çalıştırma
Aşağıdaki adımları sırasıyla terminalinizde (veya komut satırında) çalıştırarak projeyi baştan sona simüle edebilirsiniz:

```bash
# 1. Yorumları Topla
python trendyol_scraper.py
python n11_scraper.py
python hepsiburada_scraper.py

# 2. Verileri Hazırla
python birlestir.py
python haftalik_aggregate.py
python google_trends_cek.py
python birlestir_analiz.py

# 3. Analizleri Gerçekleştir
python granger_test.py
python ccf_analiz.py

# 4. Modelleri Eğit ve Kıyasla
python arima_baseline.py
python lstm_baseline.py
python prophet_baseline.py
python hibrit_arima.py
python hibrit_lstm.py
python hibrit_prophet.py
```

> ⚠️ **Not:** Web scraping (veri kazıma) adımları, internet bağlantınıza ve hedef sitelerin yanıt sürelerine göre değişiklik gösterebilir. Engellenmeleri (ban) önlemek adına kod içerisine bekleme (sleep) süreleri eklenmiştir.

---

## 💻 Teknolojiler ve Kütüphaneler

| Alan | Kullanılan Araç / Kütüphane |
| :--- | :--- |
| **Veri İşleme & Manipülasyon** | `pandas`, `numpy` |
| **Veri Kazıma (Web Scraping)** | `scrapling`, `beautifulsoup4` |
| **Arama Motoru Verisi** | `pytrends` |
| **Zaman Serisi Tahmini (ML/DL)**| `prophet`, `scikit-learn`, `tensorflow` / `keras` |
| **İstatistiksel Analizler** | `statsmodels` |
| **Görselleştirme & Çıktı** | `matplotlib`, `openpyxl` |

---

---

## 🏆 Proje Sonuçları ve Bulgular

Analiz ve modelleme aşamaları sonucunda elde edilen temel bulgular şunlardır:

* 🔍 **Granger Nedensellik Testi:** Google Trends verilerinin, e-ticaret yorum sayıları için istatistiksel olarak anlamlı bir öncü sinyal (zaman gecikmesi/lag) barındırdığı tespit edilmiştir (p < 0.05).
* 📈 **Model Performansı:** Sadece geçmiş yorum verisiyle eğitilen temel modellere kıyasla, Google Trends sinyaliyle desteklenen **Hibrit modeller (ör. Hibrit LSTM ve ARIMAX)**, MAPE ve MAE metriklerinde daha düşük hata payı sunmuştur.
* 🛒 **Kategori Etkisi:** Arama hacmi ile yorum sayısı arasındaki tahmin edici ilişki, özellikle araştırmaya daha fazla ihtiyaç duyulan ve mevsimsellik gösteren kategorilerde (ör. Klima, Robot Süpürge) çok daha belirgin şekilde gözlemlenmiştir.

*(Detaylı sonuç raporlarına ve performans karşılaştırmalarına `Çıktı Dosyaları/` dizininden ulaşabilirsiniz.)*

---

## 👨‍💻 Geliştirici

**Kadir Doğru** ✉️ [kadirdogru.ai@gmail.com](mailto:kadirdogru.ai@gmail.com)

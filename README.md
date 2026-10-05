# Stockify - Akıllı Envanter ve Satış Takip Sistemi

Stockify, Python tabanlı ve masaüstü mimarisine sahip modern bir envanter yönetim, satış takip ve iş analitiği yazılımıdır. Proje, veri güvenliği (kriptografi), yapay zeka destekli talep tahmini ve rol tabanlı yetkilendirme (RBAC) mekanizmalarıyla güçlendirilerek akademik standartlara (bitirme tezi/mezuniyet projesi) uygun olarak tasarlanmıştır.

---

## 🚀 Öne Çıkan Akademik ve Teknik Özellikler

### 1. 🔐 SHA-256 Kriptografik Parola Güvenliği (Kullanıcı Giriş & Yetkilendirme)
Sistemde düz metin (plain text) olarak parola saklanması güvenlik açığı oluşturacağından, **Secure Hash Algorithm 256-bit (SHA-256)** şifreleme altyapısı kullanılmıştır:
* **Çalışma Biçimi:** Parolalar veri tabanına (`users` tablosu) kaydedilmeden önce tek yönlü kriptografik hash fonksiyonu olan SHA-256 algoritmasından geçirilir. 
* **Doğrulama:** Giriş esnasında girilen parola yeniden hash'lenir ve veri tabanındaki değerle karşılaştırılır. Bu sayede veri tabanı ele geçirilse dahi kullanıcı şifreleri asla deşifre edilemez.
* **Rol Tabanlı Erişim Kontrolü (RBAC):**
  * **Yönetici (`admin` / `admin123`):** Ürün envanterini güncelleme, silme, ekleme, tüm finansal raporları görme ve CSV olarak aktarma yetkilerine sahiptir.
  * **Kasiyer (`kasiyer` / `kasiyer123`):** Satış kaydetme yetkisine sahiptir. Finansal veri içeren "Raporlar" sekmesi kilitlenmiştir. Ürün fiyatlarını veya envanteri değiştiremez (form alanları ve butonlar kilitlenir).

### 🤖 2. Yapay Zeka ve Matematiksel Talep Tahmin Motoru (Demand Forecasting)
Envanter kontrolünde stoksuz kalma durumunu (stockout) önlemek için veri bilimi temelli bir doğrusal tahmin motoru entegre edilmiştir. 
* **Matematiksel Model:**
  * Her bir ürün için son 10 gündeki toplam satış miktarı izlenerek **Günlük Satış Hızı ($V$)** hesaplanır:
    $$V = \frac{\sum_{i=1}^{10} Q_i}{10}$$
    *(Burada $Q_i$, $i$. gündeki satış miktarıdır)*
  * Önümüzdeki **7 Günlük Talep Tahmini ($F_7$)** doğrusal ekstrapolasyon ile bulunur:
    $$F_7 = V \times 7$$
  * Stoğun kaç gün içinde sıfırlanacağı (**Tahmini Tükenme Süresi - $D_{out}$**) hesaplanır:
    $$D_{out} = \frac{S}{V}$$
    *(Burada $S$ mevcut envanter miktarını ifade eder. $V = 0$ ise tükenme riski yoktur.)*
* **Görselleştirme:** Dashboard'daki **🤖 Yapay Zeka Satış & Stok Analizi** panelinde ürünlerin haftalık tahmini talebi ve tükenme süreleri listelenir. 3 günün altında tükenme riski olan ürünler otomatik olarak kırmızı satır (Kritik Risk), 7 günün altındakiler sarı satır (Düşük Risk) olarak etiketlenir.

### 📄 3. Dinamik HTML Fatura ve Makbuz Üretim Modülü
* Satış tamamlandığında sistem, satılan ürün, adet, birim fiyat, ciro ve kasiyer bilgilerini içeren kurumsal tasarımlı dinamik bir **HTML Fatura** (`exports/fatura_[fatura_id].html`) oluşturur.
* Fatura, tarayıcıda otomatik olarak açılarak kullanıcının tek tıkla **"Yazdır"** veya **"PDF Olarak Kaydet"** yapabilmesine olanak tanır.

---

## 🎨 Tasarım Estetiği ve UI/UX
* **Dinamik Tema Seçici:** Sol menü üzerinden anında **Karanlık Mod (Darkly)** ile **Aydınlık Mod (Flatly)** arasında geçiş yapılabilir.
* **Dinamik Grafik Çizimleri:** Matplotlib ile çizilen 7 günlük gelir alanı grafiği (`fill_between`) ve en çok satılan ürünler bar grafiği, seçilen temaya göre arka plan ve çizgi renklerini otomatik olarak günceller.
* **Renk Kodlu Tablolar:** Stok seviyesi 0 olan ürünler kırmızı, kritik seviyenin altında olanlar sarı uyarı renkleriyle listelenir.

---

## 🗂️ Proje Yapısı

```text
inventory-sales-tracker/
│
├── app.py                      # Uygulama Giriş Noktası
├── requirements.txt            # Bağımlılık Listesi
├── codebase_analysis.md        # Mimari ve Teknik Analiz Belgesi
│
├── database/
│   ├── db.py                   # Bağlantı ve Örnek Veri Seeding Mantığı
│   └── schema.sql              # SQLite Tablo Şemaları ve İndeksler
│
├── services/
│   ├── auth_service.py         # SHA-256 Parola Doğrulama Servisi
│   ├── invoice_service.py      # HTML Fatura Oluşturma Modülü
│   ├── product_service.py      # Ürün CRUD İşlemleri
│   └── sales_service.py        # Satış Kaydı ve Yapay Zeka Tahmin Motoru
│
├── ui/
│   ├── login_frame.py          # Giriş Ekranı (Login)
│   ├── main_window.py          # Ana Çerçeve ve Dinamik Tema Seçici
│   ├── dashboard_frame.py      # Analiz Paneli & AI Tablosu
│   ├── products_frame.py       # Ürün Listeleme & Kasiyer Koruması
│   ├── sales_frame.py          # Satış Yapma ve Fatura Tetikleme
│   └── reports_frame.py        # Filtrelenebilir Finansal Raporlar
│
└── exports/                    # Çıktı Klasörü (HTML Fatura & CSV Rapor)
```

---

## ⚙️ Kurulum ve Çalıştırma

1. **Bağımlılıkları Yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Uygulamayı Çalıştırın:**
   ```bash
   python app.py
   ```

3. **Giriş Bilgileri:**
   * **Yönetici (Admin):** `admin` / `admin123`
   * **Kasiyer:** `kasiyer` / `kasiyer123`
# Stockify - Mezuniyet Projesi Kod ve Sunum Rehberi

Bu rehber, projenizin jüri sunumunda (tez savunmasında) kodları hocalarınıza en profesyonel şekilde anlatabilmeniz için hazırlanmıştır. Hangi dosyanın ne işe yaradığını, içindeki fonksiyonları ve hocaların sorabileceği olası sorulara karşı vermeniz gereken yanıtları içerir.

---

## 📂 1. Klasör Yapısı ve Genel Akış

Uygulama, yazılım mühendisliğinde kabul görmüş **Katmanlı Mimari (N-Tier Architecture)** prensibiyle yazılmıştır. Kodlar arayüz (UI), iş mantığı (Services) ve veri erişimi (Database) olarak üç ana katmana ayrılmıştır. Bu ayrım, kodun okunabilirliğini ve bakımını kolaylaştırır.

---

## 📄 2. Dosya Dosya Kod Açıklamaları

### 📍 `app.py` (Uygulama Giriş Noktası)
* **Ne İşe Yarar?** Uygulamanın ana kapısıdır. Program çalıştırıldığında ilk bu dosya yürütülür.
* **Kritik Kodlar / Fonksiyonlar:**
  * `initialize_database()`: Veri tabanının kurulmasını tetikler.
  * `LoginFrame(app, on_login_success)`: Uygulamayı giriş ekranıyla başlatır.
  * `on_login_success(user)`: Giriş başarılı olduğunda giriş arayüzünü yok edip (`destroy`), ana ekranı (`MainWindow`) yükler.
* **👨‍🏫 Jüriye Nasıl Anlatılır?** 
  > *"Hocam, bu dosya uygulamamızın tetikleyici merkezidir. İlk olarak SQLite veri tabanını ayağa kaldırır, ardından kullanıcıyı karşılayan giriş ekranını yükler. Giriş başarılı olduğunda oturum bilgilerini hafızada tutarak ana paneli başlatır."*

---

### 📍 `database/db.py` (Veri Tabanı Bağlantı ve Tohumlama)
* **Ne İşe Yarar?** SQLite veri tabanına bağlantı açılmasını, şemanın kurulmasını ve sisteme ilk kez giriş yapıldığında örnek ürünler ile varsayılan şifreli kullanıcıların yüklenmesini sağlar.
* **Kritik Kodlar / Fonksiyonlar:**
  * `get_connection()`: SQLite veri tabanına güvenli bir bağlantı açar. `PRAGMA foreign_keys = ON;` koduyla ilişkisel bütünlüğü (Foreign Key) aktif eder.
  * `hash_password(password)`: Parolaları şifrelemek için **SHA-256** algoritmasını kullanır.
  * `initialize_database()`: `schema.sql` dosyasını okuyarak tabloları oluşturur.
  * `seed_sample_data(conn)`: Eğer sistem boşsa örnek ürünleri ve varsayılan `admin` (şifre: `admin123`) ile `kasiyer` (şifre: `kasiyer123`) hesaplarını şifreli olarak veri tabanına ekler.
* **👨‍🏫 Jüriye Nasıl Anlatılır?**
  > *"Hocam, veri tabanı işlemlerimiz burada yürütülüyor. SQLite kullandık çünkü sunucu kurulumu gerektirmiyor ve uygulamanın taşınabilir olmasını sağlıyor. Güvenlik için şifreleri veri tabanında açık halde değil, SHA-256 algoritmasıyla şifrelenmiş (hash) olarak saklıyoruz."*

---

### 📍 `database/schema.sql` (Veri Tabanı Şeması)
* **Ne İşe Yarar?** Veri tabanındaki tabloları ve veri arama hızını artıran indeksleri tanımlar.
* **👨‍🏫 Jüriye Nasıl Anlatılır?**
  > *"Hocam, burada 3 adet ilişkisel tablomuz var: `products` (Ürünler), `sales` (Satışlar) ve `users` (Kullanıcılar). Performansı artırmak ve arama işlemlerini milisaniyeler seviyesine indirmek için ürün adları, satış tarihleri ve kullanıcı adları kolonları üzerinde veritabanı indeksleri (Index) oluşturduk."*

---

### 📍 `services/auth_service.py` (Giriş Yetkilendirme Servisi)
* **Ne İşe Yarar?** Kullanıcının girdiği kullanıcı adı ve şifreyi veri tabanındakilerle karşılaştırır.
* **Kritik Kodlar / Fonksiyonlar:**
  * `login_user(username, password)`: Girilen şifreyi SHA-256 ile şifreleyip veri tabanındaki hash ile karşılaştırır. Eşleşirse kullanıcının rolünü (`admin` veya `kasiyer`) döndürür.
* **👨‍🏫 Jüriye Nasıl Anlatılır?**
  > *"Hocam, bu servis giriş yapan kullanıcının kimlik doğrulamasını (Authentication) yapar. Güvenlik önlemi olarak şifre karşılaştırmasını ham metin üzerinden değil, şifrelenmiş hash değerleri üzerinden yapar."*

---

### 📍 `services/invoice_service.py` (Fatura Üretim Servisi)
* **Ne İşe Yarar?** Yapılan satışlar için modern ve şık bir fatura belgesi üretir.
* **Kritik Kodlar / Fonksiyonlar:**
  * `generate_html_invoice(...)`: Satış bilgilerini alarak şablon bir HTML fatura dosyası oluşturur, bunu `exports/` klasörüne yazar ve kullanıcının internet tarayıcısında (Chrome/Edge vb.) otomatik olarak açar.
* **👨‍🏫 Jüriye Nasıl Anlatılır?**
  > *"Hocam, bu modül satış sonrasında kurumsal görünümlü dinamik bir HTML fatura üretir. Bu faturayı tarayıcı üzerinden doğrudan yazdırabilir veya tek tıkla PDF olarak kaydedebilirsiniz. Harici ağır PDF kütüphanelerine bağımlı kalmadan temiz bir çıktı sunar."*

---

### 📍 `services/product_service.py` (Ürün İş Mantığı)
* **Ne İşe Yarar?** Envanterdeki ürünlerin eklenmesi, güncellenmesi, silinmesi ve listelenmesi gibi CRUD (Create, Read, Update, Delete) iş mantığını yönetir.
* **Kritik Kodlar / Fonksiyonlar:**
  * `add_product(...)`, `update_product(...)`, `delete_product(...)`: Ürün ekler, düzenler ve siler.
  * `search_products(keyword)`: Envanterde ürün adı veya kategorisine göre dinamik filtreleme yapar.
* **👨‍🏫 Jüriye Nasıl Anlatılır?**
  > *"Hocam, bu servis envanter yönetimimizin CRUD katmanıdır. Arayüzden gelen ürün bilgilerini kontrol ederek veri tabanına yazar veya günceller."*

---

### 📍 `services/sales_service.py` (Satış ve Yapay Zeka Analiz Servisi)
* **Ne İşe Yarar?** Satış işlemlerini kaydeder, kar oranlarını hesaplar ve **Yapay Zeka tahminlerini** yapar.
* **Kritik Kodlar / Fonksiyonlar:**
  * `create_sale(product_id, quantity)`: Stok kontrolü yapar, satışı kaydeder, kârı hesaplar ve envanter stokunu otomatik düşer.
  * `get_ai_sales_forecast()`: **Yapay Zeka/Makine Öğrenmesi Tahmin Motoru.** Son 10 günlük satışların ortalama hızını çıkarır. Gelecek 7 günün talep tahminini doğrusal regresyon mantığıyla hesaplar ve mevcut stoğun kaç günde tükeneceğini öngörür.
* **👨‍🏫 Jüriye Nasıl Anlatılır?**
  > *"Hocam, bu servis sistemin en akıllı parçasıdır. Satış yapıldığında stokları otomatik düşer. Ayrıca son 10 günlük satış ivmesini hesaplayarak doğrusal bir yapay zeka tahmin modeli çalıştırır. Ürünlerin gelecek haftaki tahmini taleplerini ve kaç gün sonra stoklarının tükeneceğini hesaplayarak yöneticiye erken sipariş uyarısı verir."*

---

### 📍 `ui/login_frame.py` (Giriş Ekranı Tasarımı)
* **Ne İşe Yarar?** Kullanıcının kullanıcı adı ve şifre girdiği şık arayüz kartıdır.
* **👨‍🏫 Jüriye Nasıl Anlatılır?**
  > *"Hocam, ttkbootstrap temasıyla uyumlu, modern tasarımlı giriş ekranımızdır. Hatalı girişlerde kullanıcıya uyarı mesajı gösterir."*

---

### 📍 `ui/main_window.py` (Ana Çerçeve & Rol Yetkilendirme)
* **Ne İşe Yarar?** Giriş yaptıktan sonra açılan ana penceredir. Sol menüyü barındırır.
* **Kritik Kodlar / Fonksiyonlar:**
  * **Rol Kontrolü:** Kasiyer rolündeki kullanıcılar için `reports_btn` (Raporlar butonu) `state=DISABLED` yapılarak kilitlenir.
  * `toggle_theme()`: Tek tıkla uygulamayı aydınlık veya karanlık moda geçirir.
  * `logout()`: Oturumu güvenli bir şekilde kapatarak kullanıcıyı giriş ekranına yönlendirir.
* **👨‍🏫 Jüriye Nasıl Anlatılır?**
  > *"Hocam, bu dosya ana penceremizi yönetir. Dinamik tema desteği sunarak göz yormayan karanlık mod ile açık mod arasında geçiş sağlar. Ayrıca rol tabanlı güvenlik burada kontrol edilir; Kasiyer rolüyle girildiğinde Raporlar menüsü otomatik olarak devre dışı bırakılır."*

---

### 📍 `ui/dashboard_frame.py` (Gösterge Paneli)
* **Ne İşe Yarar?** İstatistik kartlarını, Matplotlib grafiklerini ve Yapay Zeka tahmin tablosunu gösterir.
* **Kritik Kodlar / Fonksiyonlar:**
  * `create_revenue_chart()`: Son 7 günlük ciroyu modern bir alan grafiği (Area Chart) olarak çizer.
  * `style_chart()`: Grafikleri aktif temaya göre dinamik olarak renklendirir.
  * **Yapay Zeka Tablosu:** Yapay zekadan gelen tükenme tahminlerini listeler. Kritik durumdakileri kırmızı ve sarı satır olarak renklendirir.
* **👨‍🏫 Jüriye Nasıl Anlatılır?**
  > *"Hocam, bu panel yöneticinin işletmenin genel durumunu gördüğü ekrandır. Matplotlib ile entegre edilmiş dinamik grafiklerimiz mevcuttur. Alt kısımda ise yapay zekanın erken uyarı analizleri yer alır."*

---

### 📍 `ui/products_frame.py` (Ürün Arayüzü & Yetki Engeli)
* **Ne İşe Yarar?** Ürünlerin listelendiği ve yönetildiği ekrandır.
* **Kritik Kodlar / Fonksiyonlar:**
  * **Kasiyer Koruması:** Eğer kullanıcı kasiyer ise, formdaki tüm giriş alanları ve "Kaydet, Güncelle, Sil" butonları kilitlenir (`state=DISABLED`).
* **👨‍🏫 Jüriye Nasıl Anlatılır?**
  > *"Hocam, bu ekran envanter takip ekranıdır. Kritik minimum stok seviyesinin altına düşen ürünleri otomatik sarı ve kırmızı renkle gösterir. Kasiyerlerin envanter verilerini değiştirmesini engellemek için kasiyer girişi yapıldığında düzenleme formunu tamamen kilitler."*

---

### 📍 `ui/sales_frame.py` (Satış Arayüzü)
* **Ne İşe Yarar?** Kasiyerin veya yöneticinin satış yaptığı ekrandır.
* **👨‍🏫 Jüriye Nasıl Anlatılır?**
  > *"Hocam, burası satışların girildiği ekrandır. Stokta olmayan veya yetersiz olan ürünlerin satılmasına izin vermez. Satış onaylandığında otomatik fatura oluşturma sorusu tetiklenir."*

---

### 📍 `ui/reports_frame.py` (Raporlama ve CSV Aktarımı)
* **Ne İşe Yarar?** İki tarih arasındaki ciro, kâr ve satış verilerini filtreleyip raporlar.
* **Kritik Kodlar / Fonksiyonlar:**
  * `export_csv()`: Filtrelenen rapor verilerini `exports/` klasörüne Excel ile uyumlu CSV dosyası olarak kaydeder.
* **👨‍🏫 Jüriye Nasıl Anlatılır?**
  > *"Hocam, burası finansal analizlerin yapıldığı rapordur. Belirlenen tarih aralıklarına göre filtreleme yapabilir ve işletmenin ciro/net kâr durumunu tek tıkla Excel uyumlu CSV formatında dışarı aktarabilir."*

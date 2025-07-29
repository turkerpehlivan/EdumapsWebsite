# EduMaps - Yorum Sistemi ve Veli Değerlendirme

Bu proje, EduMaps okul arama platformuna **yorum sistemi ve veli değerlendirme** özelliklerini ekler. SQL Server Express veritabanı kullanılarak geliştirilmiştir.

## 🎯 Özellikler

### ✅ Tamamlanan Özellikler

#### 1. Yorum Sistemi ve Veli Değerlendirme
- **Yorum formu** - Yıldız puanlama sistemi ile
- **Admin yorum onay paneli** - Yorumların moderasyonu
- **Spam/XSS güvenlik denetimi** - Otomatik spam filtreleme
- **Yorum listeleme algoritması** - Onaylanmış yorumları gösterme

#### 2. Detaylı Puanlama Sistemi
- Genel puan (1-5 yıldız)
- Fiziksel olanaklar puanı
- Öğretmen kalitesi puanı
- Ulaşım puanı

#### 3. Güvenlik Özellikleri
- **XSS Koruması** - HTML etiketlerinin temizlenmesi
- **Spam Filtreleme** - Gelişmiş spam skoru algoritması
- **Rate Limiting** - Kullanıcı başına saatte 3 yorum sınırı
- **Input Validasyonu** - Frontend ve backend validasyon

#### 4. Admin Panel
- Bekleyen yorumları görüntüleme
- Yorum onaylama/reddetme
- Spam yorumları yönetme
- İstatistikler ve raporlama

#### 5. Okul Profili (360 Tur, Foto/Video, Öğretmen Tanıtımları) - Türker Pehlivan
- **360° Sanal Tur** - Pannellum.js ile interaktif okul gezisi
- **Fotoğraf Galerisi** - Swiper.js ile responsive galeri
- **Video Embed Sistemi** - YouTube entegrasyonu ile öğretmen tanıtımları
- **İçerik Etkileşimi** - Modal sistemler ve klavye kısayolları
- **Öğretmen Video Tanıtımları** - Detaylı profil bilgileri ile

## 🛠️ Teknoloji Stack

- **Backend**: Python Flask
- **Veritabanı**: SQL Server Express
- **Frontend**: HTML, CSS, JavaScript
- **ORM**: SQLAlchemy
- **Güvenlik**: Bleach (XSS koruması)
- **360° Tur**: Pannellum.js
- **Galeri**: Swiper.js
- **Video**: YouTube Embed API

## 📦 Kurulum

### Gereksinimler
- Python 3.8+
- SQL Server Express
- ODBC Driver 17 for SQL Server

### 1. Proje Kurulumu
```bash
git clone <repository-url>
cd edumaps_clone
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
```

### 2. Veritabanı Kurulumu
```bash
# Veritabanı migration
python backend/migrate_db.py

# Test verilerini oluştur
python backend/create_test_data.py
```

### 3. Uygulamayı Başlat
```bash
python backend/app.py
```

## 🌐 Kullanım

### Ana Uygulama
- **URL**: http://127.0.0.1:5000
- Okul detaylarını görüntüleme
- 360° sanal tur deneyimi
- Fotoğraf galerisi (modal görüntüleme)
- Öğretmen video tanıtımları
- Yorum yapma (giriş gerekli)
- Yorumları okuma

### Admin Panel
- **URL**: http://127.0.0.1:5000/admin.html
- **Giriş**: E-posta: admin@edumaps.com, Şifre: admin123

### Test Kullanıcıları
```
Admin: admin / admin123
Test Kullanıcı: testuser / test123
Veli: veli1 / veli123
```

## 🔧 API Endpoints

### Yorum API'leri
- `POST /api/reviews` - Yeni yorum ekleme
- `GET /api/schools/{id}` - Okul detayları ve yorumları

### Admin API'leri
- `POST /api/admin/login` - Admin girişi
- `GET /api/admin/reviews/pending` - Bekleyen yorumlar
- `GET /api/admin/reviews/spam` - Spam yorumlar
- `POST /api/admin/reviews/{id}/approve` - Yorum onaylama
- `POST /api/admin/reviews/{id}/reject` - Yorum reddetme

## 🛡️ Güvenlik Özellikleri

### Spam Filtreleme Algoritması
- URL ve link kontrolü
- Aşırı pozitif/negatif kelime analizi
- Uzunluk kontrolü
- Tekrarlayan karakter/kelime tespiti
- Büyük harf oranı analizi
- Özel karakter yoğunluğu kontrolü

### XSS Koruması
- HTML etiketlerinin temizlenmesi
- Zararlı script'lerin engellenmesi
- Input sanitization

### Rate Limiting
- Kullanıcı başına saatte 3 yorum
- Aynı okula birden fazla yorum engelleme
- IP bazlı koruma

## 📊 Veritabanı Şeması

### Reviews Tablosu (Yeni Kolonlar)
```sql
moderated_by INT NULL          -- Hangi admin onayladı
moderation_date DATETIME2 NULL -- Onay tarihi
is_spam BIT NOT NULL DEFAULT 0 -- Spam işareti
spam_score FLOAT NOT NULL DEFAULT 0.0 -- Spam skoru
```

### Users Tablosu (Yeni Kolonlar)
```sql
is_admin BIT NOT NULL DEFAULT 0   -- Admin yetkisi
is_active BIT NOT NULL DEFAULT 1  -- Aktif kullanıcı
```

## 🧪 Test

Test scriptini çalıştırarak tüm özellikleri test edebilirsiniz:
```bash
python test_review_system.py
```

Test kapsamı:
- Yorum ekleme
- Spam filtreleme
- Rate limiting
- Admin API'leri
- XSS koruması

## 📈 İstatistikler

Test verilerinde:
- 3 kullanıcı (1 admin, 2 normal)
- 4 okul
- 4 yorum (1 onaylanmış, 3 bekleyen)
- Spam filtreleme aktif
- Rate limiting çalışıyor

## 🎬 Türker Pehlivan'ın Katkıları

### Video Embed Sistemi
- YouTube entegrasyonu ile öğretmen tanıtım videoları
- Modal tabanlı video oynatıcı
- Öğretmen profil bilgileri entegrasyonu

### İçerik Etkileşimi
- Fotoğraf galerisi modal görüntüleme
- Klavye kısayolları (ESC ile kapatma)
- Responsive tasarım optimizasyonu
- 360° tur kullanıcı deneyimi iyileştirmeleri

### Özellikler
- ✅ 360° sanal tur (Pannellum.js)
- ✅ Fotoğraf galerisi (Swiper.js)
- ✅ Öğretmen video tanıtımları
- ✅ Modal sistemler
- ✅ Responsive tasarım
- ✅ Klavye navigasyonu

## 🔄 Gelecek Geliştirmeler

- Email bildirimleri
- Yorum yanıtlama sistemi
- Gelişmiş spam filtreleme (ML)
- Mobil uygulama desteği
- Çoklu dil desteği
- VR tur desteği (Türker Pehlivan)

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun
3. Değişikliklerinizi commit edin
4. Pull request gönderin

## 📞 İletişim

Sorularınız için issue açabilir veya doğrudan iletişime geçebilirsiniz.

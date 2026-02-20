# Medya Yükleme Sitesi

Kullanıcıların fotoğraf ve video yükleyebileceği, admin panelinden yönetilebilecek bir web uygulaması.

## Özellikler

- Kullanıcı kayıt ve giriş sistemi
- Fotoğraf ve video yükleme
- Dosya yönetimi ve önizleme
- Admin paneli
- Modern ve responsive arayüz
- Bootstrap 5 ve Font Awesome ikonlar

## Kurulum

1. Gerekli kütüphaneleri yükleyin:
```bash
pip install -r requirements.txt
```

2. Uygulamayı çalıştırın:
```bash
python app.py
```

3. Tarayıcınızda açın:
```
http://localhost:5000
```

## Varsayılan Admin Hesabı

Uygulama ilk çalıştığında otomatik olarak admin kullanıcısı oluşturulur:

- **Kullanıcı Adı:** admin
- **Şifre:** admin123

## Desteklenen Formatlar

### Fotoğraflar
- JPG, JPEG
- PNG
- GIF
- WEBP

### Videolar
- MP4
- AVI
- MOV
- WMV
- FLV

## Dosya Boyutu Limiti

- Dosya boyutu limiti yok (sınırsız)

## Proje Yapısı

```
media_upload_site/
├── app.py                 # Ana Flask uygulaması
├── requirements.txt       # Gerekli kütüphaneler
├── templates/            # HTML şablonları
│   ├── base.html         # Ana şablon
│   ├── index.html        # Ana sayfa
│   ├── login.html        # Giriş sayfası
│   ├── register.html     # Kayıt sayfası
│   └── admin.html        # Admin paneli
├── static/               # Statik dosyalar
│   ├── css/
│   ├── js/
│   └── images/
└── uploads/              # Yüklenen medya dosyaları
    ├── photos/
    └── videos/
```

## Kullanım

1. **Kayıt Ol:** Yeni kullanıcı hesabı oluşturun
2. **Giriş Yap:** Hesabınıza giriş yapın
3. **Medya Yükle:** Fotoğraf veya video dosyalarınızı yükleyin
4. **Admin Paneli:** Admin kullanıcısıyla giriş yaparak tüm medya dosyalarını yönetin

## Güvenlik

- Şifreler hash'lenerek saklanır
- Dosya yükleme güvenliği
- Oturum yönetimi
- Admin yetki kontrolü

## Teknolojiler

- **Backend:** Flask, SQLAlchemy
- **Frontend:** Bootstrap 5, Font Awesome
- **Veritabanı:** SQLite
- **Dosya Yönetimi:** Werkzeug

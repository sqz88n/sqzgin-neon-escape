# SQZGIN BOI: NEON ESCAPE

Python 3 + Pygame ile hazırlanmış, çevrimdışı oynanabilen neon arcade hayatta kalma oyunu.

## Çalıştırma
1. Python 3.10 veya daha yeni bir sürüm kur.
2. Bu klasörü PyCharm ile aç.
3. PyCharm terminalinde:
   ```bash
   python -m pip install -r requirements.txt
   python main.py
   ```
4. Oyunu başlatmak için ana menüde **OYNA** seçeneğine tıkla.

## Kontroller
- WASD / ok tuşları: hareket
- SPACE: dash
- ESC: duraklat / menüye dön
- Fare: menü butonları

## İçerik
- Neon şehir arka planı, enerji karakteri, lazer tehdidi, engeller ve farklı kristaller
- Klasik, Zaman Saldırısı, Kristal Avı ve Antrenman modları
- Dash, kalkan, mıknatıs, yavaşlatma ve puan çarpanı güçleri
- Skor, kombo, rekor, oyun sonu, garaj ve kozmetik satın alma
- Ayarlar, başarımlar, istatistik ekranı
- Kullanıcı profilini güvenli biçimde yerel JSON'a kaydetme
- Harici görsel/ses dosyası zorunlu değil; ses efektleri prosedürel oluşturulur

## Kayıt konumu
Windows: `%APPDATA%\\SQZGIN_NEON_ESCAPE\\profile.json`
Diğer platformlarda kullanıcı veri dizini altında `SQZGIN_NEON_ESCAPE/profile.json`.

## Durum ve sınırlamalar
Bu paket masaüstü Pygame projesidir. Android APK veya Windows EXE içermez. Dokunmatik kontroller için temel sürükleme/dokunma sistemi bu sürümde uygulanmamıştır; Android'de doğrudan çalıştığı iddia edilmez. Müzik dosyası eklenmediği için arka plan müziği yoktur; kısa prosedürel efekt sesleri kullanılır. Günlük görevler ve kapsamlı görev ödülü sistemi henüz uygulanmış değildir. Pencere boyutu değiştirilebilir; çözünürlük/FPS seçenekli gelişmiş ayarlar bu sürümde yoktur.

## Test notu
Kaynak dosyalar Python sözdizimi açısından kontrol edilmiştir. Bu ortamda Pygame penceresini açarak uçtan uca oynanış testi yapılamadı; bu nedenle tüm oynanış senaryolarının test edildiği iddia edilmez.

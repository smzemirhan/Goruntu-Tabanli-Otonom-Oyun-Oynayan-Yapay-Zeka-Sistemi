# Görüntü Tabanlı Otonom Oyun Oynayan Yapay Zekâ Sistemi

Bu proje, Mersin Üniversitesi Bilgisayar Mühendisliği Bölümü **Bitirme Ödevi** kapsamında geliştirilmiş; rekabetçi birinci şahıs nişancı (FPS) oyunlarında oyun belleğine (RAM) veya kaynak dosyalarına müdahale etmeden, yalnızca görsel verileri analiz ederek çalışan otonom bir yapay zekâ ajanıdır.

Geleneksel yazılım botlarının aksine "Sıfır İz (Zero-Trace)" prensibiyle tasarlanmış olup, İnsan Arayüz Cihazı (HID) emülasyonu sayesinde anti-hile (anti-cheat) sistemleri tarafından tespit edilemeyen (undetected) donanımsal bir yapıya sahiptir.

## 👥 Geliştiriciler
* **Emirhan Semizoğlu**
* **Ayşe Nur Akıncı**

*Danışman: Doç. Dr. Volkan Yamaçlı*

---

## Proje Özellikleri

* **Görüntü İşleme ile Otonom Karar:** Oyunun API'lerine bağlanmak yerine ekrandaki pikselleri okuyarak insan gibi tepki verir.
* **YOLOv8 ile Gerçek Zamanlı Tespit:** Özel eğitilmiş veri seti kullanılarak FP16 formatında ~12ms çıkarım (inference) hızına ulaşılmıştır.
* **Çift Bilgisayar (Dual-PC) Mimarisi:** Görüntü işleme ve yapay zekâ yükü ikinci bir bilgisayara aktarılarak oyun performansında (FPS) oluşabilecek darboğazlar %100 engellenmiştir.
* **Arduino HID İzolasyonu:** Yapay zekânın ürettiği X-Y koordinat kararları seri haberleşme ile Arduino'ya gönderilir ve ana bilgisayara fiziksel bir donanım faresi (hardware mouse) hareketi olarak iletilir.
* **Dinamik Yumuşatma (Dynamic Smoothing):** Hedefe olan uzaklığa göre fare hızını otonom ayarlayarak nişangâh titremesi (jitter) ve hedefi taşırma (overshoot) hatalarını önler.

---

## Kullanılan Teknolojiler ve Donanımlar

### Yazılım
* **Dil:** Python 3.11+
* **Yapay Zekâ:** Ultralytics YOLOv8 (Deep Learning / Object Detection)
* **Görüntü İşleme:** OpenCV, MSS
* **Haberleşme:** PySerial, Win32API

### Donanım
* **Host PC:** Oyunun çalıştığı ana bilgisayar.
* **Client PC:** Yapay zekâ modelinin çalıştığı bilgisayar.
* **Video Yakalama Kartı (Capture Card):** Host PC'den Client PC'ye kayıpsız görüntü aktarımı için.
* **Arduino Leonardo:** HID (Human Interface Device) fare simülasyonu için.
* **USB-TTL Dönüştürücü:** Client PC ile Arduino arasındaki seri haberleşme köprüsü.

---

## Kurulum ve Kullanım

### 1. Gerekli Kütüphanelerin Yüklenmesi
Client PC üzerinde projeyi klonladıktan sonra gerekli bağımlılıkları yükleyin:
pip install ultralytics opencv-python numpy pyserial mss keyboard

### 2. Donanım Bağlantısı
Host PC'nin HDMI çıkışını Video Capture Card ile Client PC'ye bağlayın.

Client PC'ye USB-TTL dönüştürücüyü takın ve RX-TX çapraz bağlantılarını yaparak Arduino Leonardo'ya bağlayın.

Arduino Leonardo'yu Host PC'ye USB üzerinden standart bir fare olarak takın.

### 3. Sistemi Başlatma
Bağlantılar sağlandıktan sonra Client PC üzerinden otonom ajanı başlatın:
python Aimbot2.py

### Lisans
Bu proje, akademik bir bitirme ödevi prototipi olup eğitim ve araştırma amaçlı geliştirilmiştir. Kullanılan kütüphanelerin kendi açık kaynak lisanslarına tabidir.

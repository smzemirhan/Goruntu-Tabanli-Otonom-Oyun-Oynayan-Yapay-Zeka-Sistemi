# -*- coding: utf-8 -*-
import serial
import time

# --- AYARLAR ---
COM_PORT = 'COM14'  
BAUD_RATE = 115200

try:
    # Portu açıyoruz
    arduino = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    print(f"✅ BAĞLANTI BAŞARILI: {COM_PORT} portu açıldı.")
    print("Mavi (TX) ışığı kontrol et! PC2'deki fare sağa/sola hareket edip ATEŞ ETMELİ.")
    print("Durdurmak için terminalde CTRL+C tuşlarına basabilirsin.\n")
except Exception as e:
    print(f"❌ BAĞLANTI HATASI: Port açılamadı. Arduino IDE seri port ekranı açıksa kapatın.")
    print(f"Hata Detayı: {e}")
    exit()

try:
    while True:
        # Format: "X,Y,Click\n"
        
        # 1. Fareyi 50 piksel sağa kaydır (Ateş etme: 0)
        print("➡️ Fare sağa gönderiliyor...")
        arduino.write(b"50,0,0\n") 
        time.sleep(1) # 1 saniye bekle
        
        # 2. Hedefte dur ve ATEŞ ET (Sol Tık: 1)
        print("💥 ATEŞ EDİLİYOR! (Sol Tık)")
        arduino.write(b"0,0,1\n") 
        time.sleep(1)
        
        # 3. Fareyi 50 piksel sola kaydır (Ateş etme: 0)
        print("⬅️ Fare sola gönderiliyor...")
        arduino.write(b"-50,0,0\n")
        time.sleep(1)
        
        # 4. Hedefte dur ve ATEŞ ET (Sol Tık: 1)
        print("💥 ATEŞ EDİLİYOR! (Sol Tık)")
        arduino.write(b"0,0,1\n") 
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\n🛑 Test manuel olarak durduruldu, port kapatılıyor.")
    arduino.close()
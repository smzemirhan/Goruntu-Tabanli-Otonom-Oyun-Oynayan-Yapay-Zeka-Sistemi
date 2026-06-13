# -*- coding: utf-8 -*-
import cv2
import numpy as np
import serial 
from ultralytics import YOLO
import time
import keyboard
import random
import sys

# --- DONANIM AYARLARI ---
COM_PORT = 'COM14'         
BAUD_RATE = 115200        
CAP_CARD_ID = 0        

try:
    arduino = serial.Serial(COM_PORT, BAUD_RATE, timeout=0, write_timeout=0, dsrdtr=True)
    # Portun içindeki eski sıkışmış verileri temizle
    arduino.reset_input_buffer()
    arduino.reset_output_buffer()
    print(f"✅ SİSTEM HAZIR: {COM_PORT}")
except Exception as e:
    print(f"❌ PORT HATASI: {COM_PORT} - USB'yi çıkar tak yapın veya Arduino IDE'yi kapatın."); exit()

def send_to_arduino(x, y, click_action):
    x = max(-127, min(127, int(x)))
    y = max(-127, min(127, int(y)))
    arduino.write(f"{x},{y},{click_action}\n".encode())

# --- DOSYA VE MODEL ---
MODEL_YOLU = 'best1.pt' 

HEDEFLER = [3, 4] 
hedef_modu = "T'leri VUR"

SCREEN_SIZE = 320
merkez_x = SCREEN_SIZE // 2 
merkez_y = SCREEN_SIZE // 2

cap = cv2.VideoCapture(CAP_CARD_ID, cv2.CAP_DSHOW) 
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG')) 
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) 

crop_y1, crop_y2 = 540 - (SCREEN_SIZE//2), 540 + (SCREEN_SIZE//2)
crop_x1, crop_x2 = 960 - (SCREEN_SIZE//2), 960 + (SCREEN_SIZE//2)

silah_profilleri = {
    "TAARRUZ (F1)": {"SMOOTHING": 0.50, "BURST": 0.4, "ATIS_HIZI": 0.05, "BEKLEME": 0.15},
    "TABANCA (F2)": {"SMOOTHING": 0.55, "BURST": 0.1, "ATIS_HIZI": 0.15, "BEKLEME": 0.1},
    "SNIPER  (F3)": {"SMOOTHING": 0.70, "BURST": 0.0, "ATIS_HIZI": 0.00, "BEKLEME": 1.2}
}

aktif_profil = "TAARRUZ (F1)"
ayarlar = silah_profilleri[aktif_profil]

is_bursting = is_cooldown = False
burst_baslangic = cooldown_baslangic = son_atis_zamani = toggle_bekleme = 0

model = YOLO(MODEL_YOLU)
model.predict(np.zeros((SCREEN_SIZE, SCREEN_SIZE, 3), dtype=np.uint8), verbose=False)

print("\n" + "="*45)
print("🚀 TEK PAKET MİMARİSİ: TAKILMA VE PORT ÇÖKMESİ GİDERİLDİ 🚀")
print("="*45)

# BÜYÜK TRY-FINALLY BLOĞU: Kod çökse bile portu zorla kapatır!
try:
    while True:
        su_an = time.time()

        if keyboard.is_pressed('q'):
            print("Çıkış yapılıyor, port temizleniyor...")
            break # Döngüyü kırar, finally bloğuna gider

        if keyboard.is_pressed('f4') and (su_an - toggle_bekleme > 0.3):
            if 3 in HEDEFLER:
                HEDEFLER = [0, 1]; hedef_modu = "CT'leri VUR"
            else:
                HEDEFLER = [3, 4]; hedef_modu = "T'leri VUR"
            print(f"🔄 Takım: {hedef_modu}")
            toggle_bekleme = su_an

        ret, full_frame = cap.read()
        if not ret: continue 

        frame = full_frame[crop_y1:crop_y2, crop_x1:crop_x2]
        results = model.predict(frame, conf=0.45, verbose=False, half=True)
        
        hedef_bulundu = False
        en_yakin_mesafe = float('inf')
        hedef_fark_x = hedef_fark_y = 0

        for r in results:
            for box in r.boxes:
                if int(box.cls[0]) in HEDEFLER:
                    hedef_bulundu = True
                    x1, y1, x2, y2 = box.xyxy[0].tolist() 
                    
                    genislik = x2 - x1
                    yukseklik = y2 - y1

                    hedef_x = int(x1 + (genislik / 2))
                    hedef_y = int(y1 + (yukseklik * 0.35)) # Boyun/Göğüs

                    fark_x = hedef_x - merkez_x
                    fark_y = hedef_y - merkez_y
                    mesafe = (fark_x**2 + fark_y**2)**0.5
                    
                    if mesafe < en_yakin_mesafe:
                        en_yakin_mesafe = mesafe
                        hedef_fark_x = fark_x
                        hedef_fark_y = fark_y

        # Her döngüde değişkenleri sıfırla
        kaydir_x = kaydir_y = ates_durumu = 0

        # --- HESAPLAMA YAP (Henüz gönderme) ---
        if hedef_bulundu:
            d_smooth = ayarlar["SMOOTHING"]
            if en_yakin_mesafe > 100: d_smooth *= 1.5  
            elif en_yakin_mesafe < 30: d_smooth *= 0.6 
            
            sapma_x = random.randint(-1, 1) if en_yakin_mesafe > 20 else 0
            sapma_y = random.randint(-1, 1) if en_yakin_mesafe > 20 else 0

            kaydir_x = (hedef_fark_x + sapma_x) * d_smooth
            kaydir_y = (hedef_fark_y + sapma_y) * d_smooth
            
            if is_cooldown:
                if su_an - cooldown_baslangic >= ayarlar["BEKLEME"]:
                    is_cooldown = False 
            else:
                if abs(hedef_fark_x) < 50 and abs(hedef_fark_y) < 50:
                    if not is_bursting:
                        is_bursting = True; burst_baslangic = su_an

                    if is_bursting:
                        if su_an - burst_baslangic >= ayarlar["BURST"]:
                            is_bursting = False; is_cooldown = True; cooldown_baslangic = su_an
                        elif su_an - son_atis_zamani >= ayarlar["ATIS_HIZI"]:
                            ates_durumu = 1 # Tetiği çekme emrini hazırla
                            son_atis_zamani = su_an
        else:
            if is_bursting:
                is_bursting = False; is_cooldown = True; cooldown_baslangic = su_an

        # --- TEK PAKET GÖNDERİMİ ---
        # Sadece hareket varsa veya ateş edilecekse Arduino'yu meşgul et
        if kaydir_x != 0 or kaydir_y != 0 or ates_durumu != 0:
            send_to_arduino(kaydir_x, kaydir_y, ates_durumu)

finally:
    # 🚨 GÜVENLİ ÇIKIŞ: Hata verse bile bu blok KESİNLİKLE çalışır.
    print("Sistem kapanıyor, port güvenle serbest bırakıldı.")
    if 'arduino' in locals() and arduino.is_open:
        arduino.reset_output_buffer()
        arduino.close()
    if 'cap' in locals():
        cap.release()
    sys.exit()
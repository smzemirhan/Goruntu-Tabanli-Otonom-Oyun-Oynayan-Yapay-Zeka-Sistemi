# -*- coding: utf-8 -*-
import cv2
import numpy as np
import win32api
import win32con
from mss import mss
from ultralytics import YOLO
import time
import keyboard
import random

# --- DOSYA AYARLARI ---
MODEL_YOLU = 'best1.pt' 

# ---  TAKIM SEÇİMİ (GERÇEK DATA.YAML SIRALAMASINA GÖRE)  ---
# 0: CT-Body, 1: CT-Head, 2: Dead, 3: T-Body, 4: T-Head
HEDEFLER = [3] # Başlangıçta T'lerin vücuduna (3) kilitlen.
hedef_modu = "T'leri VUR (Sen CT'sin)"

# --- SENİN KLASİK EKRAN AYARLARIN (Sabit 1920x1080) ---
SCREEN_SIZE = 400
monitor = {"top": 540 - (SCREEN_SIZE//2), "left": 960 - (SCREEN_SIZE//2), "width": SCREEN_SIZE, "height": SCREEN_SIZE} 
merkez_x = SCREEN_SIZE // 2 
merkez_y = SCREEN_SIZE // 2

# --- SİLAH PROFİLLERİ ---
silah_profilleri = {
    "TAARRUZ (F1)": {"SMOOTHING": 0.35, "BURST": 0.5, "ATIS_HIZI": 0.06, "BEKLEME": 0.2},
    "TABANCA (F2)": {"SMOOTHING": 0.40, "BURST": 0.1, "ATIS_HIZI": 0.15, "BEKLEME": 0.1},
    "SNIPER  (F3)": {"SMOOTHING": 0.50, "BURST": 0.0, "ATIS_HIZI": 0.00, "BEKLEME": 1.2}
}

aktif_profil = "TAARRUZ (F1)"
ayarlar = silah_profilleri[aktif_profil]

# Sistem Değişkenleri
is_bursting = False
is_cooldown = False
burst_baslangic = 0
cooldown_baslangic = 0
son_atis_zamani = 0
toggle_bekleme = 0

model = YOLO(MODEL_YOLU)
sct = mss()

print("\n" + "="*45)
print(" YAZILIM AJANI: GERÇEK SINIFLARLA AKTİF ")
print("="*45)
print(f" HEDEF TAKIM: {hedef_modu} (Değiştirmek için F4)")
print(f" SİLAH PROFIILI: {aktif_profil} (F1, F2, F3)")
print("❌ ÇIKIŞ: 'q' tuşuna basılı tut")
print("="*45 + "\n")

while True:
    su_an = time.time()

    # --- KONTROL PANELİ ---
    if keyboard.is_pressed('q'):
        print("Aimbot güvenle kapatılıyor...")
        break

    #  TAKIM DEĞİŞTİRME (F4) 
    if keyboard.is_pressed('f4') and (su_an - toggle_bekleme > 0.3):
        if 3 in HEDEFLER:
            HEDEFLER = [0] # 0 = CT-Body
            hedef_modu = "CT'leri VUR (Sen T'sin)"
        else:
            HEDEFLER = [3] # 3 = T-Body
            hedef_modu = "T'leri VUR (Sen CT'sin)"
            
        print(f"🔄 Takım Değişti: Artık {hedef_modu}")
        toggle_bekleme = su_an

    if keyboard.is_pressed('f1') and aktif_profil != "TAARRUZ (F1)":
        aktif_profil = "TAARRUZ (F1)"
        ayarlar = silah_profilleri[aktif_profil]
        print(f" Profil: {aktif_profil}")
        
    elif keyboard.is_pressed('f2') and aktif_profil != "TABANCA (F2)":
        aktif_profil = "TABANCA (F2)"
        ayarlar = silah_profilleri[aktif_profil]
        print(f" Profil: {aktif_profil}")
        
    elif keyboard.is_pressed('f3') and aktif_profil != "SNIPER  (F3)":
        aktif_profil = "SNIPER  (F3)"
        ayarlar = silah_profilleri[aktif_profil]
        print(f" Profil: {aktif_profil}")

    # --- EKRAN OKUMA VE TAHMİN ---
    ekran = np.array(sct.grab(monitor))
    frame = cv2.cvtColor(ekran, cv2.COLOR_BGRA2BGR)
    
    results = model.predict(frame, conf=0.6, verbose=False, half=True)
    
    hedef_bulundu = False
    en_yakin_mesafe = float('inf')
    hedef_fark_x = 0
    hedef_fark_y = 0

    for r in results:
        boxes = r.boxes
        for box in boxes:
            cls = int(box.cls[0])
            
            # SADECE SEÇİLİ TAKIMI (0 veya 3) VUR
            if cls in HEDEFLER:
                hedef_bulundu = True
                x1, y1, x2, y2 = box.xyxy[0].tolist() 
                
                genislik = x2 - x1
                yukseklik = y2 - y1

                # Klasik %20 Formülü
                hedef_x = int(x1 + (genislik / 2))
                hedef_y = int(y1 + (yukseklik * 0.20)) 

                fark_x = hedef_x - merkez_x
                fark_y = hedef_y - merkez_y
                
                mesafe = (fark_x**2 + fark_y**2)**0.5
                
                if mesafe < en_yakin_mesafe:
                    en_yakin_mesafe = mesafe
                    hedef_fark_x = fark_x
                    hedef_fark_y = fark_y

    # --- HAREKET VE ATIŞ ALGORİTMASI ---
    if hedef_bulundu:
        mesafe = en_yakin_mesafe
        dinamik_smoothing = ayarlar["SMOOTHING"]
        if mesafe > 150: dinamik_smoothing = ayarlar["SMOOTHING"] * 1.7  
        elif mesafe < 40: dinamik_smoothing = ayarlar["SMOOTHING"] * 0.6 
        
        sapma_x = random.randint(-1, 1) if mesafe > 20 else 0
        sapma_y = random.randint(-1, 1) if mesafe > 20 else 0

        kaydir_x = int((hedef_fark_x + sapma_x) * dinamik_smoothing)
        kaydir_y = int((hedef_fark_y + sapma_y) * dinamik_smoothing)
        
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, kaydir_x, kaydir_y, 0, 0)
        
        if is_cooldown:
            if su_an - cooldown_baslangic >= ayarlar["BEKLEME"]:
                is_cooldown = False 
        else:
            if abs(hedef_fark_x) < 40 and abs(hedef_fark_y) < 40:
                if not is_bursting:
                    is_bursting = True
                    burst_baslangic = su_an

                if is_bursting:
                    if su_an - burst_baslangic >= ayarlar["BURST"]:
                        is_bursting = False
                        is_cooldown = True
                        cooldown_baslangic = su_an
                    else:
                        if su_an - son_atis_zamani >= ayarlar["ATIS_HIZI"]:
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                            time.sleep(0.01) 
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                            son_atis_zamani = su_an
                            
    else:
        if is_bursting:
            is_bursting = False
            is_cooldown = True
            cooldown_baslangic = su_an

cv2.destroyAllWindows()

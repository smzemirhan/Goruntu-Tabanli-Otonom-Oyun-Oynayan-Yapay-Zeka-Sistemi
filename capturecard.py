import cv2

def capture_card_bul():
    # Ýlk 5 ID'yi tara
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                cv2.imshow(f'Kamera ID: {i} - Görüntü Var mi?', frame)
                print(f"ID {i} çalýþýyor. Capture Card görüntüsü bu mu? (Evet ise 'q' basýn)")
                if cv2.waitKey(0) & 0xFF == ord('q'):
                    cap.release()
                    cv2.destroyAllWindows()
                    return i
            cap.release()
    cv2.destroyAllWindows()
    print("Capture Card bulunamadý!")
    return None

id = capture_card_bul()
print(f"Senin Capture Card ID'n: {id}")
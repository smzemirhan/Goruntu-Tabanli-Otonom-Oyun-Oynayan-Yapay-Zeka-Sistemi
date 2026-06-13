#include <Mouse.h>

void setup() {
  Serial1.begin(115200); // PC2'den (TTL üzerinden) gelecek komutları dinlemeye başla
  Mouse.begin();         // Bilgisayara "Ben bir fareyim" de
}

void loop() {
  // Eğer PC2'den bir mesaj geldiyse:
  if (Serial1.available() > 0) {
    String data = Serial1.readStringUntil('\n');
    int comma1 = data.indexOf(',');
    int comma2 = data.indexOf(',', comma1 + 1);

    if (comma1 > 0 && comma2 > 0) {
      int x = data.substring(0, comma1).toInt();
      int y = data.substring(comma1 + 1, comma2).toInt();
      int click = data.substring(comma2 + 1).toInt();

      // Fareyi hareket ettir
      Mouse.move(x, y, 0);

      // Tıklama komutu geldiyse tıkla veya bırak
      if (click == 1) {
        Mouse.press(MOUSE_LEFT);
      } else if (click == 2) {
        Mouse.release(MOUSE_LEFT);
      }
    }
  }
}
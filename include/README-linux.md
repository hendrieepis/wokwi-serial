📘 Dokumentasi Praktikum: Simulasi Sensor dengan Potensiometer + Serial Redirect via tty0tty

## Tujuan

Mensimulasikan pengukuran kelembapan, suhu, dan intensitas cahaya menggunakan potensiometer yang terhubung ke pin A0, A1, dan A2 pada Arduino Mega2560, lalu mengirim data ke PC melalui serial virtual (tty0tty) dan ditampilkan di Python.

------

## Peralatan & Tools

- Ubuntu (Linux)
- VSCode + Wokwi Extension
- PlatformIO
- `tty0tty` (modul kernel virtual serial)
- Python 3 (dengan `pyserial`)
- picocom (untuk debugging serial)
- netcat (opsional untuk testing)

------

## 1. Instalasi tty0tty

Langkah instalasi sebai berikut

```bash
sudo apt install build-essential dkms
git clone https://github.com/freemed/tty0tty.git
cd tty0tty/module
make
sudo make install
sudo modprobe tty0tty
```

Setela itu lakukan Verifikasi

```bash
lsmod | grep tty0tty
ls /dev/tnt*
```

Harus muncul:

```
/dev/tnt0 /dev/tnt1 ...
```

------

## 2. Setup Proyek PlatformIO + Wokwi

### Struktur File:

```
test-mega2560-wokwi/
├── src/
│   └── main.cpp
├── platformio.ini
└── wokwi.toml
```

Isi main.cpp dengan kode berikut:

```cpp
void setup() {
  Serial.begin(9600);
}

void loop() {
  int kelembaban = analogRead(A0);
  int suhu = analogRead(A1);
  int cahaya = analogRead(A2);
  Serial.print("Kelembaban: ");
  Serial.print(kelembaban);
  Serial.print(", Suhu: ");
  Serial.print(suhu);
  Serial.print(", Cahaya: ");
  Serial.println(cahaya);
  delay(1000);
}
```

------

### `platformio.ini`

```ini
[env:mega2560]
platform = atmelavr
board = megaatmega2560
framework = arduino
monitor_speed = 9600
```

------

### wokwi.toml

```toml
[simulation]
rfc2217ServerPort = 4000
```

------

## 3. Redirect Serial dari Wokwi ke tty0tty

Jalankan Bridge dengan `socat`:

Jika Wokwi sebagai server di port 4000, jalankan perintah ini untuk membuat client yang menghubungkan `localhost:4000` ke `/dev/tnt0`:

```bash
socat -d -d TCP4:localhost:4000 /dev/tnt0,raw,echo=0
```

Sekarang:

- Wokwi akan mengirim data ke port 4000
- `socat` menghubungkan data itu ke **`/dev/tnt0`**
- Kamu bisa baca dari `/dev/tnt1` menggunakan **picocom** atau **Python**

------

## 4. Uji dengan Netcat (Verifikasi Koneksi Serial)

Jalankan perintah berikut di terminal untuk menghubungkan ke port 4000 yang disediakan oleh Wokwi:

```bash
netcat localhost 4000
```

**Verifikasi output** yang muncul di terminal:

```
Kelembaban: 512, Suhu: 500, Cahaya: 400
```

Jika data muncul dengan benar, berarti koneksi serial antara Wokwi dan `localhost:4000` sudah berhasil, dan kamu siap untuk melanjutkan ke langkah berikutnya.

------

## 5. Uji dengan Picocom

### Jalankan picocom untuk membaca data dari `/dev/tnt1`:

```bash
picocom /dev/tnt1 -b 9600
```

Kamu akan melihat output seperti:

```
Kelembaban: 512, Suhu: 500, Cahaya: 400
```

------

## 6. Python Code untuk Menampilkan Data Serial

monitor.py

```python
import serial

ser = serial.Serial("/dev/tnt1", 9600)

while True:
  line = ser.readline().decode().strip()
  print(line)
```

Jalankan:

```bash
python3 monitor.py
```

Output:

```
Kelembaban: 512, Suhu: 500, Cahaya: 400
```

------

## Catatan Tambahan

- Jika tidak muncul `/dev/tntX`, jalankan ulang `sudo modprobe tty0tty`.
- Untuk autoload `tty0tty` saat boot, tambahkan `tty0tty` ke `/etc/modules`.

------

## Checklist Mahasiswa

-  Install `tty0tty` & pastikan `/dev/tnt0`, `/dev/tnt1` ada
-  Buat proyek PlatformIO dengan kode sensor
-  Konfigurasi `wokwi.toml` untuk redirect ke port 4000
-  Jalankan `socat` untuk bridge ke `/dev/tnt0`
-  Verifikasi koneksi dengan `netcat localhost 4000`
-  Jalankan Python untuk baca dari `/dev/tnt1`

------

Dengan dokumentasi ini, mahasiswa dapat mengikuti langkah-langkah secara runtut, mulai dari instalasi dan setup hingga membaca data sensor melalui serial virtual yang terhubung antara Wokwi, tty0tty, dan aplikasi Python.
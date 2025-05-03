import serial
import time

# Ganti 'COMx' dengan port Arduino Mega Anda (misal 'COM3' di Windows atau '/dev/ttyACM0' di Linux)
PORT = '/dev/tnt1'   # <-- Ganti sesuai dengan port Anda
BAUD_RATE = 9600

def main():
    try:
        # Buka koneksi serial
        ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Tunggu Arduino reset

        print("Membaca data dari Arduino Mega...\nTekan Ctrl+C untuk berhenti.")

        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    try:
                        suhu, kelembaban, cahaya = map(int, line.split(','))
                        print(f"Suhu: {suhu}, Kelembaban: {kelembaban}, Cahaya: {cahaya}")
                    except ValueError:
                        print(f"Data rusak: {line}")
    except KeyboardInterrupt:
        print("\nProgram dihentikan oleh pengguna.")
    except serial.SerialException as e:
        print(f"Kesalahan serial: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Koneksi serial ditutup.")

if __name__ == "__main__":
    main()

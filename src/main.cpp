#include <Arduino.h>

void setup() {
	Serial.begin(9600);  // Pakai baud rate lebih tinggi (Mega mendukung)
	analogReference(DEFAULT);  // Kalibrasi ADC ke 5V (default)
  }
  
  void loop() {
	// Baca sensor (Pastikan pin sesuai wiring Anda!)
	int suhu = analogRead(A0);     // Pin A0 untuk suhu
	int kelembaban = analogRead(A1); // Pin A1 untuk kelembaban
	int cahaya = analogRead(A2);    // Pin A2 untuk cahaya
  
	// Kirim data dalam format CSV: suhu,kelembaban,cahaya
	Serial.print(suhu); 
	Serial.print(",");
	Serial.print(kelembaban);
	Serial.print(",");
	Serial.println(cahaya);  // println() untuk akhiri dengan \r\n
  
	delay(1000);  // Kirim setiap 1 detik
}
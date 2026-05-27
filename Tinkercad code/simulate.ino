#include <LiquidCrystal.h>
LiquidCrystal lcd(7, 8, 9, 10, 11, 12);

// Define Analog Pins for your potentiometers/sensors
const int tempPin = A0;
const int humPin = A1;
const int aqiPin = A2;

void setup() {
  Serial.begin(9600);
  lcd.begin(16, 2);
}

void loop() {
  // 1. Read raw analog data (0 to 1023) 
  int rawTemp = analogRead(tempPin);
  int rawHum = analogRead(humPin);
  int rawAQI = analogRead(aqiPin);

  // 2. Map to realistic ranges defined in your paper [cite: 40, 125]
  // Map Temp: 0-1023 to 0-50°C
  float temperature = map(rawTemp, 0, 1023, 0, 50); 
  // Map Humidity: 0-1023 to 20-90% RH
  int humidity = map(rawHum, 0, 1023, 20, 90);
  // Map AQI: 0-1023 to 0-500 ppm
  int AQI = map(rawAQI, 0, 1023, 0, 500);

  // 3. Print to Serial in CSV format for Python/ML [cite: 117]
  // Format: Temp,Humidity,AQI
  Serial.print(temperature, 1);
  Serial.print(",");
  Serial.print(humidity);
  Serial.print(",");
  Serial.println(AQI);

  // 4. Display on LCD for local awareness [cite: 90, 106]
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("T:"); lcd.print(temperature, 1); lcd.print("C ");
  lcd.print("H:"); lcd.print(humidity); lcd.print("%");

  lcd.setCursor(0, 1);
  lcd.print("AQI: "); lcd.print(AQI);
  
  // AQI Classification logic from Table III [cite: 125, 126]
  if(AQI > 150) lcd.print(" !UNSAFE"); 

  delay(2000); // Polling interval suggested in your methodology [cite: 103]
}
Entf-bild – Ultraschall-Entfernungsmessung mit 1602 IIC LCD-Anzeige
====================================================================
Projekt für Raspberry Pi 5 mit Pi OS 64-bit


BESCHREIBUNG
------------
Dieses Projekt misst die Entfernung per Ultraschall und zeigt das Ergebnis
live auf einem 1602 IIC LCD-Display (16x2 Zeichen, I2C-Schnittstelle) an.


BENOEDIGTE HARDWARE
-------------------
  - Raspberry Pi 5 (Pi OS 64-bit)
  - Ultraschallsensor (Pins beschriftet: Echo/TX/SDA  und  Trig/RX/SCL)
  - 1602 IIC LCD-Display (PCF8574-Adapter bereits aufgelötet)
  - Jumper-Kabel
  - (Optional) Steckplatine (Breadboard)
  - (Optional) Spannungsteiler: 2x Widerstände 1 kOhm und 2 kOhm


VERKABELUNG
-----------

1. Ultraschallsensor --> Raspberry Pi 5
   +--------------------------+---------------------------+
   | Sensor-Pin               | Raspberry Pi 5            |
   +--------------------------+---------------------------+
   | VCC  (5 V)               | Pin  2  (5 V)             |
   | GND                      | Pin  6  (GND)             |
   | Trig (RX / SCL)          | Pin 16  (GPIO 23)         |
   | Echo (TX / SDA)          | Pin 18  (GPIO 24)         |
   +--------------------------+---------------------------+

   WICHTIG – Spannungspegel:
   Der Raspberry Pi arbeitet mit 3,3-V-Logik. Viele Ultraschallsensoren
   liefern am Echo-Pin 5 V. Um den Pi zu schützen, einen Spannungsteiler
   verwenden:

       Echo-Pin (Sensor) ──── 1 kOhm ──── GPIO 24 ──── 2 kOhm ──── GND

   Der Trig-Pin verträgt direkt 3,3-V-Pegel vom Pi (kein Teiler nötig).


2. 1602 IIC LCD-Display --> Raspberry Pi 5
   +--------------------------+---------------------------+
   | LCD-Pin                  | Raspberry Pi 5            |
   +--------------------------+---------------------------+
   | VCC                      | Pin  4  (5 V)             |
   | GND                      | Pin  9  (GND)             |
   | SDA                      | Pin  3  (GPIO 2 / SDA1)   |
   | SCL                      | Pin  5  (GPIO 3 / SCL1)   |
   +--------------------------+---------------------------+


GPIO-PINBELEGUNG RASPBERRY PI 5 (Ausschnitt)
--------------------------------------------

        3,3 V [ 1][ 2] 5 V
 GPIO 2 SDA   [ 3][ 4] 5 V
 GPIO 3 SCL   [ 5][ 6] GND
 GPIO 4       [ 7][ 8] GPIO 14 TX
         GND  [ 9][10] GPIO 15 RX
 GPIO 17      [11][12] GPIO 18
 GPIO 27      [13][14] GND
 GPIO 22      [15][16] GPIO 23  <-- TRIG (Sensor)
        3,3 V [17][18] GPIO 24  <-- ECHO (Sensor)
 GPIO 10 MOSI [19][20] GND
 GPIO 9  MISO [21][22] GPIO 25
 GPIO 11 CLK  [23][24] GPIO 8  CE0
         GND  [25][26] GPIO 7  CE1


INSTALLATION
------------

Schritt 1 – I2C aktivieren
  sudo raspi-config
  --> Interface Options --> I2C --> Enable
  --> Reboot (sudo reboot)

Schritt 2 – I2C-Adresse des LCD ermitteln
  sudo apt install i2c-tools
  i2cdetect -y 1

  Die Adresse erscheint als zweistellige Hex-Zahl (z. B. "27" oder "3f").
  In main.py die Variable LCD_I2C_ADDR entsprechend setzen:
    LCD_I2C_ADDR = 0x27   (Standard)
    LCD_I2C_ADDR = 0x3F   (alternativ)

Schritt 3 – Abhängigkeiten installieren
  sudo apt update
  sudo apt install python3-lgpio
  pip install gpiozero lgpio smbus2

Schritt 4 – Programm starten
  python3 main.py


BEDIENUNG
---------
  - Zeile 1 des LCD zeigt dauerhaft "Entfernung:".
  - Zeile 2 zeigt die aktuelle Entfernung in cm (wird alle 0,5 s aktualisiert).
  - Mit Strg+C (SIGINT) wird das Programm sauber beendet und das Display
    gelöscht.


FEHLERBEHEBUNG
--------------
  Problem: LCD bleibt dunkel / zeigt keine Zeichen
    Lösung: Kontrast-Poti auf der Rückseite des I2C-Adapters drehen.

  Problem: I2C-Adresse wird von i2cdetect nicht erkannt
    Lösung: VCC- und GND-Verkabelung des LCD prüfen.

  Problem: Falscher Messwert oder kein Messwert vom Sensor
    Lösung: Echo-/Trig-Kabel tauschen oder Spannungsteiler am Echo-Pin
             prüfen.

  Problem: "ImportError: No module named gpiozero / smbus2"
    Lösung: pip install gpiozero lgpio smbus2 erneut ausführen.
             Sicherstellen, dass pip fuer Python 3 verwendet wird
             (pip3 install ...).

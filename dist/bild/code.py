#!/usr/bin/env python3
"""
Raspberry Pi 5 - Ultraschall-Entfernungsmessung mit HC-SR04
Anzeige auf 1602 I2C LCD Display

Verkabelung:
-----------
HC-SR04 Sensor:
  VCC  -> 5V (Pin 2 oder 4)
  GND  -> GND (Pin 6)
  TRIG -> GPIO 23 (Pin 16)
  ECHO -> GPIO 24 (Pin 18) *ueber Spannungsteiler!*
         (ECHO gibt 5V aus -> mit 1kΩ + 2kΩ Spannungsteiler auf 3.3V reduzieren)

1602 I2C LCD Display:
  VCC -> 5V (Pin 2 oder 4)
  GND -> GND (Pin 9 oder 14)
  SDA -> GPIO 2 / SDA (Pin 3)
  SCL -> GPIO 3 / SCL (Pin 5)

Hinweis: I2C muss aktiviert sein:
  sudo raspi-config -> Interface Options -> I2C -> Enable
"""

import time
import board
import busio
import digitalio
from adafruit_character_lcd.character_lcd_i2c import Character_LCD_I2C

# ============================================================
# Konfiguration
# ============================================================
TRIG_PIN = board.D23          # GPIO 23 fuer Trigger
ECHO_PIN = board.D24          # GPIO 24 fuer Echo
LCD_COLUMNS = 16              # 1602 = 16 Spalten
LCD_ROWS = 2                  # 1602 = 2 Zeilen
LCD_I2C_ADDR = 0x27           # Standard-Adresse (manchmal 0x3F)
MESS_INTERVALL = 0.5          # Sekunden zwischen Messungen
SCHALLGESCHWINDIGKEIT = 34300  # cm/s bei ~20°C

# ============================================================
# Hardware-Initialisierung
# ============================================================

# --- I2C & LCD ---
i2c = busio.I2C(board.SCL, board.SDA)
lcd = Character_LCD_I2C(i2c, LCD_COLUMNS, LCD_ROWS, address=LCD_I2C_ADDR)
lcd.backlight = True

# --- Ultraschall-Sensor (HC-SR04) ---
trig = digitalio.DigitalInOut(TRIG_PIN)
trig.direction = digitalio.Direction.OUTPUT
trig.value = False

echo = digitalio.DigitalInOut(ECHO_PIN)
echo.direction = digitalio.Direction.INPUT


def messe_entfernung():
    """Misst die Entfernung mit dem HC-SR04 Sensor.
    Gibt die Entfernung in cm zurueck oder -1 bei Timeout.
    Verwendet time.monotonic() fuer robuste Zeitmessung.
    """
    # Trigger-Puls senden (10µs HIGH)
    trig.value = True
    time.sleep(0.00001)  # 10 Mikrosekunden
    trig.value = False

    # Warten bis Echo HIGH wird (Start der Messung)
    timeout_start = time.monotonic()
    puls_start = timeout_start
    while not echo.value:
        puls_start = time.monotonic()
        if puls_start - timeout_start > 0.1:
            return -1

    # Warten bis Echo LOW wird (Ende der Messung)
    puls_ende = puls_start
    while echo.value:
        puls_ende = time.monotonic()
        if puls_ende - puls_start > 0.1:
            return -1

    # Entfernung berechnen
    puls_dauer = puls_ende - puls_start
    entfernung = (puls_dauer * SCHALLGESCHWINDIGKEIT) / 2

    return round(entfernung, 1)


def zeige_auf_lcd(entfernung):
    """Zeigt die Entfernung auf dem LCD-Display an."""
    lcd.clear()
    lcd.cursor_position(0, 0)
    lcd.message = "Entfernung:"

    lcd.cursor_position(0, 1)
    if entfernung < 0:
        lcd.message = "Kein Signal!"
    elif entfernung > 400:
        lcd.message = "Ausser Reichweite"
    else:
        lcd.message = f"{entfernung} cm"


def main():
    """Hauptprogramm - misst dauerhaft und zeigt auf LCD an."""
    print("=" * 40)
    print("Ultraschall-Entfernungsmessung")
    print("HC-SR04 + 1602 I2C LCD")
    print("Druecke Ctrl+C zum Beenden")
    print("=" * 40)

    # Begruessung auf LCD
    lcd.clear()
    lcd.message = "Entfernungs-\nmessung aktiv!"
    time.sleep(2)

    try:
        while True:
            entfernung = messe_entfernung()
            zeige_auf_lcd(entfernung)

            # Auch in der Konsole ausgeben
            if entfernung < 0:
                print("Messung: Kein Signal")
            else:
                print(f"Messung: {entfernung} cm")

            time.sleep(MESS_INTERVALL)

    except KeyboardInterrupt:
        print("\nProgramm beendet.")
        lcd.clear()
        lcd.message = "Programm\nbeendet!"
        time.sleep(1)
        lcd.clear()
        lcd.backlight = False


if __name__ == "__main__":
    main()

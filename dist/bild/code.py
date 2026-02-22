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
import lgpio
from RPLCD.i2c import CharLCD

# ============================================================
# Konfiguration
# ============================================================
TRIG_PIN = 23                 # GPIO 23 fuer Trigger
ECHO_PIN = 24                 # GPIO 24 fuer Echo
LCD_COLUMNS = 16              # 1602 = 16 Spalten
LCD_ROWS = 2                  # 1602 = 2 Zeilen
LCD_I2C_ADDR = 0x27           # Standard-Adresse (manchmal 0x3F)
MESS_INTERVALL = 0.5          # Sekunden zwischen Messungen
SCHALLGESCHWINDIGKEIT = 34300  # cm/s bei ~20°C

# ============================================================
# Hardware-Initialisierung
# ============================================================

# --- LCD (PCF8574-basiert) ---
lcd = CharLCD(i2c_expander='PCF8574', address=LCD_I2C_ADDR,
              port=1, cols=LCD_COLUMNS, rows=LCD_ROWS,
              dotsize=8, auto_linebreaks=True)
lcd.backlight_enabled = True

# --- GPIO (lgpio direkt) ---
h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, TRIG_PIN)
lgpio.gpio_claim_input(h, ECHO_PIN)


def messe_entfernung():
    """Misst die Entfernung mit dem HC-SR04 Sensor.
    Gibt die Entfernung in cm zurueck oder -1 bei Timeout.
    Verwendet time.monotonic() fuer robuste Zeitmessung.
    """
    # Trigger-Puls senden (10µs HIGH)
    lgpio.gpio_write(h, TRIG_PIN, 1)
    time.sleep(0.00001)  # 10 Mikrosekunden
    lgpio.gpio_write(h, TRIG_PIN, 0)

    # Warten bis Echo HIGH wird (Start der Messung)
    timeout_start = time.monotonic()
    puls_start = timeout_start
    while lgpio.gpio_read(h, ECHO_PIN) == 0:
        puls_start = time.monotonic()
        if puls_start - timeout_start > 0.1:
            return -1

    # Warten bis Echo LOW wird (Ende der Messung)
    puls_ende = puls_start
    while lgpio.gpio_read(h, ECHO_PIN) == 1:
        puls_ende = time.monotonic()
        if puls_ende - puls_start > 0.1:
            return -1

    # Entfernung berechnen
    puls_dauer = puls_ende - puls_start
    entfernung = (puls_dauer * SCHALLGESCHWINDIGKEIT) / 2

    return round(entfernung, 1)


def zeige_auf_lcd(entfernung):
    """Zeigt die Entfernung auf dem LCD-Display an.
    Ueberschreibt die Zeilen direkt (kein lcd.clear()),
    damit das Display nicht flackert/blinkt.
    """
    # Zeile 1: immer "Entfernung:"
    zeile1 = "Entfernung:".ljust(LCD_COLUMNS)

    # Zeile 2: Messwert
    if entfernung < 0:
        zeile2 = "Kein Signal!".ljust(LCD_COLUMNS)
    elif entfernung > 400:
        zeile2 = "Ausser Reichw.".ljust(LCD_COLUMNS)
    else:
        zeile2 = f"{entfernung} cm".ljust(LCD_COLUMNS)

    lcd.cursor_pos = (0, 0)
    lcd.write_string(zeile1)
    lcd.cursor_pos = (1, 0)
    lcd.write_string(zeile2)


def main():
    """Hauptprogramm - misst dauerhaft und zeigt auf LCD an."""
    print("=" * 40)
    print("Ultraschall-Entfernungsmessung")
    print("HC-SR04 + 1602 I2C LCD")
    print("Druecke Ctrl+C zum Beenden")
    print("=" * 40)

    # Begruessung auf LCD
    lcd.clear()
    lcd.write_string("Entfernungs-")
    lcd.cursor_pos = (1, 0)
    lcd.write_string("messung aktiv!")
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
        lcd.write_string("Programm")
        lcd.cursor_pos = (1, 0)
        lcd.write_string("beendet!")
        time.sleep(1)
        lcd.clear()
        lcd.backlight_enabled = False
        lgpio.gpiochip_close(h)


if __name__ == "__main__":
    main()

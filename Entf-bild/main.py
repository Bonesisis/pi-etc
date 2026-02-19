#!/usr/bin/env python3
"""
Entf-bild – Ultraschall-Entfernungsmessung mit 1602 IIC LCD-Anzeige
====================================================================
Für Raspberry Pi 5 mit Pi OS 64-bit

Sensor-Pins (Aufschrift auf dem Sensor):
  Echo / TX / SDA  →  GPIO 24  (Pin 18)
  Trig / RX / SCL  →  GPIO 23  (Pin 16)

1602 IIC LCD-Pins:
  SDA  →  GPIO 2  (Pin 3)
  SCL  →  GPIO 3  (Pin 5)

Abhängigkeiten installieren:
  sudo apt update
  sudo apt install python3-lgpio
  pip install gpiozero lgpio smbus2
"""

import time
from gpiozero import DistanceSensor
import smbus2

# ── Sensor-Einstellungen ──────────────────────────────────────────────────────
TRIG_PIN = 23   # GPIO-Pin für Trigger (Trig / RX / SCL des Sensors)
ECHO_PIN  = 24  # GPIO-Pin für Echo   (Echo / TX / SDA des Sensors)

# ── LCD-Einstellungen ─────────────────────────────────────────────────────────
LCD_I2C_ADDR = 0x27   # Standard-Adresse des PCF8574-Adapters; ggf. auf 0x3F ändern
LCD_I2C_BUS  = 1      # I2C-Bus 1  (SDA = GPIO 2, SCL = GPIO 3)


# ─────────────────────────────────────────────────────────────────────────────
# Einfacher LCD-Treiber für PCF8574-basiertes 1602-IIC-Display (4-Bit-Modus)
# ─────────────────────────────────────────────────────────────────────────────
class LCD1602IIC:
    """Steuert ein 1602-LCD über einen PCF8574-I2C-Adapter."""

    # PCF8574-Bit-Zuordnung
    RS = 0x01   # Register-Select
    E  = 0x04   # Enable
    BL = 0x08   # Hintergrundbeleuchtung
    D4 = 0x10
    D5 = 0x20
    D6 = 0x40
    D7 = 0x80

    def __init__(self, bus: smbus2.SMBus, addr: int = 0x27):
        self._bus  = bus
        self._addr = addr
        self._backlight = self.BL
        self._init_display()

    # ── interne Hilfsmethoden ──────────────────────────────────────────────────

    def _write_byte(self, data: int):
        self._bus.write_byte(self._addr, data | self._backlight)
        time.sleep(0.0001)

    def _pulse_enable(self, data: int):
        self._write_byte(data | self.E)
        time.sleep(0.0005)
        self._write_byte(data & ~self.E)
        time.sleep(0.0001)

    def _write_nibble(self, nibble: int, mode: int):
        """Sendet ein 4-Bit-Nibble; mode=0 → Befehl, mode=RS → Zeichen."""
        high = mode | (nibble & 0xF0)
        low  = mode | ((nibble << 4) & 0xF0)
        self._pulse_enable(high)
        self._pulse_enable(low)

    def _cmd(self, cmd: int):
        """Sendet einen LCD-Befehl."""
        self._write_nibble(cmd, 0)

    def _char(self, ch: int):
        """Sendet ein einzelnes Zeichen."""
        self._write_nibble(ch, self.RS)

    def _init_display(self):
        """Initialisiert das LCD im 4-Bit-Modus."""
        time.sleep(0.05)
        for _ in range(3):
            self._pulse_enable(0x30)
            time.sleep(0.005)
        self._pulse_enable(0x20)   # in den 4-Bit-Modus wechseln
        time.sleep(0.001)
        self._cmd(0x28)   # 2 Zeilen, 5×8 Punkte
        self._cmd(0x0C)   # Display an, Cursor aus
        self._cmd(0x06)   # Cursor nach rechts
        self.clear()

    # ── öffentliche Methoden ───────────────────────────────────────────────────

    def clear(self):
        """Löscht den Displayinhalt."""
        self._cmd(0x01)
        time.sleep(0.002)

    def set_cursor(self, row: int, col: int):
        """Setzt den Cursor auf Zeile row (0 oder 1) und Spalte col (0–15)."""
        offsets = [0x00, 0x40]
        self._cmd(0x80 | (offsets[row] + col))

    def print(self, text: str):
        """Schreibt einen Text an der aktuellen Cursor-Position."""
        for ch in text:
            self._char(ord(ch))


# ─────────────────────────────────────────────────────────────────────────────
# Hauptprogramm
# ─────────────────────────────────────────────────────────────────────────────
def main():
    # Ultraschallsensor initialisieren (max. Reichweite 4 m)
    sensor = DistanceSensor(echo=ECHO_PIN, trigger=TRIG_PIN, max_distance=4)

    with smbus2.SMBus(LCD_I2C_BUS) as bus:
        lcd = LCD1602IIC(bus, LCD_I2C_ADDR)

        # Überschrift in Zeile 1
        lcd.set_cursor(0, 0)
        lcd.print("Entfernung:     ")

        try:
            while True:
                distance_cm = sensor.distance * 100   # Meter → Zentimeter

                # Entfernung in Zeile 2 anzeigen (rechtsbündig, 1 Dezimalstelle)
                lcd.set_cursor(1, 0)
                lcd.print(f"{distance_cm:6.1f} cm    ")

                time.sleep(0.5)

        except KeyboardInterrupt:
            lcd.clear()
            lcd.set_cursor(0, 0)
            lcd.print("Programm beendet")
            time.sleep(1)
            lcd.clear()


if __name__ == "__main__":
    main()

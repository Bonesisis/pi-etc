@#!/bin/bash
# ============================================================
# Setup-Skript fuer Raspberry Pi 5
# Installiert alle nötigen Pakete fuer HC-SR04 + 1602 I2C LCD
# ============================================================

echo "=== Raspberry Pi Entfernungsmessung - Setup ==="
echo ""

# System updaten
echo "[1/4] System wird aktualisiert..."
sudo apt-get update -y
sudo apt-get upgrade -y

# I2C aktivieren (falls noch nicht geschehen)
echo "[2/4] I2C wird aktiviert..."
sudo raspi-config nonint do_i2c 0

# Python-Pakete installieren
echo "[3/4] Python-Pakete werden installiert..."
sudo apt-get install -y python3-pip python3-smbus i2c-tools
pip3 install --break-system-packages adafruit-blinka adafruit-circuitpython-charlcd

# I2C testen
echo "[4/4] I2C-Geraete werden gesucht..."
echo "Gefundene I2C-Adressen:"
i2cdetect -y 1

echo ""
echo "=== Setup abgeschlossen! ==="
echo "Starte das Programm mit: python3 code.py"
echo ""
echo "Falls das LCD nicht funktioniert:"
echo "  - Pruefe ob eine Adresse bei i2cdetect angezeigt wird"
echo "  - Falls 0x3F statt 0x27: Aendere LCD_I2C_ADDR in code.py"

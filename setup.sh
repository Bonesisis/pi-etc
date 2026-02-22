#!/usr/bin/env bash
# ============================================================
# Setup-Skript fuer Raspberry Pi 5
# Ultraschall-Entfernungsmessung (HC-SR04 + 1602 I2C LCD)
#
# Ausfuehren:  bash ~/pi-etc/setup.sh
# ============================================================
set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$REPO_DIR/.venv"

echo "============================================"
echo " Raspberry Pi 5 - Projekt-Setup"
echo "============================================"

# --- 1. Systempakete installieren ---
echo ""
echo "[1/4] Systempakete installieren ..."
sudo apt-get update -qq
sudo apt-get install -y \
    python3-full \
    python3-venv \
    python3-lgpio \
    python3-libgpiod \
    python3-smbus \
    i2c-tools

# --- 2. Virtuelle Umgebung anlegen (mit Zugriff auf System-Pakete) ---
echo ""
echo "[2/4] Virtuelle Umgebung in $VENV_DIR ..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv --system-site-packages "$VENV_DIR"
    echo "       -> Neu angelegt."
else
    echo "       -> Existiert bereits."
fi

# Aktivieren
source "$VENV_DIR/bin/activate"

# --- 3. Python-Pakete in der venv installieren ---
echo ""
echo "[3/4] Python-Pakete installieren ..."
python -m pip install --upgrade pip wheel setuptools -q
python -m pip install -r "$REPO_DIR/requirements.txt" -q

# --- 4. I2C pruefen ---
echo ""
echo "[4/4] I2C-Bus pruefen ..."
if command -v i2cdetect &> /dev/null; then
    echo "       i2cdetect -y 1:"
    i2cdetect -y 1 || echo "       (Fehler: I2C evtl. nicht aktiviert)"
else
    echo "       i2cdetect nicht gefunden."
fi

# --- Fertig ---
echo ""
echo "============================================"
echo " Setup abgeschlossen!"
echo ""
echo " Starten mit:"
echo "   cd $REPO_DIR"
echo "   source .venv/bin/activate"
echo "   python dist/bild/code.py"
echo "============================================"

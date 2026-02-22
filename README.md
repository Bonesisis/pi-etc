
# pi-etc – Raspberry Pi 5 Ultraschall + LCD

## Ersteinrichtung (einmalig)

```bash
sudo apt-get update && sudo apt-get install -y python3-full python3-venv python3-lgpio python3-libgpiod python3-smbus i2c-tools
```

I2C aktivieren (falls noch nicht aktiv):
```bash
sudo raspi-config nonint do_i2c 0
sudo reboot
```

## Update: alles neu laden

```bash
cd ~/pi-etc && git reset --hard HEAD && git clean -fd && git pull && rm -rf .venv && python3 -m venv --system-site-packages .venv && source .venv/bin/activate && pip install -U pip wheel setuptools && pip install RPLCD smbus2
```

## Nur starten

```bash
cd ~/pi-etc && source .venv/bin/activate && python dist/bild/code.py
```

## Update + direkt starten

```bash
cd ~/pi-etc && git reset --hard HEAD && git clean -fd && git pull && rm -rf .venv && python3 -m venv --system-site-packages .venv && source .venv/bin/activate && pip install -U pip wheel setuptools && pip install RPLCD smbus2 && python dist/bild/code.py
```
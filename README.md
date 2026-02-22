
für update und dann alt löschen neu laden 

cd ~/pi-etc && git reset --hard HEAD && git clean -fd && git pull && rm -rf .venv && python3 -m venv .venv && source .venv/bin/activate && python -m pip install -U pip wheel setuptools && python -m pip install adafruit-blinka adafruit-circuitpython-charlcd

nur starten
cd ~/pi-etc && source .venv/bin/activate && python dist/bild/code.py

für alt weg neu rein und direkt starten 
cd ~/pi-etc && git reset --hard HEAD && git clean -fd && git pull && rm -rf .venv && python3 -m venv .venv && source .venv/bin/activate && python -m pip install -U pip wheel setuptools && python -m pip install adafruit-blinka adafruit-circuitpython-charlcd && python dist/bild/code.py
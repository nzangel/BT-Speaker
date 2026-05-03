ARG BUILD_FROM=ghcr.io/home-assistant/base:latest
FROM ${BUILD_FROM}

# Paquets système : BlueZ + PulseAudio + Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    bluez \
    bluez-tools \
    pulseaudio \
    pulseaudio-module-bluetooth \
    python3 \
    python3-pip \
    python3-dbus \
    dbus \
    && rm -rf /var/lib/apt/lists/*

# Bibliothèques Python
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Code de l'add-on
COPY app/ /app/
COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/run.sh"]
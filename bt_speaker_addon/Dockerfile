ARG BUILD_FROM=ghcr.io/home-assistant/aarch64-base-debian:bookworm
FROM ${BUILD_FROM}

RUN apt-get update && apt-get install -y --no-install-recommends \
    bluez bluez-tools \
    pulseaudio pulseaudio-module-bluetooth \
    python3 python3-pip python3-dev \
    python3-dbus python3-gi python3-venv \
    dbus build-essential \
    libdbus-1-dev libglib2.0-dev \
    pkg-config gir1.2-glib-2.0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY app/ /app/

# run.sh placé dans /etc/services.d/bt-speaker/run (structure s6 v3)
COPY rootfs/ /
RUN chmod a+x /etc/services.d/bt-speaker/run \
    && chmod a+x /etc/services.d/bt-speaker/finish
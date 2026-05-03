ARG BUILD_FROM=ghcr.io/home-assistant/base:latest
FROM ${BUILD_FROM}

# Alpine utilise apk, pas apt-get
RUN apk add --no-cache \
    bluez \
    bluez-libs \
    pulseaudio \
    pulseaudio-bluez \
    python3 \
    py3-pip \
    py3-dbus \
    py3-gobject3 \
    dbus \
    gcc \
    musl-dev \
    dbus-dev \
    pkgconfig \
    glib-dev \
    python3-dev \
    libffi-dev

# Venv pour isoler les dépendances pip
RUN python3 -m venv /opt/venv --system-site-packages
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY app/ /app/
COPY rootfs/ /
RUN chmod a+x /etc/services.d/bt-speaker/run \
    && chmod a+x /etc/services.d/bt-speaker/finish
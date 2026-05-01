ARG BUILD_FROM=ghcr.io/home-assistant/aarch64-base-debian:bookworm
FROM ${BUILD_FROM}

# 1. Paquets système — tout ce qu'il faut pour compiler ET exécuter
RUN apt-get update && apt-get install -y --no-install-recommends \
    bluez \
    bluez-tools \
    pulseaudio \
    pulseaudio-module-bluetooth \
    python3 \
    python3-pip \
    python3-dev \
    python3-dbus \
    python3-gi \
    python3-venv \
    dbus \
    build-essential \
    libdbus-1-dev \
    libglib2.0-dev \
    pkg-config \
    gir1.2-glib-2.0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 2. Environnement virtuel — contourne le blocage pip de Debian Bookworm
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 3. Mise à jour pip dans le venv
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 4. Dépendances Python
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# 5. Code de l'add-on
COPY app/ /app/
COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/run.sh"]
#!/usr/bin/with-contenv bashio

# Lecture des options depuis l'UI HA
SPEAKER_MAC=$(bashio::config 'speaker_mac')
POLL_INTERVAL=$(bashio::config 'poll_interval')

# PulseAudio en mode système (nécessaire pour A2DP dans un conteneur)
mkdir -p /var/run/pulse
pulseaudio --system \
    --disallow-exit \
    --disallow-module-loading=false \
    --log-target=stderr \
    --exit-idle-time=-1 &

# Attendre que PulseAudio soit prêt
sleep 2

# Charger le module Bluetooth de PulseAudio
pactl load-module module-bluetooth-discover
pactl load-module module-bluetooth-policy

# Lancer l'API Python
SPEAKER_MAC="${SPEAKER_MAC}" \
POLL_INTERVAL="${POLL_INTERVAL}" \
python3 /app/main.py
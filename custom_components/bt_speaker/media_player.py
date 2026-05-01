from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature as Feature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .coordinator import BtSpeakerCoordinator

SUPPORTED_FEATURES = (
    Feature.PLAY | Feature.PAUSE
    | Feature.VOLUME_SET | Feature.VOLUME_STEP
    | Feature.TURN_OFF
)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    coordinator: BtSpeakerCoordinator = hass.data[DOMAIN][entry.entry_id]
    entity = BtSpeakerMediaPlayer(coordinator)
    async_add_entities([entity])
    # On stocke la ref de l'entité pour que __init__.py puisse
    # appeler ses méthodes depuis les handlers de service
    hass.data[DOMAIN]["entity"] = entity


class BtSpeakerMediaPlayer(CoordinatorEntity, MediaPlayerEntity):

    _attr_name = "BT Speaker"
    _attr_unique_id = "bt_speaker_player"
    _attr_supported_features = SUPPORTED_FEATURES

    def __init__(self, coordinator: BtSpeakerCoordinator):
        super().__init__(coordinator)
        self._volume = 0.5
        self._scanned_devices: list[dict] = []  # ← résultats du scan
        self._scanning = False

    # --- État ---

    @property
    def state(self) -> MediaPlayerState:
        if not self.coordinator.data:
            return MediaPlayerState.UNAVAILABLE
        if self.coordinator.data.get("connected"):
            return MediaPlayerState.IDLE
        return MediaPlayerState.OFF

    @property
    def volume_level(self) -> float:
        return self._volume

    @property
    def extra_state_attributes(self) -> dict:
        data = self.coordinator.data or {}
        return {
            "speaker_name":    data.get("name", "—"),
            "paired":          data.get("paired", False),
            "connected":       data.get("connected", False),
            # ↓ Nouveaux attributs pour le scan
            "scanning":        self._scanning,
            "scanned_devices": self._scanned_devices,
        }

    # --- Commandes media ---

    async def async_media_play(self):
        await self.coordinator.async_play()

    async def async_media_pause(self):
        await self.coordinator.async_pause()

    async def async_set_volume_level(self, volume: float):
        self._volume = volume
        await self.coordinator.async_set_volume(volume)
        self.async_write_ha_state()

    async def async_turn_off(self):
        await self.coordinator.async_disconnect()
        await self.coordinator.async_request_refresh()

    # --- Méthodes appelées par les services ---

    async def async_scan_devices(self, duration: int = 10):
        """Déclenche le scan et met à jour l'état en temps réel."""
        self._scanning = True
        self._scanned_devices = []
        self.async_write_ha_state()  # HA voit scanning=True immédiatement
        try:
            devices = await self.coordinator.async_scan(duration)
            self._scanned_devices = devices
        finally:
            self._scanning = False
            self.async_write_ha_state()  # HA voit les résultats

    async def async_connect_device(self, mac: str):
        """Connecte une enceinte par MAC et rafraîchit l'état."""
        await self.coordinator.async_connect(mac)
        await self.coordinator.async_request_refresh()
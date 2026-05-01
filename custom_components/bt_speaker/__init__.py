import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from .const import DOMAIN
from .coordinator import BtSpeakerCoordinator

PLATFORMS = ["media_player"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    coordinator = BtSpeakerCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Setup des entités (media_player.py stocke la ref dans hass.data)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # --- Enregistrement des services ---
    _register_services(hass)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    hass.data[DOMAIN].pop(entry.entry_id, None)
    hass.data[DOMAIN].pop("entity", None)
    hass.services.async_remove(DOMAIN, "scan")
    hass.services.async_remove(DOMAIN, "connect")
    hass.services.async_remove(DOMAIN, "disconnect")
    return True


def _register_services(hass: HomeAssistant):

    def _entity() -> "BtSpeakerMediaPlayer":
        return hass.data[DOMAIN].get("entity")

    # bt_speaker.scan
    async def handle_scan(call: ServiceCall):
        duration = call.data.get("duration", 10)
        entity = _entity()
        if entity:
            await entity.async_scan_devices(duration=duration)

    hass.services.async_register(
        DOMAIN, "scan", handle_scan,
        schema=vol.Schema({
            vol.Optional("duration", default=10): vol.All(
                int, vol.Range(min=5, max=30)
            )
        })
    )

    # bt_speaker.connect
    async def handle_connect(call: ServiceCall):
        mac = call.data.get("mac")
        entity = _entity()
        if entity and mac:
            await entity.async_connect_device(mac=mac)

    hass.services.async_register(
        DOMAIN, "connect", handle_connect,
        schema=vol.Schema({
            vol.Required("mac"): str
        })
    )

    # bt_speaker.disconnect
    async def handle_disconnect(call: ServiceCall):
        entity = _entity()
        if entity:
            await entity.async_turn_off()

    hass.services.async_register(
        DOMAIN, "disconnect", handle_disconnect,
        schema=vol.Schema({})
    )
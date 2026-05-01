from datetime import timedelta
import aiohttp
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN, SCAN_INTERVAL, CONF_HOST, CONF_PORT

class BtSpeakerCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, entry):
        self.host = entry.data[CONF_HOST]
        self.port = entry.data[CONF_PORT]
        self.base_url = f"http://{self.host}:{self.port}"
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )

    async def _async_update_data(self):
        try:
            async with aiohttp.ClientSession() as s:
                r = await s.get(f"{self.base_url}/status", timeout=5)
                return await r.json()
        except Exception as e:
            raise UpdateFailed(e)

    # --- Commandes exposées aux entités ---

    async def async_play(self):
        await self._post("/play")

    async def async_pause(self):
        await self._post("/pause")

    async def async_set_volume(self, volume: float):
        await self._post("/volume", {"volume": int(volume * 100)})

    async def async_connect(self, mac: str):
        await self._post("/connect", {"mac": mac})

    async def async_disconnect(self):
        await self._post("/disconnect")

    async def async_scan(self) -> list:
        async with aiohttp.ClientSession() as s:
            r = await s.get(f"{self.base_url}/scan", timeout=15)
            data = await r.json()
            return data.get("devices", [])

    async def _post(self, path, body=None):
        async with aiohttp.ClientSession() as s:
            await s.post(
                f"{self.base_url}{path}",
                json=body or {},
                timeout=5
            )
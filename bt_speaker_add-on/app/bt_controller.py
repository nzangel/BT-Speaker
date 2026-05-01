import asyncio
from dbus_fast.aio import MessageBus
from dbus_fast import BusType

# Interfaces BlueZ standard
BLUEZ_SERVICE    = "org.bluez"
ADAPTER_IFACE    = "org.bluez.Adapter1"
DEVICE_IFACE     = "org.bluez.Device1"
MEDIA_CTRL_IFACE = "org.bluez.MediaControl1"  # AVRCP
MEDIA_PLAY_IFACE = "org.bluez.MediaPlayer1"    # contrôle lecture

class BluetoothController:

    def __init__(self):
        self.bus = None
        self.adapter_path = "/org/bluez/hci0"
        self.device_path = None

    async def connect(self):
        # Connexion au dbus SYSTÈME (celui de l'hôte via host_dbus: true)
        self.bus = await MessageBus(bus_type=BusType.SYSTEM).connect()

    # --- Scan des appareils disponibles ---
    async def scan(self, duration: int = 10) -> list[dict]:
        adapter = await self._get_interface(
            self.adapter_path, ADAPTER_IFACE
        )
        await adapter.call_start_discovery()
        await asyncio.sleep(duration)
        await adapter.call_stop_discovery()
        return await self._list_devices()

    # --- Connexion à l'enceinte ---
    async def pair_and_connect(self, mac: str):
        # Le path dbus dérive de l'adresse MAC
        mac_path = mac.replace(":", "_").upper()
        self.device_path = f"/org/bluez/hci0/dev_{mac_path}"

        device = await self._get_interface(
            self.device_path, DEVICE_IFACE
        )
        props = await device.get_all()

        if not props.get("Paired", False):
            await device.call_pair()
            await asyncio.sleep(2)

        if not props.get("Connected", False):
            await device.call_connect()
            await asyncio.sleep(2)

    # --- Contrôle AVRCP (play/pause/volume) ---
    async def play(self):
        player = await self._get_media_player()
        await player.call_play()

    async def pause(self):
        player = await self._get_media_player()
        await player.call_pause()

    async def set_volume(self, volume: int):
        # Volume AVRCP : 0-127
        ctrl = await self._get_interface(
            self.device_path, MEDIA_CTRL_IFACE
        )
        await ctrl.set_volume(int(volume * 127 / 100))

    async def get_status(self) -> dict:
        if not self.device_path:
            return {"connected": False}
        try:
            device = await self._get_interface(
                self.device_path, DEVICE_IFACE
            )
            props = await device.get_all()
            return {
                "connected": props.get("Connected", False),
                "name":      props.get("Name", ""),
                "paired":    props.get("Paired", False),
            }
        except Exception:
            return {"connected": False}

    # --- Helpers internes ---
    async def _get_interface(self, path, iface):
        obj = await self.bus.get_proxy_object(
            BLUEZ_SERVICE, path,
            await self.bus.introspect(BLUEZ_SERVICE, path)
        )
        return obj.get_interface(iface)

    async def _get_media_player(self):
        # Le MediaPlayer1 est un enfant du device
        return await self._get_interface(
            self.device_path + "/player0",
            MEDIA_PLAY_IFACE
        )

    async def _list_devices(self) -> list[dict]:
        # Parcourt ObjectManager pour lister les devices BT
        mgr_obj = await self.bus.get_proxy_object(
            BLUEZ_SERVICE, "/",
            await self.bus.introspect(BLUEZ_SERVICE, "/")
        )
        mgr = mgr_obj.get_interface("org.freedesktop.DBus.ObjectManager")
        objects = await mgr.call_get_managed_objects()
        return [
            {"mac": v[DEVICE_IFACE]["Address"].value,
             "name": v[DEVICE_IFACE].get("Name", {}).value or "?"}
            for path, v in objects.items()
            if DEVICE_IFACE in v
        ]
import asyncio, os, json
from aiohttp import web
from bt_controller import BluetoothController

bt = BluetoothController()

# --- Handlers ---

async def handle_status(req):
    status = await bt.get_status()
    return web.json_response(status)

async def handle_scan(req):
    devices = await bt.scan(duration=10)
    return web.json_response({"devices": devices})

async def handle_connect(req):
    data = await req.json()
    mac = data.get("mac")
    if not mac:
        return web.json_response(
            {"error": "mac required"}, status=400
        )
    await bt.pair_and_connect(mac)
    return web.json_response({"ok": True})

async def handle_disconnect(req):
    await bt.disconnect()
    return web.json_response({"ok": True})

async def handle_play(req):
    await bt.play()
    return web.json_response({"ok": True})

async def handle_pause(req):
    await bt.pause()
    return web.json_response({"ok": True})

async def handle_volume(req):
    data = await req.json()
    vol = int(data.get("volume", 50))
    await bt.set_volume(max(0, min(100, vol)))
    return web.json_response({"ok": True})

# --- Startup ---

async def on_startup(app):
    await bt.connect()
    # Auto-connexion si MAC configurée
    mac = os.getenv("SPEAKER_MAC", "")
    if mac:
        try:
            await bt.pair_and_connect(mac)
        except Exception as e:
            print(f"Auto-connect failed: {e}")

# --- App & routes ---

app = web.Application()
app.on_startup.append(on_startup)
app.router.add_get( "/status",     handle_status)
app.router.add_get( "/scan",       handle_scan)
app.router.add_post("/connect",    handle_connect)
app.router.add_post("/disconnect", handle_disconnect)
app.router.add_post("/play",       handle_play)
app.router.add_post("/pause",      handle_pause)
app.router.add_post("/volume",     handle_volume)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8765)
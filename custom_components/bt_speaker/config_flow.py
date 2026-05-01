import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_HOST, CONF_PORT, DEFAULT_HOST, DEFAULT_PORT

class BtSpeakerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Vérifier que l'add-on répond
            try:
                import aiohttp
                async with aiohttp.ClientSession() as s:
                    url = (
                        f"http://{user_input[CONF_HOST]}"
                        f":{user_input[CONF_PORT]}/status"
                    )
                    await s.get(url, timeout=3)
                return self.async_create_entry(
                    title="BT Speaker", data=user_input
                )
            except Exception:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            errors=errors,
            data_schema=vol.Schema({
                vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
            })
        )
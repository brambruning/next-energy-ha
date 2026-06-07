from __future__ import annotations

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import DOMAIN
from .coordinator import NextEnergyCoordinator


class NextEnergyConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> ConfigFlowResult:
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        errors: dict[str, str] = {}

        if user_input is not None:
            coordinator = NextEnergyCoordinator(self.hass)
            try:
                await coordinator._fetch_prices()
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title="Next Energy", data={})

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            errors=errors,
            description_placeholders={},
        )

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN, DEFAULT_NAME, DEFAULT_TIMEOUT, CONF_NAME, CONF_ENTITY_ID, CONF_TIMEOUT

class SleepTimerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SleepTimer."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Check if the entity ID is valid
            if not await self._validate_entity_id(user_input[CONF_ENTITY_ID]):
                errors["base"] = "invalid_entity_id"
            else:
                return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        # Show the configuration form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_ENTITY_ID): str,
                vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): vol.All(int, vol.Range(min=1)),
            }),
            errors=errors,
        )

    async def _validate_entity_id(self, entity_id):
        """Validate that the entity ID exists."""
        return self.hass.states.get(entity_id) is not None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return SleepTimerOptionsFlow(config_entry)

class SleepTimerOptionsFlow(config_entries.OptionsFlow):
    """Handle an options flow for SleepTimer."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(CONF_TIMEOUT, default=self.config_entry.options.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)): vol.All(int, vol.Range(min=1)),
            }),
        )
import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.event import async_call_later
from .const import DOMAIN, CONF_NAME, CONF_ENTITY_ID, CONF_TIMEOUT

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the SleepTimer switch from a config entry."""
    name = config_entry.data[CONF_NAME]
    entity_id = config_entry.data[CONF_ENTITY_ID]
    timeout = config_entry.data.get(CONF_TIMEOUT, 600)

    async_add_entities([SleepTimerSwitch(hass, name, entity_id, timeout)])

class SleepTimerSwitch(SwitchEntity):
    """Representation of a SleepTimer switch."""

    def __init__(self, hass, name, entity_id, timeout):
        """Initialize the switch."""
        self._hass = hass
        self._name = name
        self._entity_id = entity_id
        self._timeout = timeout
        self._is_on = False
        self._timer = None

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Turn on the switch and start the timer."""
        self._is_on = True
        self.async_write_ha_state()

        # Turn on the target entity
        await self._hass.services.async_call("switch", "turn_on", {"entity_id": self._entity_id})

        # Start the timer
        self._timer = async_call_later(self._hass, self._timeout, self._handle_timeout)

    async def async_turn_off(self, **kwargs):
        """Turn off the switch and cancel the timer."""
        self._is_on = False
        self.async_write_ha_state()

        # Turn off the target entity
        await self._hass.services.async_call("switch", "turn_off", {"entity_id": self._entity_id})

        # Cancel the timer
        if self._timer:
            self._timer()
            self._timer = None

    async def _handle_timeout(self, _now):
        """Handle the timeout."""
        self._is_on = False
        self.async_write_ha_state()

        # Turn off the target entity
        await self._hass.services.async_call("switch", "turn_off", {"entity_id": self._entity_id})

        # Clear the timer
        self._timer = None
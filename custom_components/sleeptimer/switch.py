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

    # Generate a unique ID based on the name
    unique_id = f"sleeptimer_{name.lower().replace(' ', '_')}"

    async_add_entities([SleepTimerSwitch(hass, name, entity_id, timeout, unique_id)])

class SleepTimerSwitch(SwitchEntity):
    """Representation of a SleepTimer switch."""

    def __init__(self, hass, name, entity_id, timeout, unique_id):
        """Initialize the switch."""
        self._hass = hass
        self._name = name
        self._entity_id = entity_id
        self._timeout = timeout
        self._is_on = False
        self._timer = None
        self._unique_id = unique_id

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self._is_on

    @property
    def unique_id(self):
        """Return a unique ID for the switch."""
        return self._unique_id

    async def async_turn_on(self, **kwargs):
        """Turn on the switch and start the timer."""
        self._is_on = True
        self.async_write_ha_state()

        await self._hass.services.async_call(
            "homeassistant",
            "turn_on",
            {"entity_id": self._entity_id},
            blocking=True,
        )

        # Start the timer
        self._timer = async_call_later(self._hass, self._timeout, self._handle_timeout)

    async def async_turn_off(self, **kwargs):
        """Turn off the switch and cancel the timer."""
        self._is_on = False
        self.async_write_ha_state()

        await self._hass.services.async_call(
            "homeassistant",
            "turn_off",
            {"entity_id": self._entity_id},
            blocking=True,
        )

        # Cancel the timer
        if self._timer:
            self._timer()
            self._timer = None

    async def _handle_timeout(self, _now):
        """Handle the timeout."""
        self._is_on = False
        self.async_write_ha_state()

        await self._hass.services.async_call(
            "homeassistant",
            "turn_off",
            {"entity_id": self._entity_id},
            blocking=True,
        )

        # Clear the timer
        self._timer = None
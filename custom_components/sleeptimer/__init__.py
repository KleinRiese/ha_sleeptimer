from .const import DOMAIN

async def async_setup_entry(hass, config_entry):
    """Set up SleepTimer from a config entry."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config_entry, "switch")
    )
    return True

async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    await hass.config_entries.async_forward_entry_unload(config_entry, "switch")
    return True
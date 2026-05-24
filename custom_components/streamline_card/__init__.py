"""Component to expose streamline_card templates from configuration.yaml."""
from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import CONF_TEMPLATES, DOMAIN

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_TEMPLATES, default={}): vol.Schema(
                    {cv.string: vol.Schema({}, extra=vol.ALLOW_EXTRA)}
                )
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/templates"})
@websocket_api.async_response
async def handle_templates(hass, connection, msg):
    """Return templates defined in configuration.yaml."""
    templates = hass.data.get(DOMAIN, {})
    connection.send_result(msg["id"], {"templates": templates})


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Streamline Card component."""
    try:
        templates = config.get(DOMAIN, {}).get(CONF_TEMPLATES, {})
        if not isinstance(templates, dict):
            _LOGGER.warning(
                "streamline_card.templates must be a dictionary, got %s",
                type(templates).__name__,
            )
            templates = {}
    except Exception as err:
        _LOGGER.warning("Error loading streamline_card templates: %s", err)
        templates = {}

    hass.data[DOMAIN] = templates
    websocket_api.async_register_command(hass, handle_templates)
    return True

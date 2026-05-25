"""Component to expose streamline_card templates from configuration.yaml."""
from __future__ import annotations

import logging
import os

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {cv.string: vol.Schema({}, extra=vol.ALLOW_EXTRA)}
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
        templates = config.get(DOMAIN, {})
        if not isinstance(templates, dict):
            _LOGGER.warning(
                "streamline_card must be a dictionary, got %s",
                type(templates).__name__,
            )
            templates = {}
        else:
            _LOGGER.debug(
                "Loaded %d streamline_card templates from configuration.yaml",
                len(templates),
            )
    except Exception as err:
        _LOGGER.warning("Error loading streamline_card templates: %s", err)
        templates = {}

    hass.data[DOMAIN] = templates
    websocket_api.async_register_command(hass, handle_templates)

    www_dir = os.path.join(os.path.dirname(__file__), "www")
    if os.path.isdir(www_dir):
        hass.http.register_static_path(
            f"/{DOMAIN}/static",
            www_dir,
            cache_headers=False,
        )
        _LOGGER.debug(
            "Registered static path /%s/static -> %s",
            DOMAIN,
            www_dir,
        )
    else:
        _LOGGER.warning("www directory not found at %s", www_dir)

    _LOGGER.debug(
        "streamline_card component setup complete, registered WS API: %s/templates",
        DOMAIN,
    )
    return True

__all__ = ["GpioDigitalOutput"]

import asyncio
from typing import Dict, Any, List

import gpiozero  # type: ignore

from yaqd_core import DiscreteHardware

from .__version__ import __branch__


class GpioDigitalOutput(DiscreteHardware):
    _kind = "gpio-digital-output"

    def __init__(self, name, config, config_filepath):
        super().__init__(name, config, config_filepath)
        self._controller = gpiozero.DigitalOutputDevice(pin=config["index"])
        self._position_identifiers = {"low": 0, "high": 1}

    def _connection_lost(self, peername):
        super()._connection_lost(peername)
        if len(self._clients) == 0:
            self._controller.value = 0

    def _set_position(self, value):
        self._controller.value = value

    async def update_state(self):
        while True:
            self._state["position"] = self._controller.value
            if self._state["position"]:
                self._state["position_identifier"] = "high"
            else:
                self._state["position_identifier"] = "low"
            self._busy = False
            await self._busy_sig.wait()

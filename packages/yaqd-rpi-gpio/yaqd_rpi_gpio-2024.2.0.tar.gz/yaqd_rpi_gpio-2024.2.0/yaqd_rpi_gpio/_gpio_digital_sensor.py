__all__ = ["GpioDigitalSensor"]

import asyncio
from typing import Dict, Any, List

import gpiozero  # type: ignore

from yaqd_core import Sensor

from .__version__ import __branch__


class GpioDigitalSensor(Sensor):
    _kind = "gpio-digital-sensor"

    def __init__(self, name, config, config_filepath):
        super().__init__(name, config, config_filepath)
        self._channel_names = config["channels"].keys()
        self._channel_units = {k: None for k in self._channel_names}
        self._controllers = []
        for name in self._channel_names:
            pin = config["channels"][name]["pin"]
            pull_up = config["channels"][name].get("pull_up", False)
            dev = gpiozero.InputDevice(pin=pin, pull_up=pull_up)
            self._controllers.append(dev)

    async def _measure(self):
        out = dict()
        for name, controller in zip(self._channel_names, self._controllers):
            out[name] = controller.value
        return out

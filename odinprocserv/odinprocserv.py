import asyncio
import logging
from typing import List

from aioca import caput

START_DELAY = 3


class OdinProcServConfig:
    def __init__(
        self,
        prefix,
        process_count,
        server_process_name,
        server_delay,
        ioc_name,
        ioc_delay,
    ) -> None:
        self.prefix = prefix
        self.process_count = process_count
        self.server_process_name = server_process_name
        self.server_delay = server_delay
        self.ioc_name = ioc_name
        self.ioc_delay = ioc_delay

    def __repr__(self) -> str:
        return "{}({})".format(self.__class__.__name__, self.__dict__)


class OdinProcServControl:
    def __init__(self, config: OdinProcServConfig, builder, log_level: str) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(log_level)

        self.config = config
        self._logger.debug("Config: %s", self.config)

        processes = range(1, config.process_count + 1)
        self.process_names = [
            self._format_process_name(config.prefix, number) for number in processes
        ]
        self._logger.debug("Processes: %s", ", ".join(self.process_names))
        # Remove server so we can control it separately
        self.process_names.remove(config.server_process_name)

        # Records
        self.start = builder.longOut("START", on_update=self.start)
        self.stop = builder.longOut("STOP", on_update=self.stop)
        self.restart = builder.longOut("RESTART", on_update=self.restart)

    async def start(self, value) -> None:
        if value:
            await self._start()
            self.start.set(0)

    async def _start(self) -> None:
        self._logger.info("Start called")
        await self._press_buttons(self.process_names, "START")
        self._logger.info("Started processes")

        await asyncio.sleep(self.config.server_delay)
        await self._press_buttons([self.config.server_process_name], "START")
        self._logger.info("Started Odin Server")

        await asyncio.sleep(self.config.ioc_delay)
        await self._press_buttons([self.config.ioc_name], "START")
        self._logger.info("Started ADOdin IOC")

    async def stop(self, value) -> None:
        if value:
            await self._stop()
            self.stop.set(0)

    async def _stop(self):
        self._logger.info("Stop called")
        await self._press_buttons(
            self.process_names
            + [self.config.server_process_name, self.config.ioc_name],
            "STOP",
        )

    async def restart(self, value) -> None:
        if value:
            await self._restart()
            self.restart.set(0)

    async def _restart(self) -> None:
        self._logger.info("Restart called")
        await self._stop()
        await asyncio.sleep(START_DELAY)
        await self._start()

    async def _press_buttons(self, button_prefixes: List[str], button_suffix: str) -> None:
        buttons = ["{}:{}".format(name, button_suffix) for name in button_prefixes]
        self._logger.info("Pressing buttons: %s", buttons[0])
        self._logger.info("caput(%s, 1)", buttons)
        await caput(buttons, 1)
        self._logger.info("Caput complete")

    @staticmethod
    def _format_process_name(prefix: str, process_number: int) -> str:
        if not prefix.endswith("-"):
            prefix += "-"
        return "{}{:02d}".format(prefix, process_number)

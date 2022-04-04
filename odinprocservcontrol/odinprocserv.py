from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Union

from aioca import caput
from softioc import builder

RESTART_DELAY = 3


@dataclass
class OdinProcServConfig:
    """OdinProcServControl configuration options

    args:
        prefix: Prefix for PVs - e.g. BLXXY-CS-ODN-01
        process_count: Total number of odin processes
        server_process_name: Name of odin server process - e.g. BLXXY-EA-ODN-11
        server_delay: Delay before starting server
        ioc_name: Name of ADOdin IOC - e.g. BLXXY-EA-IOC-03
        ioc_delay: Delay before starting IOC
    """

    prefix: str
    process_count: int
    server_process_name: str
    server_delay: Union[int, float]
    ioc_name: str
    ioc_delay: Union[int, float]


class OdinProcServControl:
    """Control of start, stop and restart of odin processes via PVs

    args:
        config: Configuration options
        log_level: Logging level - e.g. DEBUG
    """

    def __init__(self, config: OdinProcServConfig, log_level: str) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(log_level)

        self.config = config
        self._logger.debug("Config: %s", self.config)

        processes = range(1, config.process_count + 1)
        self.data_process_names = [
            self._format_process_name(config.prefix, number) for number in processes
        ]
        self.data_process_names.remove(config.server_process_name)
        self._logger.debug(
            "OdinProcServ Targets:\nData processes: %s\nServer: %s\nIOC: %s",
            ", ".join(self.data_process_names),
            self.config.server_process_name,
            self.config.ioc_name,
        )

        # Records
        self.start = builder.longOut("START", on_update=self.start_processes)
        self.stop = builder.longOut("STOP", on_update=self.stop_processes)
        self.restart = builder.longOut("RESTART", on_update=self.restart_processes)

    async def start_processes(self, value: int) -> None:
        """If button pressed, call _start and then release the button"""
        if value:
            await self._start_processes()
            self.start.set(0)

    async def _start_processes(self) -> None:
        """Start processes in the correct order with appropriate delays

        The logic is as follows:
            - Start all data processes
            - Wait for server delay time
            - Start server
            - Wait for IOC delay time
            - Start IOC

        """
        self._logger.info("Start called")
        await self._press_buttons(self.data_process_names, "START")
        self._logger.info("Started data processes")

        await asyncio.sleep(self.config.server_delay)
        await self._press_buttons([self.config.server_process_name], "START")
        self._logger.info("Started server")

        await asyncio.sleep(self.config.ioc_delay)
        await self._press_buttons([self.config.ioc_name], "START")
        self._logger.info("Started ADOdin IOC")

        # Stop will have toggled autorestart off - toggle it back on
        await self._press_buttons(
            self.data_process_names
            + [self.config.server_process_name, self.config.ioc_name],
            "TOGGLE",
        )

        self._logger.debug("Restart complete")

    async def stop_processes(self, value: int) -> None:
        """If button pressed, call _stop and then release the button"""
        if value:
            await self._stop_processes()
            self.stop.set(0)

    async def _stop_processes(self):
        """Stop all processes"""
        self._logger.info("Stop called")
        await self._press_buttons(
            self.data_process_names
            + [self.config.server_process_name, self.config.ioc_name],
            "STOP",
        )

        self._logger.debug("Stop complete")

    async def restart_processes(self, value: int) -> None:
        """If button pressed, call _restart and then release the button"""
        if value:
            await self._restart_processes()
            self.restart.set(0)

    async def _restart_processes(self) -> None:
        """Restart processes by directly calling _stop and then _start"""
        self._logger.info("Restart called")
        await self._stop_processes()
        await asyncio.sleep(RESTART_DELAY)
        await self._start_processes()

        self._logger.debug("Restart complete")

    async def _press_buttons(
        self, button_prefixes: list[str], button_suffix: str
    ) -> None:
        """Press buttons corresponding to the given suffix for all prefixes

        In this context, press means caput(..., 1)

        args:
            button_prefixes: A list of PV prefixes to press the given button_suffix on
                Note: The separating `:` will be added
            button_suffix: The button to press on the given `button_prefixes`

        """
        buttons = ["{}:{}".format(name, button_suffix) for name in button_prefixes]
        self._logger.debug("caput(%s, 1)", buttons)
        await caput(buttons, 1)
        self._logger.debug("Caput complete")

    @staticmethod
    def _format_process_name(prefix: str, process_number: int) -> str:
        """Format a valid DLS process name from a prefix and a number

        args:
            prefix: Process prefix including first three elements of the process name
                e.g. BLXXY-EA-EIG1
            process_number: The number of the process, i.e. the fourth element of the
                process name. This will be padded to width 2, but can also be 3 digits
                or more

        """
        if not prefix.endswith("-"):
            prefix += "-"
        return "{}{:02d}".format(prefix, process_number)

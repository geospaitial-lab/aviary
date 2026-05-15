#  Copyright (C) 2026 Marius Maryniak
#
#  This file is part of aviary.
#
#  aviary is free software: you can redistribute it and/or modify it under the terms of the
#  GNU General Public License as published by the Free Software Foundation,
#  either version 3 of the License, or (at your option) any later version.
#
#  aviary is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with aviary.
#  If not, see <https://www.gnu.org/licenses/>.

from typing import Any

from loguru import logger

from aviary.core.enums import LogLevel
from aviary.core.mixins import IDMixin


class Logger(IDMixin):
    """Logger"""

    def __init__(
        self,
        sink: Any,  # noqa: ANN401
        level: LogLevel = LogLevel.INFO,
        format: str = '{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {message}',  # noqa: A002
    ) -> None:
        """
        Parameters:
            sink: Sink
            level: Log level
            format: Format
        """
        self._sink = sink
        self._level = level
        self._format = format

        self._logger = logger

        self._logger.remove()
        self._logger.add(
            sink=self._sink,
            level=self._level,
            format=self._format,
        )
        self._logger.enable(name='aviary')

        super().__init__()

    def add_handler(
        self,
        sink: Any,  # noqa: ANN401
        level: LogLevel = LogLevel.INFO,
        format: str = '{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {message}',  # noqa: A002
    ) -> None:
        """Adds a handler to the logger.

        Parameters:
            sink: Sink
            level: Log level
            format: Format
        """
        self._logger.add(
            sink=sink,
            level=level,
            format=format,
        )

    def disable(self) -> None:
        """Disables the logger."""
        self._logger.disable(name='aviary')

    def enable(self) -> None:
        """Enables the logger."""
        self._logger.enable(name='aviary')

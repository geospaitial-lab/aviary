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

import json
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
        serialize: bool = False,
        format: str = '{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {message}',  # noqa: A002
    ) -> None:
        """
        Parameters:
            sink: Sink
            level: Log level
            serialize: If True, the logs are serialized to JSON format
            format: Format
        """
        self._sink = sink
        self._level = level
        self._serialize = serialize
        self._format = format

        self._logger = logger

        self._logger.remove()

        if self._sink is not None:
            if self._serialize:
                def serializer(record: dict[str, object]) -> str:
                    subset = {
                        'timestamp': record['time'].isoformat(),
                        'level': record['level'].name,
                        'message': record['message'],
                    }
                    if record['extra']:
                        subset.update(record['extra'])
                    return json.dumps(subset).replace('{', '{{').replace('}', '}}') + '\n'

                self._logger.add(
                    sink=self._sink,
                    level=self._level.to_loguru(),
                    format=serializer,
                )
            else:
                self._logger.add(
                    sink=self._sink,
                    level=self._level.to_loguru(),
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
            level=level.to_loguru(),
            format=format,
        )

    def disable(self) -> None:
        """Disables the logger."""
        self._logger.disable(name='aviary')

    def enable(self) -> None:
        """Enables the logger."""
        self._logger.enable(name='aviary')

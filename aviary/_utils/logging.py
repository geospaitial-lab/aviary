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

from __future__ import annotations

import time
from functools import wraps
from typing import (
    Any,
    TypeVar,
)

from loguru import logger

T = TypeVar('T', bound=type)


def _get_name(
    obj: object,
) -> str:
    module = obj.__module__
    qualname = obj.__qualname__

    if module is not None and module != '__main__':
        return f'{module}.{qualname}'

    return qualname


def _get_log(
    obj: object,
) -> str:
    if hasattr(obj, '_log'):
        return obj._log()  # noqa: SLF001

    return str(obj)


def _wrap_with_logging(
    cls: T,
    *,
    name: str,
) -> T:
    init = cls.__init__

    @wraps(init)
    def new_init(
        self: object,
        *args: Any,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        init(self, *args, **kwargs)

        logger.debug(
            'Initialized {}[{}]...',
            name,
            str(self.id)[:8],
        )

    cls.__init__ = new_init

    if callable(cls):
        call = cls.__call__

        @wraps(call)
        def new_call(
            self: object,
            *args: Any,  # noqa: ANN401
            **kwargs: Any,  # noqa: ANN401
        ) -> Any:  # noqa: ANN401
            logger.trace(
                'Calling {}[{}]...',
                name,
                str(self.id)[:8],
            )

            start_time = time.perf_counter()
            result = call(self, *args, **kwargs)
            elapsed_time = time.perf_counter() - start_time

            logger.trace(
                'Done with {}[{}] in {:.3f} s: {}',
                name,
                str(self.id)[:8],
                elapsed_time,
                _get_log(result),
            )

            return result

        cls.__call__ = new_call

    return cls


def log(
    cls: T,
) -> T:
    """Logs during initialization on debug level and on call on trace level.

    Parameters:
        cls: Class

    Returns:
        Decorator
    """
    name = _get_name(cls)

    return _wrap_with_logging(
        cls,
        name=name,
    )

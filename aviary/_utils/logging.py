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
    cls = obj if isinstance(obj, type) else obj.__class__
    qualname = cls.__qualname__

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
) -> T:
    init = cls.__init__

    @wraps(init)
    def new_init(
        self: object,
        *args: Any,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        init(self, *args, **kwargs)

        name = _get_name(self)

        logger.bind(
            component=name,
            id=str(self.id),
        ).debug(
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
            name = _get_name(self)

            if args:
                input_ = args[0]
            elif kwargs:
                input_ = next(iter(kwargs.values()))
            else:
                input_ = None

            logger.bind(
                component=name,
                id=str(self.id),
                input=_get_log(input_),
            ).trace(
                'Calling {}[{}] with {}...',
                name,
                str(self.id)[:8],
                _get_log(input_),
            )

            start_time = time.perf_counter()
            output = call(self, *args, **kwargs)
            duration = time.perf_counter() - start_time

            logger.bind(
                component=name,
                id=str(self.id),
                duration=duration,
                output=_get_log(output),
            ).trace(
                'Done with {}[{}] in {:.3f} s: {}',
                name,
                str(self.id)[:8],
                duration,
                _get_log(output),
            )

            return output

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
    return _wrap_with_logging(cls)

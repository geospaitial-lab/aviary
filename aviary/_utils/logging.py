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

import inspect
from functools import wraps
from typing import (
    TYPE_CHECKING,
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


def _wrap_with_logging(
    cls: T,
    *,
    name: str,
) -> T:
    orig_init = cls.__init__

    @wraps(orig_init)
    def new_init(
        self: Any,  # noqa: ANN401
        *args: Any,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        orig_init(self, *args, **kwargs)

        params = inspect.signature(orig_init).bind_partial(self, *args, **kwargs).arguments
        params.pop('self', None)

        if params:
            logger.debug(f'Initializing {name}[{self.id}] with {params}...')
        else:
            logger.debug(f'Initializing {name}[{self.id}]...')

    cls.__init__ = new_init

    if hasattr(cls, '__call__'):
        orig_call = cls.__call__

        @wraps(orig_call)
        def new_call(
            self: Any,  # noqa: ANN401
            *args: Any,  # noqa: ANN401
            **kwargs: Any,  # noqa: ANN401
        ) -> Any:  # noqa: ANN401
            logger.trace(f'Calling {name}[{self.id}]...')
            return orig_call(self, *args, **kwargs)

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

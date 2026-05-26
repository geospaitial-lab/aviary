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
import warnings
from functools import wraps
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
)

if TYPE_CHECKING:
    from collections.abc import Callable

from aviary.core.warnings import (
    AviaryDeprecationWarning,
    AviaryExperimentalWarning,
)

T = TypeVar('T')


def _get_message(
    obj: object,
    *,
    message_type: str,
    since: str | None = None,
    removal: str | None = None,
    description: str | None = None,
) -> str:
    module = obj.__module__
    qualname = obj.__qualname__

    if module is not None and module != '__main__':  # noqa: SIM108
        name = f'{module}.{qualname}'
    else:
        name = qualname

    since = f' since {since}' if since is not None else ''
    description = f' {description}' if description is not None else ''

    if message_type == 'experimental':
        base = f'{name} is experimental{since} and may change without notice.'
    elif message_type == 'deprecated':
        until = f' and will be removed in {removal}' if removal else ''
        base = f'{name} is deprecated{since}{until}.'
    else:
        message = 'Invalid message type!'
        raise ValueError(message)

    return f'{base}{description}'


def _wrap_with_warning(
    obj: T,
    *,
    message_type: str,
    category: Warning,
    since: str | None = None,
    removal: str | None = None,
    description: str | None = None,
    set_flag: str | None = None,
) -> T:
    if inspect.isclass(obj):
        if set_flag:
            setattr(obj, set_flag, True)

        init = obj.__init__

        @wraps(init)
        def new_init(
            self: object,
            *args: Any,  # noqa: ANN401
            **kwargs: Any,  # noqa: ANN401
        ) -> Callable:
            message = _get_message(
                obj=obj,
                message_type=message_type,
                since=since,
                removal=removal,
                description=description,
            )
            warnings.warn(message, category=category, stacklevel=2)
            return init(self, *args, **kwargs)

        obj.__init__ = new_init
        return obj

    @wraps(obj)
    def wrapper(
        *args: Any,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> Callable:
        message = _get_message(
            obj=obj,
            message_type=message_type,
            since=since,
            removal=removal,
            description=description,
        )
        warnings.warn(message, category=category, stacklevel=2)
        return obj(*args, **kwargs)

    return wrapper


def deprecated(
    *,
    since: str | None = None,
    removal: str | None = None,
    description: str | None = None,
) -> Callable:
    """Marks an object as deprecated.

    Parameters:
        since: Version since which the object is deprecated
        removal: Version when the object will be removed
        description: Description

    Returns:
        Decorator
    """
    def decorator(
        obj: T,
    ) -> T:
        return _wrap_with_warning(
            obj=obj,
            message_type='deprecated',
            category=AviaryDeprecationWarning,
            since=since,
            removal=removal,
            description=description,
            set_flag='_deprecated',
        )
    return decorator


def experimental(
    *,
    since: str | None = None,
    description: str | None = None,
) -> Callable:
    """Marks an object as experimental.

    Parameters:
        since: Version since which the object is experimental
        description: Description

    Returns:
        Decorator
    """
    def decorator(
        obj: T,
    ) -> T:
        return _wrap_with_warning(
            obj=obj,
            message_type='experimental',
            category=AviaryExperimentalWarning,
            since=since,
            removal=None,
            description=description,
            set_flag='_experimental',
        )
    return decorator

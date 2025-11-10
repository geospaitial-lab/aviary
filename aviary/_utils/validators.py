#  Copyright (C) 2024-2025 Marius Maryniak
#
#  This file is part of aviary.
#
#  aviary is free software: you can redistribute it and / or modify it under the terms of the
#  GNU General Public License as published by the Free Software Foundation,
#  either version 3 of the License, or (at your option) any later version.
#
#  aviary is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with aviary.
#  If not, see <https://www.gnu.org/licenses/>.

import re

from aviary.core.enums import ChannelName
from aviary.core.exceptions import AviaryUserError

_valid_name_pattern = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def validate_name(
    name: ChannelName | str | None,
    param: str,
    description: str,
) -> None:
    """Validates `name`.

    Parameters:
        name: Name
        param: Parameter
        description: Description
    """
    if not isinstance(name, str):
        return

    if not _valid_name_pattern.match(name):
        message = (
            f'Invalid {param}! '
            f'The {description} must start with a letter or underscore '
            'and contain only letters, numbers, and underscores.'
        )
        raise AviaryUserError(message)

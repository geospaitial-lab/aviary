#  Copyright (C) 2024-2025 Marius Maryniak
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

import re

import hypothesis
import pytest

# noinspection PyProtectedMember
from aviary._utils.validators import validate_name
from aviary.core.enums import ChannelName
from aviary.core.exceptions import AviaryUserError
from tests._utils.strategies.strategies_test_validators import (
    invalid_names,
    valid_names,
)


@hypothesis.given(name=valid_names)
def test_validate_name_valid(
    name: ChannelName | str | None,
) -> None:
    validate_name(
        name=name,
        param='name',
        description='name',
    )


@hypothesis.given(name=invalid_names)
def test_validate_name_invalid(
    name: str,
) -> None:
    message = re.escape(
        'Invalid name! '
        'The name must start with a letter or underscore and contain only letters, numbers, and underscores.',
    )

    with pytest.raises(AviaryUserError, match=message):
        validate_name(
            name=name,
            param='name',
            description='name',
        )

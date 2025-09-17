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

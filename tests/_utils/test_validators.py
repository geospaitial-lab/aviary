import re

import hypothesis
import pytest

# noinspection PyProtectedMember
from aviary._utils.validators import _validate_channel_name
from aviary.core.enums import ChannelName
from aviary.core.exceptions import AviaryUserError
from tests._utils.strategies.strategies_test_validators import (
    invalid_channel_names,
    valid_channel_names,
)


@hypothesis.given(channel_name=valid_channel_names)
def test__validate_channel_name_valid(
    channel_name: ChannelName | str | None,
) -> None:
    _validate_channel_name(channel_name=channel_name)


@hypothesis.given(channel_name=invalid_channel_names)
def test__validate_channel_name_invalid(
    channel_name: str,
) -> None:
    message = re.escape('Invalid channel_name! The channel name must contain only characters and underscores.')

    with pytest.raises(AviaryUserError, match=message):
        _validate_channel_name(channel_name=channel_name)

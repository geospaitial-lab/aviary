import pytest

from aviary.core.enums import ChannelName

# noinspection PyProtectedMember
from aviary.core.type_aliases import (
    ChannelKey,
    ChannelKeySet,
    ChannelNameKeySet,
    ChannelNameSet,
    _is_channel_key,
    _parse_channel_key,
    _parse_channel_keys,
)
from tests.core.data.data_test_type_aliases import (
    data_test__is_channel_key,
    data_test__parse_channel_key,
    data_test__parse_channel_keys,
)


@pytest.mark.parametrize(('value', 'expected'), data_test__is_channel_key)
def test__is_channel_key(
    value: object,
    expected: bool,
) -> None:
    is_channel_key = _is_channel_key(value=value)

    assert is_channel_key is expected


@pytest.mark.parametrize(('channel_key', 'expected'), data_test__parse_channel_key)
def test__parse_channel_key(
    channel_key: ChannelName | str | ChannelKey,
    expected: ChannelKey,
) -> None:
    channel_key = _parse_channel_key(channel_key=channel_key)

    assert channel_key == expected


@pytest.mark.parametrize(('channel_keys', 'expected'), data_test__parse_channel_keys)
def test__parse_channel_keys(
    channel_keys:
        ChannelName | str |
        ChannelKey |
        ChannelNameSet | ChannelKeySet | ChannelNameKeySet |
        None,
    expected: ChannelKeySet,
) -> None:
    channel_keys = _parse_channel_keys(channel_keys=channel_keys)

    assert channel_keys == expected

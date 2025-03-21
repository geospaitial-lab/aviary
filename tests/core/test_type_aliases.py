import pytest

from aviary.core.enums import ChannelName

# noinspection PyProtectedMember
from aviary.core.type_aliases import (
    ChannelKey,
    ChannelKeySet,
    ChannelNameKeySet,
    ChannelNameSet,
    _coerce_channel_key,
    _coerce_channel_keys,
    _is_channel_key,
)
from tests.core.data.data_test_type_aliases import (
    data_test__coerce_channel_key,
    data_test__coerce_channel_keys,
    data_test__is_channel_key,
)


@pytest.mark.parametrize(('channel_key', 'expected'), data_test__coerce_channel_key)
def test__coerce_channel_key(
    channel_key: ChannelName | str | ChannelKey | None,
    expected: ChannelKey | None,
) -> None:
    channel_key = _coerce_channel_key(channel_key=channel_key)

    assert channel_key == expected


@pytest.mark.parametrize(('channel_keys', 'expected'), data_test__coerce_channel_keys)
def test__coerce_channel_keys(
    channel_keys:
        ChannelName | str |
        ChannelKey |
        ChannelNameSet | ChannelKeySet | ChannelNameKeySet |
        bool |
        None,
    expected: ChannelKeySet | bool,
) -> None:
    channel_keys = _coerce_channel_keys(channel_keys=channel_keys)

    assert channel_keys == expected


@pytest.mark.parametrize(('value', 'expected'), data_test__is_channel_key)
def test__is_channel_key(
    value: object,
    expected: bool,
) -> None:
    is_channel_key = _is_channel_key(value=value)

    assert is_channel_key is expected

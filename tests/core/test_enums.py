import pytest
import rasterio as rio

# noinspection PyProtectedMember
from aviary.core.enums import (
    ChannelName,
    InterpolationMode,
    _coerce_channel_name,
    _coerce_channel_names,
)
from aviary.core.type_aliases import ChannelNameSet
from tests.core.data.data_test_enums import (
    data_test__coerce_channel_name,
    data_test__coerce_channel_names,
)


@pytest.mark.parametrize(('channel_name', 'expected'), data_test__coerce_channel_name)
def test__coerce_channel_name(
    channel_name: ChannelName | str,
    expected: ChannelName | str,
) -> None:
    channel_name = _coerce_channel_name(channel_name=channel_name)

    assert channel_name == expected


@pytest.mark.parametrize(('channel_names', 'expected'), data_test__coerce_channel_names)
def test__coerce_channel_names(
    channel_names:
        ChannelName | str |
        ChannelNameSet |
        bool |
        None,
    expected: ChannelNameSet | bool,
) -> None:
    channel_names = _coerce_channel_names(channel_names=channel_names)

    assert channel_names == expected


def test_interpolation_mode_to_rio() -> None:
    assert InterpolationMode.BILINEAR.to_rio() == rio.enums.Resampling.bilinear
    assert InterpolationMode.NEAREST.to_rio() == rio.enums.Resampling.nearest

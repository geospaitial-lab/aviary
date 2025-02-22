import pytest
import rasterio as rio

# noinspection PyProtectedMember
from aviary.core.enums import (
    ChannelName,
    InterpolationMode,
    _parse_channel_name,
)
from tests.core.data.data_test_enums import data_test__parse_channel_name


@pytest.mark.parametrize(('channel_name', 'expected'), data_test__parse_channel_name)
def test__parse_channel_name(
    channel_name: ChannelName | str,
    expected: ChannelName | str,
) -> None:
    channel_name = _parse_channel_name(channel_name=channel_name)

    assert channel_name == expected


def test_interpolation_mode_to_rio() -> None:
    assert InterpolationMode.BILINEAR.to_rio() == rio.enums.Resampling.bilinear
    assert InterpolationMode.NEAREST.to_rio() == rio.enums.Resampling.nearest

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

import pytest
import rasterio as rio

# noinspection PyProtectedMember
from aviary.core.enums import (
    ChannelName,
    InterpolationMode,
    _coerce_channel_name,
    _coerce_channel_names,
    _coerce_layer_names,
)
from aviary.core.type_aliases import ChannelNameSet
from tests.core.data.data_test_enums import (
    data_test__coerce_channel_name,
    data_test__coerce_channel_names,
    data_test__coerce_layer_names,
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


@pytest.mark.parametrize(('layer_names', 'expected'), data_test__coerce_layer_names)
def test__coerce_layer_names(
    layer_names: str | set[str] | bool | None,
    expected: set[str] | bool,
) -> None:
    layer_names = _coerce_layer_names(layer_names=layer_names)

    assert layer_names == expected


def test_interpolation_mode_to_rio() -> None:
    assert InterpolationMode.BILINEAR.to_rio() == rio.enums.Resampling.bilinear
    assert InterpolationMode.NEAREST.to_rio() == rio.enums.Resampling.nearest

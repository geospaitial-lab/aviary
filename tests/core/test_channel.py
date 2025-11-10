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

import copy
import inspect
import pickle

import geopandas as gpd
import geopandas.testing
import numpy as np
import numpy.typing as npt
import pytest

from aviary.core.channel import (
    RasterChannel,
    VectorChannel,
)
from aviary.core.enums import ChannelName
from aviary.core.exceptions import AviaryUserError
from aviary.core.type_aliases import (
    BufferSize,
    CoordinatesSet,
    FractionalBufferSize,
    TileSize,
)
from tests.core.data.data_test_channel import (
    data_test_raster_channel_add,
    data_test_raster_channel_add_exceptions,
    data_test_raster_channel_append,
    data_test_raster_channel_append_inplace,
    data_test_raster_channel_append_inplace_return,
    data_test_raster_channel_eq,
    data_test_raster_channel_from_channels,
    data_test_raster_channel_from_channels_exceptions,
    data_test_raster_channel_getitem,
    data_test_raster_channel_getitem_slice,
    data_test_raster_channel_init,
    data_test_raster_channel_init_exceptions,
    data_test_raster_channel_remove_buffer,
    data_test_raster_channel_remove_buffer_inplace,
    data_test_raster_channel_remove_buffer_inplace_return,
    data_test_vector_channel_add,
    data_test_vector_channel_add_exceptions,
    data_test_vector_channel_append,
    data_test_vector_channel_append_inplace,
    data_test_vector_channel_append_inplace_return,
    data_test_vector_channel_eq,
    data_test_vector_channel_from_channels,
    data_test_vector_channel_from_channels_exceptions,
    data_test_vector_channel_from_unnormalized_data_exceptions,
    data_test_vector_channel_getitem,
    data_test_vector_channel_getitem_slice,
    data_test_vector_channel_init,
    data_test_vector_channel_init_exceptions,
    data_test_vector_channel_remove_buffer,
    data_test_vector_channel_remove_buffer_inplace,
    data_test_vector_channel_remove_buffer_inplace_return,
)


@pytest.mark.parametrize(
    (
        'data',
        'name',
        'buffer_size',
        'metadata',
        'copy',
        'expected_data',
        'expected_name',
        'expected_buffer_size',
        'expected_metadata',
        'expected_copy',
    ),
    data_test_raster_channel_init,
)
def test_raster_channel_init(
    data: npt.NDArray | list[npt.NDArray],
    name: ChannelName | str,
    buffer_size: FractionalBufferSize,
    metadata: dict[str, object] | None,
    copy: bool,
    expected_data: list[npt.NDArray],
    expected_name: ChannelName | str,
    expected_buffer_size: FractionalBufferSize,
    expected_metadata: dict[str, object],
    expected_copy: bool,
) -> None:
    raster_channel = RasterChannel(
        data=data,
        name=name,
        buffer_size=buffer_size,
        metadata=metadata,
        copy=copy,
    )

    for data_item, expected_data_item in zip(raster_channel, expected_data, strict=True):
        np.testing.assert_array_equal(data_item, expected_data_item)

    assert raster_channel.name == expected_name
    assert raster_channel.buffer_size == expected_buffer_size
    assert raster_channel.metadata == expected_metadata
    assert raster_channel.is_copied is expected_copy


@pytest.mark.parametrize(('data', 'buffer_size', 'message'), data_test_raster_channel_init_exceptions)
def test_raster_channel_init_exceptions(
    data: list[npt.NDArray],
    buffer_size: FractionalBufferSize,
    message: str,
) -> None:
    name = ChannelName.R
    metadata = None
    copy = False

    with pytest.raises(AviaryUserError, match=message):
        _ = RasterChannel(
            data=data,
            name=name,
            buffer_size=buffer_size,
            metadata=metadata,
            copy=copy,
        )


def test_raster_channel_init_defaults() -> None:
    signature = inspect.signature(RasterChannel)
    buffer_size = signature.parameters['buffer_size'].default
    metadata = signature.parameters['metadata'].default
    copy = signature.parameters['copy'].default

    expected_buffer_size = 0.
    expected_metadata = None
    expected_copy = False

    assert buffer_size == expected_buffer_size
    assert metadata is expected_metadata
    assert copy is expected_copy


def test_raster_channel_mutability_no_copy(
    raster_channel_data: list[npt.NDArray],
    metadata: dict[str, object],
) -> None:
    name = ChannelName.R
    buffer_size = 0.
    copy = False

    raster_channel = RasterChannel(
        data=raster_channel_data,
        name=name,
        buffer_size=buffer_size,
        metadata=metadata,
        copy=copy,
    )

    assert id(raster_channel._data) == id(raster_channel_data)

    for data_item, data_item_ in zip(raster_channel, raster_channel_data, strict=True):
        assert id(data_item) == id(data_item_)

    assert id(raster_channel.data) == id(raster_channel._data)
    assert id(raster_channel._metadata) == id(metadata)
    assert id(raster_channel.metadata) == id(raster_channel._metadata)


def test_raster_channel_mutability_copy(
    raster_channel_data: list[npt.NDArray],
    metadata: dict[str, object],
) -> None:
    name = ChannelName.R
    buffer_size = 0.
    copy = True

    raster_channel = RasterChannel(
        data=raster_channel_data,
        name=name,
        buffer_size=buffer_size,
        metadata=metadata,
        copy=copy,
    )

    assert id(raster_channel._data) != id(raster_channel_data)

    for data_item, data_item_ in zip(raster_channel, raster_channel_data, strict=True):
        assert id(data_item) != id(data_item_)

    assert id(raster_channel.data) == id(raster_channel._data)
    assert id(raster_channel._metadata) != id(metadata)
    assert id(raster_channel.metadata) == id(raster_channel._metadata)


def test_raster_channel_setters(
    raster_channel: RasterChannel,
) -> None:
    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        raster_channel.data = None

    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        raster_channel.buffer_size = None


def test_raster_channel_serializability(
    raster_channel: RasterChannel,
) -> None:
    serialized_raster_channel = pickle.dumps(raster_channel)
    deserialized_raster_channel = pickle.loads(serialized_raster_channel)  # noqa: S301

    assert raster_channel == deserialized_raster_channel


def test_raster_channel_batch_size(
    raster_channel: RasterChannel,
) -> None:
    expected = 2

    assert raster_channel.batch_size == expected


@pytest.mark.parametrize(('channels', 'copy', 'expected'), data_test_raster_channel_from_channels)
def test_raster_channel_from_channels(
    channels: list[RasterChannel],
    copy: bool,
    expected: RasterChannel,
) -> None:
    raster_channel = RasterChannel.from_channels(
        channels=channels,
        copy=copy,
    )

    assert raster_channel == expected


@pytest.mark.parametrize(('channels', 'message'), data_test_raster_channel_from_channels_exceptions)
def test_raster_channel_from_channels_exceptions(
    channels: list[RasterChannel],
    message: str,
) -> None:
    copy = False

    with pytest.raises(AviaryUserError, match=message):
        _ = RasterChannel.from_channels(
            channels=channels,
            copy=copy,
        )


def test_raster_channel_from_channels_defaults() -> None:
    signature = inspect.signature(RasterChannel.from_channels)
    copy = signature.parameters['copy'].default

    expected_copy = False

    assert copy is expected_copy


@pytest.mark.parametrize(('other', 'expected'), data_test_raster_channel_eq)
def test_raster_channel_eq(
    other: object,
    expected: bool,
    raster_channel: RasterChannel,
) -> None:
    equals = raster_channel == other

    assert equals is expected


def test_raster_channel_len(
    raster_channel: RasterChannel,
) -> None:
    expected = 2

    assert len(raster_channel) == expected


@pytest.mark.parametrize(('index', 'expected'), data_test_raster_channel_getitem)
def test_raster_channel_getitem(
    index: int,
    expected: npt.NDArray,
    raster_channel: RasterChannel,
) -> None:
    data_item = raster_channel[index]

    np.testing.assert_array_equal(data_item, expected)


@pytest.mark.parametrize(('index', 'expected'), data_test_raster_channel_getitem_slice)
def test_raster_channel_getitem_slice(
    index: slice,
    expected: list[npt.NDArray],
    raster_channel: RasterChannel,
) -> None:
    data = raster_channel[index]

    for data_item, expected_data_item in zip(data, expected, strict=True):
        np.testing.assert_array_equal(data_item, expected_data_item)


def test_get_raster_channel_iter(
    raster_channel: RasterChannel,
    raster_channel_data: list[npt.NDArray],
) -> None:
    for data_item, expected_data_item in zip(raster_channel, raster_channel_data, strict=True):
        np.testing.assert_array_equal(data_item, expected_data_item)


@pytest.mark.parametrize(('other', 'expected'), data_test_raster_channel_add)
def test_raster_channel_add(
    other: RasterChannel,
    expected: RasterChannel,
    raster_channel: RasterChannel,
) -> None:
    raster_channel = raster_channel + other

    assert raster_channel == expected


@pytest.mark.parametrize(('other', 'message'), data_test_raster_channel_add_exceptions)
def test_raster_channel_add_exceptions(
    other: RasterChannel,
    message: str,
    raster_channel: RasterChannel,
) -> None:
    with pytest.raises(AviaryUserError, match=message):
        _ = raster_channel + other


@pytest.mark.parametrize(('data', 'expected'), data_test_raster_channel_append)
def test_raster_channel_append(
    data: npt.NDArray | list[npt.NDArray],
    expected: RasterChannel,
    raster_channel: RasterChannel,
) -> None:
    copied_raster_channel = copy.deepcopy(raster_channel)

    raster_channel_ = raster_channel.append(
        data=data,
        inplace=False,
    )

    assert raster_channel == copied_raster_channel
    assert raster_channel_ == expected
    assert id(raster_channel_) != id(raster_channel)
    assert id(raster_channel_.data) != id(raster_channel.data)

    for data_item_, data_item in zip(raster_channel_, raster_channel, strict=False):
        assert id(data_item_) != id(data_item)

    assert id(raster_channel_.metadata) != id(raster_channel.metadata)
    assert raster_channel.is_copied is False
    assert raster_channel_.is_copied is True


@pytest.mark.parametrize(('data', 'expected'), data_test_raster_channel_append_inplace)
def test_raster_channel_append_inplace(
    data: npt.NDArray | list[npt.NDArray],
    expected: RasterChannel,
    raster_channel: RasterChannel,
) -> None:
    raster_channel.append(
        data=data,
        inplace=True,
    )

    assert raster_channel == expected


@pytest.mark.parametrize(('data', 'expected'), data_test_raster_channel_append_inplace_return)
def test_raster_channel_append_inplace_return(
    data: npt.NDArray | list[npt.NDArray],
    expected: RasterChannel,
    raster_channel: RasterChannel,
) -> None:
    raster_channel_ = raster_channel.append(
        data=data,
        inplace=True,
    )

    assert raster_channel == expected
    assert raster_channel_ == expected
    assert id(raster_channel_) == id(raster_channel)
    assert id(raster_channel_.data) == id(raster_channel.data)

    for data_item_, data_item in zip(raster_channel_, raster_channel, strict=False):
        assert id(data_item_) == id(data_item)

    assert id(raster_channel_.metadata) == id(raster_channel.metadata)


def test_raster_channel_append_defaults() -> None:
    signature = inspect.signature(RasterChannel.append)
    inplace = signature.parameters['inplace'].default

    expected_inplace = False

    assert inplace is expected_inplace


def test_raster_channel_copy(
    raster_channel: RasterChannel,
) -> None:
    copied_raster_channel = raster_channel.copy()

    assert copied_raster_channel == raster_channel
    assert copied_raster_channel.is_copied is True
    assert id(copied_raster_channel) != id(raster_channel)
    assert id(copied_raster_channel.data) != id(raster_channel.data)

    for copied_data_item, data_item in zip(copied_raster_channel, raster_channel, strict=True):
        assert id(copied_data_item) != id(data_item)

    assert id(copied_raster_channel.metadata) != id(raster_channel.metadata)


@pytest.mark.parametrize(('raster_channel', 'expected'), data_test_raster_channel_remove_buffer)
def test_raster_channel_remove_buffer(
    raster_channel: RasterChannel,
    expected: RasterChannel,
) -> None:
    copied_raster_channel = copy.deepcopy(raster_channel)

    raster_channel_ = raster_channel.remove_buffer(inplace=False)

    assert raster_channel == copied_raster_channel
    assert raster_channel_ == expected
    assert id(raster_channel_) != id(raster_channel)
    assert id(raster_channel_.data) != id(raster_channel.data)

    for data_item_, data_item in zip(raster_channel_, raster_channel, strict=True):
        assert id(data_item_) != id(data_item)

    assert id(raster_channel_.metadata) != id(raster_channel.metadata)
    assert raster_channel.is_copied is False
    assert raster_channel_.is_copied is True


@pytest.mark.parametrize(('raster_channel', 'expected'), data_test_raster_channel_remove_buffer_inplace)
def test_raster_channel_remove_buffer_inplace(
    raster_channel: RasterChannel,
    expected: RasterChannel,
) -> None:
    raster_channel.remove_buffer(inplace=True)

    assert raster_channel == expected


@pytest.mark.parametrize(('raster_channel', 'expected'), data_test_raster_channel_remove_buffer_inplace_return)
def test_raster_channel_remove_buffer_inplace_return(
    raster_channel: RasterChannel,
    expected: RasterChannel,
) -> None:
    raster_channel_ = raster_channel.remove_buffer(inplace=True)

    assert raster_channel == expected
    assert raster_channel_ == expected
    assert id(raster_channel_) == id(raster_channel)
    assert id(raster_channel_.data) == id(raster_channel.data)

    for data_item_, data_item in zip(raster_channel_, raster_channel, strict=True):
        assert id(data_item_) == id(data_item)

    assert id(raster_channel_.metadata) == id(raster_channel.metadata)


def test_raster_channel_remove_buffer_defaults() -> None:
    signature = inspect.signature(RasterChannel.remove_buffer)
    inplace = signature.parameters['inplace'].default

    expected_inplace = False

    assert inplace is expected_inplace


@pytest.mark.parametrize(
    (
        'data',
        'name',
        'buffer_size',
        'metadata',
        'copy',
        'expected_data',
        'expected_name',
        'expected_buffer_size',
        'expected_metadata',
        'expected_copy',
    ),
    data_test_vector_channel_init,
)
def test_vector_channel_init(
    data: gpd.GeoDataFrame | list[gpd.GeoDataFrame],
    name: ChannelName | str,
    buffer_size: FractionalBufferSize,
    metadata: dict[str, object] | None,
    copy: bool,
    expected_data: list[gpd.GeoDataFrame],
    expected_name: ChannelName | str,
    expected_buffer_size: FractionalBufferSize,
    expected_metadata: dict[str, object],
    expected_copy: bool,
) -> None:
    vector_channel = VectorChannel(
        data=data,
        name=name,
        buffer_size=buffer_size,
        metadata=metadata,
        copy=copy,
    )

    for data_item, expected_data_item in zip(vector_channel, expected_data, strict=True):
        gpd.testing.assert_geodataframe_equal(data_item, expected_data_item)

    assert vector_channel.name == expected_name
    assert vector_channel.buffer_size == expected_buffer_size
    assert vector_channel.metadata == expected_metadata
    assert vector_channel.is_copied is expected_copy


@pytest.mark.parametrize(('data', 'buffer_size', 'message'), data_test_vector_channel_init_exceptions)
def test_vector_channel_init_exceptions(
    data: list[gpd.GeoDataFrame],
    buffer_size: FractionalBufferSize,
    message: str,
) -> None:
    name = ChannelName.R
    metadata = None
    copy = False

    with pytest.raises(AviaryUserError, match=message):
        _ = VectorChannel(
            data=data,
            name=name,
            buffer_size=buffer_size,
            metadata=metadata,
            copy=copy,
        )


def test_vector_channel_init_defaults() -> None:
    signature = inspect.signature(VectorChannel)
    buffer_size = signature.parameters['buffer_size'].default
    metadata = signature.parameters['metadata'].default
    copy = signature.parameters['copy'].default

    expected_buffer_size = 0.
    expected_metadata = None
    expected_copy = False

    assert buffer_size == expected_buffer_size
    assert metadata is expected_metadata
    assert copy is expected_copy


def test_vector_channel_mutability_no_copy(
    vector_channel_data: list[gpd.GeoDataFrame],
    metadata: dict[str, object],
) -> None:
    name = ChannelName.R
    buffer_size = 0.
    copy = False

    vector_channel = VectorChannel(
        data=vector_channel_data,
        name=name,
        buffer_size=buffer_size,
        metadata=metadata,
        copy=copy,
    )

    assert id(vector_channel._data) == id(vector_channel_data)

    for data_item, data_item_ in zip(vector_channel, vector_channel_data, strict=True):
        assert id(data_item) == id(data_item_)

    assert id(vector_channel.data) == id(vector_channel._data)
    assert id(vector_channel._metadata) == id(metadata)
    assert id(vector_channel.metadata) == id(vector_channel._metadata)


def test_vector_channel_mutability_copy(
    vector_channel_data: list[gpd.GeoDataFrame],
    metadata: dict[str, object],
) -> None:
    name = ChannelName.R
    buffer_size = 0.
    copy = True

    vector_channel = VectorChannel(
        data=vector_channel_data,
        name=name,
        buffer_size=buffer_size,
        metadata=metadata,
        copy=copy,
    )

    assert id(vector_channel._data) != id(vector_channel_data)

    for data_item, data_item_ in zip(vector_channel, vector_channel_data, strict=True):
        assert id(data_item) != id(data_item_)

    assert id(vector_channel.data) == id(vector_channel._data)
    assert id(vector_channel._metadata) != id(metadata)
    assert id(vector_channel.metadata) == id(vector_channel._metadata)


def test_vector_channel_setters(
    vector_channel: VectorChannel,
) -> None:
    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        vector_channel.data = None

    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        vector_channel.buffer_size = None


def test_vector_channel_serializability(
    vector_channel: VectorChannel,
) -> None:
    serialized_vector_channel = pickle.dumps(vector_channel)
    deserialized_vector_channel = pickle.loads(serialized_vector_channel)  # noqa: S301

    assert vector_channel == deserialized_vector_channel


def test_vector_channel_batch_size(
    vector_channel: VectorChannel,
) -> None:
    expected = 2

    assert vector_channel.batch_size == expected


@pytest.mark.parametrize(('channels', 'copy', 'expected'), data_test_vector_channel_from_channels)
def test_vector_channel_from_channels(
    channels: list[VectorChannel],
    copy: bool,
    expected: VectorChannel,
) -> None:
    vector_channel = VectorChannel.from_channels(
        channels=channels,
        copy=copy,
    )

    assert vector_channel == expected


@pytest.mark.parametrize(('channels', 'message'), data_test_vector_channel_from_channels_exceptions)
def test_vector_channel_from_channels_exceptions(
    channels: list[VectorChannel],
    message: str,
) -> None:
    copy = False

    with pytest.raises(AviaryUserError, match=message):
        _ = VectorChannel.from_channels(
            channels=channels,
            copy=copy,
        )


def test_vector_channel_from_channels_defaults() -> None:
    signature = inspect.signature(VectorChannel.from_channels)
    copy = signature.parameters['copy'].default

    expected_copy = False

    assert copy is expected_copy


@pytest.mark.skip(reason='Not implemented')
def test_vector_channel_from_unnormalized_data() -> None:
    pass


@pytest.mark.parametrize(
    (
        'data',
        'coordinates',
        'tile_size',
        'buffer_size',
        'message',
    ),
    data_test_vector_channel_from_unnormalized_data_exceptions,
)
def test_vector_channel_from_unnormalized_data_exceptions(
    data: list[gpd.GeoDataFrame],
    coordinates: CoordinatesSet,
    tile_size: TileSize,
    buffer_size: BufferSize,
    message: str,
) -> None:
    name = ChannelName.R
    metadata = None
    copy = False

    with pytest.raises(AviaryUserError, match=message):
        _ = VectorChannel.from_unnormalized_data(
            data=data,
            name=name,
            coordinates=coordinates,
            tile_size=tile_size,
            buffer_size=buffer_size,
            metadata=metadata,
            copy=copy,
        )


def test_vector_channel_from_unnormalized_data_defaults() -> None:
    signature = inspect.signature(VectorChannel.from_unnormalized_data)
    buffer_size = signature.parameters['buffer_size'].default
    metadata = signature.parameters['metadata'].default
    copy = signature.parameters['copy'].default

    expected_buffer_size = 0.
    expected_metadata = None
    expected_copy = False

    assert buffer_size == expected_buffer_size
    assert metadata is expected_metadata
    assert copy is expected_copy


@pytest.mark.parametrize(('other', 'expected'), data_test_vector_channel_eq)
def test_vector_channel_eq(
    other: object,
    expected: bool,
    vector_channel: VectorChannel,
) -> None:
    equals = vector_channel == other

    assert equals is expected


def test_vector_channel_len(
    vector_channel: VectorChannel,
) -> None:
    expected = 2

    assert len(vector_channel) == expected


@pytest.mark.parametrize(('index', 'expected'), data_test_vector_channel_getitem)
def test_vector_channel_getitem(
    index: int,
    expected: gpd.GeoDataFrame,
    vector_channel: VectorChannel,
) -> None:
    data_item = vector_channel[index]

    gpd.testing.assert_geodataframe_equal(data_item, expected)


@pytest.mark.parametrize(('index', 'expected'), data_test_vector_channel_getitem_slice)
def test_vector_channel_getitem_slice(
    index: slice,
    expected: list[gpd.GeoDataFrame],
    vector_channel: VectorChannel,
) -> None:
    data = vector_channel[index]

    for data_item, expected_data_item in zip(data, expected, strict=True):
        gpd.testing.assert_geodataframe_equal(data_item, expected_data_item)


def test_get_vector_channel_iter(
    vector_channel: VectorChannel,
    vector_channel_data: list[gpd.GeoDataFrame],
) -> None:
    for data_item, expected_data_item in zip(vector_channel, vector_channel_data, strict=True):
        gpd.testing.assert_geodataframe_equal(data_item, expected_data_item)


@pytest.mark.parametrize(('other', 'expected'), data_test_vector_channel_add)
def test_vector_channel_add(
    other: VectorChannel,
    expected: VectorChannel,
    vector_channel: VectorChannel,
) -> None:
    vector_channel = vector_channel + other

    assert vector_channel == expected


@pytest.mark.parametrize(('other', 'message'), data_test_vector_channel_add_exceptions)
def test_vector_channel_add_exceptions(
    other: VectorChannel,
    message: str,
    vector_channel: VectorChannel,
) -> None:
    with pytest.raises(AviaryUserError, match=message):
        _ = vector_channel + other


@pytest.mark.parametrize(('data', 'expected'), data_test_vector_channel_append)
def test_vector_channel_append(
    data: gpd.GeoDataFrame | list[gpd.GeoDataFrame],
    expected: VectorChannel,
    vector_channel: VectorChannel,
) -> None:
    copied_vector_channel = copy.deepcopy(vector_channel)

    vector_channel_ = vector_channel.append(
        data=data,
        inplace=False,
    )

    assert vector_channel == copied_vector_channel
    assert vector_channel_ == expected
    assert id(vector_channel_) != id(vector_channel)
    assert id(vector_channel_.data) != id(vector_channel.data)

    for data_item_, data_item in zip(vector_channel_, vector_channel, strict=False):
        assert id(data_item_) != id(data_item)

    assert id(vector_channel_.metadata) != id(vector_channel.metadata)
    assert vector_channel.is_copied is False
    assert vector_channel_.is_copied is True


@pytest.mark.parametrize(('data', 'expected'), data_test_vector_channel_append_inplace)
def test_vector_channel_append_inplace(
    data: gpd.GeoDataFrame | list[gpd.GeoDataFrame],
    expected: VectorChannel,
    vector_channel: VectorChannel,
) -> None:
    vector_channel.append(
        data=data,
        inplace=True,
    )

    assert vector_channel == expected


@pytest.mark.parametrize(('data', 'expected'), data_test_vector_channel_append_inplace_return)
def test_vector_channel_append_inplace_return(
    data: gpd.GeoDataFrame | list[gpd.GeoDataFrame],
    expected: VectorChannel,
    vector_channel: VectorChannel,
) -> None:
    vector_channel_ = vector_channel.append(
        data=data,
        inplace=True,
    )

    assert vector_channel == expected
    assert vector_channel_ == expected
    assert id(vector_channel_) == id(vector_channel)
    assert id(vector_channel_.data) == id(vector_channel.data)

    for data_item_, data_item in zip(vector_channel_, vector_channel, strict=False):
        assert id(data_item_) == id(data_item)

    assert id(vector_channel_.metadata) == id(vector_channel.metadata)


def test_vector_channel_append_defaults() -> None:
    signature = inspect.signature(VectorChannel.append)
    inplace = signature.parameters['inplace'].default

    expected_inplace = False

    assert inplace is expected_inplace


def test_vector_channel_copy(
    vector_channel: VectorChannel,
) -> None:
    copied_vector_channel = vector_channel.copy()

    assert copied_vector_channel == vector_channel
    assert copied_vector_channel.is_copied is True
    assert id(copied_vector_channel) != id(vector_channel)
    assert id(copied_vector_channel.data) != id(vector_channel.data)

    for copied_data_item, data_item in zip(copied_vector_channel, vector_channel, strict=True):
        assert id(copied_data_item) != id(data_item)

    assert id(copied_vector_channel.metadata) != id(vector_channel.metadata)


@pytest.mark.parametrize(('vector_channel', 'expected'), data_test_vector_channel_remove_buffer)
def test_vector_channel_remove_buffer(
    vector_channel: VectorChannel,
    expected: VectorChannel,
) -> None:
    copied_vector_channel = copy.deepcopy(vector_channel)

    vector_channel_ = vector_channel.remove_buffer(inplace=False)

    assert vector_channel == copied_vector_channel
    assert vector_channel_ == expected
    assert id(vector_channel_) != id(vector_channel)
    assert id(vector_channel_.data) != id(vector_channel.data)

    for data_item_, data_item in zip(vector_channel_, vector_channel, strict=True):
        assert id(data_item_) != id(data_item)

    assert id(vector_channel_.metadata) != id(vector_channel.metadata)
    assert vector_channel.is_copied is False
    assert vector_channel_.is_copied is True


@pytest.mark.parametrize(('vector_channel', 'expected'), data_test_vector_channel_remove_buffer_inplace)
def test_vector_channel_remove_buffer_inplace(
    vector_channel: VectorChannel,
    expected: VectorChannel,
) -> None:
    vector_channel.remove_buffer(inplace=True)

    assert vector_channel == expected


@pytest.mark.parametrize(('vector_channel', 'expected'), data_test_vector_channel_remove_buffer_inplace_return)
def test_vector_channel_remove_buffer_inplace_return(
    vector_channel: VectorChannel,
    expected: VectorChannel,
) -> None:
    vector_channel_ = vector_channel.remove_buffer(inplace=True)

    assert vector_channel == expected
    assert vector_channel_ == expected
    assert id(vector_channel_) == id(vector_channel)
    assert id(vector_channel_.data) == id(vector_channel.data)

    for data_item_, data_item in zip(vector_channel_, vector_channel, strict=True):
        assert id(data_item_) == id(data_item)

    assert id(vector_channel_.metadata) == id(vector_channel.metadata)


def test_vector_channel_remove_buffer_defaults() -> None:
    signature = inspect.signature(VectorChannel.remove_buffer)
    inplace = signature.parameters['inplace'].default

    expected_inplace = False

    assert inplace is expected_inplace

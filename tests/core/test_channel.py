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
    FractionalBufferSize,
    TileSize,
    TimeStep,
)
from tests.core.data.data_test_channel import (
    data_test_raster_channel_eq,
    data_test_raster_channel_init,
    data_test_raster_channel_init_exceptions,
    data_test_raster_channel_remove_buffer,
    data_test_vector_channel_eq,
    data_test_vector_channel_from_unscaled_data_exceptions,
    data_test_vector_channel_init,
    data_test_vector_channel_init_exceptions,
    data_test_vector_channel_remove_buffer,
)


@pytest.mark.parametrize(
    (
        'data',
        'name',
        'buffer_size',
        'time_step',
        'copy',
        'expected_data',
        'expected_name',
        'expected_buffer_size',
        'expected_time_step',
        'expected_copy',
    ),
    data_test_raster_channel_init,
)
def test_raster_channel_init(
    data: npt.NDArray,
    name: ChannelName | str,
    buffer_size: FractionalBufferSize,
    time_step: TimeStep | None,
    copy: bool,
    expected_data: npt.NDArray,
    expected_name: ChannelName | str,
    expected_buffer_size: FractionalBufferSize,
    expected_time_step: TimeStep | None,
    expected_copy: bool,
) -> None:
    raster_channel = RasterChannel(
        data=data,
        name=name,
        buffer_size=buffer_size,
        time_step=time_step,
        copy=copy,
    )

    np.testing.assert_array_equal(raster_channel.data, expected_data)
    assert raster_channel.name == expected_name
    assert raster_channel.buffer_size == expected_buffer_size
    assert raster_channel.time_step == expected_time_step
    assert raster_channel.is_copied == expected_copy


@pytest.mark.parametrize(('data', 'buffer_size', 'message'), data_test_raster_channel_init_exceptions)
def test_raster_channel_init_exceptions(
    data: npt.NDArray,
    buffer_size: FractionalBufferSize,
    message: str,
) -> None:
    name = ChannelName.R
    time_step = None
    copy = False

    with pytest.raises(AviaryUserError, match=message):
        _ = RasterChannel(
            data=data,
            name=name,
            buffer_size=buffer_size,
            time_step=time_step,
            copy=copy,
        )


def test_raster_channel_init_defaults() -> None:
    signature = inspect.signature(RasterChannel)
    buffer_size = signature.parameters['buffer_size'].default
    time_step = signature.parameters['time_step'].default
    copy = signature.parameters['copy'].default
    expected_buffer_size = 0.
    expected_time_step = None
    expected_copy = False

    assert buffer_size == expected_buffer_size
    assert time_step is expected_time_step
    assert copy is expected_copy


def test_raster_channel_mutability_no_copy(
    raster_channel_data: npt.NDArray,
) -> None:
    name = ChannelName.R
    buffer_size = 0.
    time_step = None
    copy = False

    raster_channel = RasterChannel(
        data=raster_channel_data,
        name=name,
        buffer_size=buffer_size,
        time_step=time_step,
        copy=copy,
    )

    assert id(raster_channel._data) == id(raster_channel_data)
    assert id(raster_channel.data) == id(raster_channel._data)


def test_raster_channel_mutability_copy(
    raster_channel_data: npt.NDArray,
) -> None:
    name = ChannelName.R
    buffer_size = 0.
    time_step = None
    copy = True

    raster_channel = RasterChannel(
        data=raster_channel_data,
        name=name,
        buffer_size=buffer_size,
        time_step=time_step,
        copy=copy,
    )

    assert id(raster_channel._data) != id(raster_channel_data)
    assert id(raster_channel.data) == id(raster_channel._data)


def test_raster_channel_setters(
    raster_channel: RasterChannel,
) -> None:
    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        raster_channel.data = None

    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        raster_channel.name = None

    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        raster_channel.buffer_size = None

    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        raster_channel.time_step = None


def test_raster_channel_serializability(
    raster_channel: RasterChannel,
) -> None:
    serialized_raster_channel = pickle.dumps(raster_channel)
    deserialized_raster_channel = pickle.loads(serialized_raster_channel)  # noqa: S301

    assert raster_channel == deserialized_raster_channel


def test_raster_channel_key(
    raster_channel: RasterChannel,
) -> None:
    expected_name = ChannelName.R
    expected_time_step = None
    expected = (expected_name, expected_time_step)

    assert raster_channel.key == expected


@pytest.mark.parametrize(('other', 'expected'), data_test_raster_channel_eq)
def test_raster_channel_eq(
    other: object,
    expected: bool,
    raster_channel: RasterChannel,
) -> None:
    equals = raster_channel == other

    assert equals is expected


def test_raster_channel_copy(
    raster_channel: RasterChannel,
) -> None:
    copied_raster_channel = raster_channel.copy()

    assert copied_raster_channel == raster_channel
    assert copied_raster_channel.is_copied is True
    assert id(copied_raster_channel) != id(raster_channel)
    assert id(copied_raster_channel.data) != id(raster_channel.data)


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
    assert raster_channel.is_copied is False
    assert raster_channel_.is_copied is True


@pytest.mark.parametrize(('raster_channel', 'expected'), data_test_raster_channel_remove_buffer)
def test_raster_channel_remove_buffer_inplace(
    raster_channel: RasterChannel,
    expected: RasterChannel,
) -> None:
    raster_channel.remove_buffer(inplace=True)

    assert raster_channel == expected


@pytest.mark.parametrize(('raster_channel', 'expected'), data_test_raster_channel_remove_buffer)
def test_raster_channel_remove_buffer_inplace_return(
    raster_channel: RasterChannel,
    expected: RasterChannel,
) -> None:
    raster_channel_ = raster_channel.remove_buffer(inplace=True)

    assert raster_channel == expected
    assert raster_channel_ == expected
    assert id(raster_channel_) == id(raster_channel)


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
        'time_step',
        'copy',
        'expected_data',
        'expected_name',
        'expected_buffer_size',
        'expected_time_step',
        'expected_copy',
    ),
    data_test_vector_channel_init,
)
def test_vector_channel_init(
    data: gpd.GeoDataFrame,
    name: ChannelName | str,
    buffer_size: FractionalBufferSize,
    time_step: TimeStep | None,
    copy: bool,
    expected_data: gpd.GeoDataFrame,
    expected_name: ChannelName | str,
    expected_buffer_size: FractionalBufferSize,
    expected_time_step: TimeStep | None,
    expected_copy: bool,
) -> None:
    vector_channel = VectorChannel(
        data=data,
        name=name,
        buffer_size=buffer_size,
        time_step=time_step,
        copy=copy,
    )

    gpd.testing.assert_geodataframe_equal(vector_channel.data, expected_data)
    assert vector_channel.name == expected_name
    assert vector_channel.buffer_size == expected_buffer_size
    assert vector_channel.time_step == expected_time_step
    assert vector_channel.is_copied == expected_copy


@pytest.mark.parametrize(('data', 'buffer_size', 'message'), data_test_vector_channel_init_exceptions)
def test_vector_channel_init_exceptions(
    data: gpd.GeoDataFrame,
    buffer_size: FractionalBufferSize,
    message: str,
) -> None:
    name = ChannelName.R
    time_step = None
    copy = False

    with pytest.raises(AviaryUserError, match=message):
        _ = VectorChannel(
            data=data,
            name=name,
            buffer_size=buffer_size,
            time_step=time_step,
            copy=copy,
        )


def test_vector_channel_init_defaults() -> None:
    signature = inspect.signature(VectorChannel)
    buffer_size = signature.parameters['buffer_size'].default
    time_step = signature.parameters['time_step'].default
    copy = signature.parameters['copy'].default
    expected_buffer_size = 0.
    expected_time_step = None
    expected_copy = False

    assert buffer_size == expected_buffer_size
    assert time_step is expected_time_step
    assert copy is expected_copy


def test_vector_channel_mutability_no_copy(
    vector_channel_data: gpd.GeoDataFrame,
) -> None:
    name = ChannelName.R
    buffer_size = 0.
    time_step = None
    copy = False

    vector_channel = VectorChannel(
        data=vector_channel_data,
        name=name,
        buffer_size=buffer_size,
        time_step=time_step,
        copy=copy,
    )

    assert id(vector_channel._data) == id(vector_channel_data)
    assert id(vector_channel.data) == id(vector_channel._data)


def test_vector_channel_mutability_copy(
    vector_channel_data: gpd.GeoDataFrame,
) -> None:
    name = ChannelName.R
    buffer_size = 0.
    time_step = None
    copy = True

    vector_channel = VectorChannel(
        data=vector_channel_data,
        name=name,
        buffer_size=buffer_size,
        time_step=time_step,
        copy=copy,
    )

    assert id(vector_channel._data) != id(vector_channel_data)
    assert id(vector_channel.data) == id(vector_channel._data)


def test_vector_channel_setters(
    vector_channel: VectorChannel,
) -> None:
    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        vector_channel.data = None

    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        vector_channel.name = None

    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        vector_channel.buffer_size = None

    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        vector_channel.time_step = None


def test_vector_channel_serializability(
    vector_channel: VectorChannel,
) -> None:
    serialized_vector_channel = pickle.dumps(vector_channel)
    deserialized_vector_channel = pickle.loads(serialized_vector_channel)  # noqa: S301

    assert vector_channel == deserialized_vector_channel


def test_vector_channel_key(
    vector_channel: VectorChannel,
) -> None:
    expected_name = ChannelName.R
    expected_time_step = None
    expected = (expected_name, expected_time_step)

    assert vector_channel.key == expected


@pytest.mark.skip(reason='Not implemented')
def test_vector_channel_from_unscaled_data() -> None:
    pass


@pytest.mark.parametrize(
    (
        'tile_size',
        'buffer_size',
        'message',
    ),
    data_test_vector_channel_from_unscaled_data_exceptions,
)
def test_vector_channel_from_unscaled_data_exceptions(
    tile_size: TileSize,
    buffer_size: BufferSize,
    message: str,
    vector_channel_data: gpd.GeoDataFrame,
) -> None:
    name = ChannelName.R
    coordinates = (0, 0)
    time_step = None
    copy = False

    with pytest.raises(AviaryUserError, match=message):
        _ = VectorChannel.from_unscaled_data(
            data=vector_channel_data,
            name=name,
            coordinates=coordinates,
            tile_size=tile_size,
            buffer_size=buffer_size,
            time_step=time_step,
            copy=copy,
        )


def test_vector_channel_from_unscaled_data_defaults() -> None:
    signature = inspect.signature(VectorChannel.from_unscaled_data)
    buffer_size = signature.parameters['buffer_size'].default
    time_step = signature.parameters['time_step'].default
    copy = signature.parameters['copy'].default
    expected_buffer_size = 0.
    expected_time_step = None
    expected_copy = False

    assert buffer_size == expected_buffer_size
    assert time_step is expected_time_step
    assert copy is expected_copy


@pytest.mark.parametrize(('other', 'expected'), data_test_vector_channel_eq)
def test_vector_channel_eq(
    other: object,
    expected: bool,
    vector_channel: VectorChannel,
) -> None:
    equals = vector_channel == other

    assert equals is expected


def test_vector_channel_copy(
    vector_channel: VectorChannel,
) -> None:
    copied_vector_channel = vector_channel.copy()

    assert copied_vector_channel == vector_channel
    assert copied_vector_channel.is_copied is True
    assert id(copied_vector_channel) != id(vector_channel)
    assert id(copied_vector_channel.data) != id(vector_channel.data)


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
    assert vector_channel.is_copied is False
    assert vector_channel_.is_copied is True


@pytest.mark.parametrize(('vector_channel', 'expected'), data_test_vector_channel_remove_buffer)
def test_vector_channel_remove_buffer_inplace(
    vector_channel: VectorChannel,
    expected: VectorChannel,
) -> None:
    vector_channel.remove_buffer(inplace=True)

    assert vector_channel == expected


@pytest.mark.parametrize(('vector_channel', 'expected'), data_test_vector_channel_remove_buffer)
def test_vector_channel_remove_buffer_inplace_return(
    vector_channel: VectorChannel,
    expected: VectorChannel,
) -> None:
    vector_channel_ = vector_channel.remove_buffer(inplace=True)

    assert vector_channel == expected
    assert vector_channel_ == expected
    assert id(vector_channel_) == id(vector_channel)


def test_vector_channel_remove_buffer_defaults() -> None:
    signature = inspect.signature(VectorChannel.remove_buffer)
    inplace = signature.parameters['inplace'].default
    expected_inplace = False

    assert inplace is expected_inplace

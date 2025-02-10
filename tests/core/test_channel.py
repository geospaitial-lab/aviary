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
from aviary.core.type_aliases import FractionalBufferSize
from tests.core.data.data_test_channel import (
    data_test_raster_channel_init_exceptions,
    data_test_raster_channel_remove_buffer,
    data_test_vector_channel_init_exceptions,
    data_test_vector_channel_remove_buffer,
)


def test_raster_channel_init(
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

    np.testing.assert_array_equal(raster_channel.data, raster_channel_data)
    assert raster_channel.name == name
    assert raster_channel.buffer_size == buffer_size
    assert raster_channel.time_step == time_step
    assert raster_channel.is_copied == copy


def test_raster_channel_init_built_in_name(
    raster_channel_data: npt.NDArray,
) -> None:
    name = 'r'
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
    expected_name = ChannelName.R

    np.testing.assert_array_equal(raster_channel.data, raster_channel_data)
    assert raster_channel.name == expected_name
    assert raster_channel.buffer_size == buffer_size
    assert raster_channel.time_step == time_step
    assert raster_channel.is_copied == copy


def test_raster_channel_init_custom_name(
    raster_channel_data: npt.NDArray,
) -> None:
    name = 'custom'
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

    np.testing.assert_array_equal(raster_channel.data, raster_channel_data)
    assert raster_channel.name == name
    assert raster_channel.buffer_size == buffer_size
    assert raster_channel.time_step == time_step
    assert raster_channel.is_copied == copy


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

    assert buffer_size == 0.
    assert time_step is None
    assert copy is False


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


def test_raster_channel_pickle(
    raster_channel: RasterChannel,
) -> None:
    pickled_raster_channel = pickle.dumps(raster_channel)
    unpickled_raster_channel = pickle.loads(pickled_raster_channel)  # noqa: S301

    assert raster_channel == unpickled_raster_channel


def test_raster_channel_key(
    raster_channel: RasterChannel,
) -> None:
    expected_name = ChannelName.R
    expected_time_step = None
    expected_key = (expected_name, expected_time_step)

    assert raster_channel.key == expected_key


def test_raster_channel_eq(
    raster_channel: RasterChannel,
    raster_channel_data: npt.NDArray,
    raster_channel_buffered_data: npt.NDArray,
) -> None:
    other_name = ChannelName.R
    other_buffer_size = 0.
    other_time_step = None
    other_copy = False
    other_raster_channel = RasterChannel(
        data=raster_channel_data,
        name=other_name,
        buffer_size=other_buffer_size,
        time_step=other_time_step,
        copy=other_copy,
    )

    assert raster_channel == other_raster_channel

    other_name = ChannelName.R
    other_buffer_size = 0.
    other_time_step = None
    other_copy = True
    other_raster_channel = RasterChannel(
        data=raster_channel_data,
        name=other_name,
        buffer_size=other_buffer_size,
        time_step=other_time_step,
        copy=other_copy,
    )

    assert raster_channel == other_raster_channel

    other_name = ChannelName.G
    other_buffer_size = .25
    other_time_step = 0
    other_copy = False
    other_raster_channel = RasterChannel(
        data=raster_channel_buffered_data,
        name=other_name,
        buffer_size=other_buffer_size,
        time_step=other_time_step,
        copy=other_copy,
    )

    assert raster_channel != other_raster_channel

    other_raster_channel = 'invalid'

    assert raster_channel != other_raster_channel


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

    assert inplace is False


def test_vector_channel_init(
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

    gpd.testing.assert_geodataframe_equal(vector_channel.data, vector_channel_data)
    assert vector_channel.name == name
    assert vector_channel.buffer_size == buffer_size
    assert vector_channel.time_step == time_step
    assert vector_channel.is_copied == copy


def test_vector_channel_init_empty_data(
    vector_channel_empty_data: gpd.GeoDataFrame,
) -> None:
    name = ChannelName.R
    buffer_size = 0.
    time_step = None
    copy = False
    vector_channel = VectorChannel(
        data=vector_channel_empty_data,
        name=name,
        buffer_size=buffer_size,
        time_step=time_step,
        copy=copy,
    )

    gpd.testing.assert_geodataframe_equal(vector_channel.data, vector_channel_empty_data)
    assert vector_channel.name == name
    assert vector_channel.buffer_size == buffer_size
    assert vector_channel.time_step == time_step
    assert vector_channel.is_copied == copy


def test_vector_channel_init_built_in_name(
    vector_channel_data: gpd.GeoDataFrame,
) -> None:
    name = 'r'
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
    expected_name = ChannelName.R

    gpd.testing.assert_geodataframe_equal(vector_channel.data, vector_channel_data)
    assert vector_channel.name == expected_name
    assert vector_channel.buffer_size == buffer_size
    assert vector_channel.time_step == time_step
    assert vector_channel.is_copied == copy


def test_vector_channel_init_custom_name(
    vector_channel_data: gpd.GeoDataFrame,
) -> None:
    name = 'custom'
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

    gpd.testing.assert_geodataframe_equal(vector_channel.data, vector_channel_data)
    assert vector_channel.name == name
    assert vector_channel.buffer_size == buffer_size
    assert vector_channel.time_step == time_step
    assert vector_channel.is_copied == copy


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

    assert buffer_size == 0.
    assert time_step is None
    assert copy is False


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


def test_vector_channel_pickle(
    vector_channel: VectorChannel,
) -> None:
    pickled_vector_channel = pickle.dumps(vector_channel)
    unpickled_vector_channel = pickle.loads(pickled_vector_channel)  # noqa: S301

    assert vector_channel == unpickled_vector_channel


def test_vector_channel_key(
    vector_channel: VectorChannel,
) -> None:
    expected_name = ChannelName.R
    expected_time_step = None
    expected_key = (expected_name, expected_time_step)

    assert vector_channel.key == expected_key


def test_vector_channel_eq(
    vector_channel: VectorChannel,
    vector_channel_data: gpd.GeoDataFrame,
    vector_channel_empty_data: gpd.GeoDataFrame,
) -> None:
    other_name = ChannelName.R
    other_buffer_size = 0.
    other_time_step = None
    other_copy = False
    other_vector_channel = VectorChannel(
        data=vector_channel_data,
        name=other_name,
        buffer_size=other_buffer_size,
        time_step=other_time_step,
        copy=other_copy,
    )

    assert vector_channel == other_vector_channel

    other_name = ChannelName.R
    other_buffer_size = 0.
    other_time_step = None
    other_copy = True
    other_vector_channel = VectorChannel(
        data=vector_channel_data,
        name=other_name,
        buffer_size=other_buffer_size,
        time_step=other_time_step,
        copy=other_copy,
    )

    assert vector_channel == other_vector_channel

    other_name = ChannelName.G
    other_buffer_size = .25
    other_time_step = 0
    other_copy = False
    other_vector_channel = VectorChannel(
        data=vector_channel_empty_data,
        name=other_name,
        buffer_size=other_buffer_size,
        time_step=other_time_step,
        copy=other_copy,
    )

    assert vector_channel != other_vector_channel

    other_vector_channel = 'invalid'

    assert vector_channel != other_vector_channel


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

    assert inplace is False

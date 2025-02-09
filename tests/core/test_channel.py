import inspect
import pickle

import numpy as np
import numpy.typing as npt
import pytest

from aviary.core.channel import RasterChannel
from aviary.core.enums import ChannelName
from aviary.core.exceptions import AviaryUserError
from aviary.core.type_aliases import FractionalBufferSize
from tests.core.data.data_test_channel import data_test_raster_channel_init_exceptions


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


def test_raster_channel_copy(
    raster_channel: RasterChannel,
) -> None:
    copied_raster_channel = raster_channel.copy()

    assert copied_raster_channel == raster_channel
    assert copied_raster_channel.is_copied is True
    assert id(copied_raster_channel) != id(raster_channel)
    assert id(copied_raster_channel.data) != id(raster_channel.data)

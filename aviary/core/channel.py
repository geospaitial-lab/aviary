from __future__ import annotations

import weakref
from abc import (
    ABC,
    abstractmethod,
)
from collections.abc import (
    Iterable,
    Iterator,
)
from typing import (
    TYPE_CHECKING,
    overload,
)

import geopandas as gpd
import numpy as np
import numpy.typing as npt

# noinspection PyProtectedMember
from aviary._functional.utils.coordinates_filter import duplicates_filter

# noinspection PyProtectedMember
from aviary._utils.validators import validate_channel_name
from aviary.core.enums import (
    ChannelName,
    _coerce_channel_name,
)
from aviary.core.exceptions import AviaryUserError

if TYPE_CHECKING:
    from aviary.core.tiles import Tiles
    from aviary.core.type_aliases import (
        BufferSize,
        ChannelKey,
        Coordinates,
        CoordinatesSet,
        FractionalBufferSize,
        TileSize,
        TimeStep,
    )


class Channel(ABC, Iterable[object]):
    """Abstract class for channels

    Notes:
        - The `data` property returns a reference to the data
        - The dunder methods `__getitem__` and `__iter__` return or yield a reference to a data item

    Implemented channels:
        - `RasterChannel`: Contains batched raster data
        - `VectorChannel`: Contains batched vector data
    """
    _data: list[object]

    def __init__(
        self,
        data: object | list[object],
        name: ChannelName | str,
        buffer_size: FractionalBufferSize = 0.,
        time_step: TimeStep | None = None,
        copy: bool = False,
    ) -> None:
        """
        Parameters:
            data: Data
            name: Name
            buffer_size: Buffer size as a fraction of the spatial extent of the data
            time_step: Time step
            copy: If True, the data is copied during initialization
        """
        self._data = data
        self._name = name
        self._buffer_size = buffer_size
        self._time_step = time_step
        self._copy = copy

        self._validate()

        if self._copy:
            self._copy_data()

        self._observer_tiles = None

    def _validate(self) -> None:
        """Validates the channel."""
        self._coerce_data()
        self._validate_data()
        self._name = _coerce_channel_name(channel_name=self._name)
        validate_channel_name(
            channel_name=self._name,
            param_name='name',
            description='name',
        )
        self._validate_buffer_size()

    def _coerce_data(self) -> None:
        """Coerces `data`."""
        if not isinstance(self._data, list):
            self._data = [self._data]

    @abstractmethod
    def _validate_data(self) -> None:
        """Validates `data`."""

    @abstractmethod
    def _copy_data(self) -> None:
        """Copies `data`."""

    def _mark_as_copied(self) -> None:
        """Sets `_copy` to True if the data is copied before the initialization."""
        self._copy = True

    def _validate_buffer_size(self) -> None:
        """Validates `buffer_size`.

        Raises:
            AviaryUserError: Invalid `buffer_size` (the buffer size is not in the range [0, 0.5))
        """
        if self._buffer_size < 0 or self._buffer_size >= .5:  # noqa: PLR2004
            message = (
                'Invalid buffer_size! '
                'The buffer size must be in the range [0, 0.5).'
            )
            raise AviaryUserError(message)

    def _register_observer_tiles(
        self,
        observer_tiles: Tiles,
    ) -> None:
        """Registers the observer tiles.

        Parameters:
            observer_tiles: Observer tiles
        """
        self._observer_tiles = weakref.ref(observer_tiles)

    def _unregister_observer_tiles(self) -> None:
        """Unregisters the observer tiles."""
        self._observer_tiles = None

    @property
    @abstractmethod
    def data(self) -> list[object]:
        """
        Returns:
            Data
        """

    @property
    def name(self) -> ChannelName | str:
        """
        Returns:
            Name
        """
        return self._name

    @name.setter
    def name(
        self,
        name: ChannelName | str,
    ) -> None:
        """
        Parameters:
            name: Name
        """
        self._name = _coerce_channel_name(channel_name=name)
        validate_channel_name(
            channel_name=self._name,
            param_name='name',
            description='name',
        )

        if self._observer_tiles is None:
            return

        observer_tiles = self._observer_tiles()

        if observer_tiles is None:
            return

        # noinspection PyProtectedMember
        observer_tiles._validate()  # noqa: SLF001

    @property
    def buffer_size(self) -> FractionalBufferSize:
        """
        Returns:
            Buffer size as a fraction of the spatial extent of the data
        """
        return self._buffer_size

    @property
    def time_step(self) -> TimeStep | None:
        """
        Returns:
            Time step
        """
        return self._time_step

    @time_step.setter
    def time_step(
        self,
        time_step: TimeStep | None,
    ) -> None:
        """
        Parameters:
            time_step: Time step
        """
        self._time_step = time_step

        if self._observer_tiles is None:
            return

        observer_tiles = self._observer_tiles()

        if observer_tiles is None:
            return

        # noinspection PyProtectedMember
        observer_tiles._validate()  # noqa: SLF001

    @property
    def is_copied(self) -> bool:
        """
        Returns:
            If True, the data is copied during initialization
        """
        return self._copy

    @property
    def batch_size(self) -> int:
        """
        Returns:
            Batch size
        """
        return len(self)

    @property
    def is_in_tiles(self) -> bool:
        """
        Returns:
            True if the channel is inside tiles, False otherwise
        """
        if self._observer_tiles is None:
            return False

        return self._observer_tiles() is not None

    @property
    def key(self) -> ChannelKey:
        """
        Returns:
            Name and time step combination
        """
        return self._name, self._time_step

    @classmethod
    def from_channels(
        cls,
        channels: list[Channel],
        copy: bool = False,
    ) -> Channel:
        """Creates a channel from channels.

        Parameters:
            channels: Channels
            copy: If True, the data is copied during initialization

        Returns:
            Channel

        Raises:
            AviaryUserError: Invalid channels (the channels must contain at least one channel)
            AviaryUserError: Invalid channels (the names of the channels are not equal)
            AviaryUserError: Invalid channels (the buffer sizes of the channels are not equal)
            AviaryUserError: Invalid channels (the time steps of the channels are not equal)
        """
        if not channels:
            message = (
                'Invalid channels! '
                'The channels must contain at least one channel.'
            )
            raise AviaryUserError(message)

        channel_names = {channel.name for channel in channels}

        if len(channel_names) > 1:
            message = (
                'Invalid channels! '
                'The names of the channels must be equal.'
            )
            raise AviaryUserError(message)

        buffer_sizes = {channel.buffer_size for channel in channels}

        if len(buffer_sizes) > 1:
            message = (
                'Invalid channels! '
                'The buffer sizes of the channels must be equal.'
            )
            raise AviaryUserError(message)

        time_steps = {channel.time_step for channel in channels}

        if len(time_steps) > 1:
            message = (
                'Invalid channels! '
                'The time steps of the channels must be equal.'
            )
            raise AviaryUserError(message)

        first_channel = channels[0]

        data = [data_item for channel in channels for data_item in channel]
        name = first_channel.name
        buffer_size = first_channel.buffer_size
        time_step = first_channel.time_step
        return cls(
            data=data,
            name=name,
            buffer_size=buffer_size,
            time_step=time_step,
            copy=copy,
        )

    @abstractmethod
    def __repr__(self) -> str:
        """Returns the string representation.

        Returns:
            String representation
        """

    def __getstate__(self) -> dict:
        """Gets the state for pickling.

        Returns:
            State
        """
        state = self.__dict__.copy()
        state['_observer_tiles'] = None
        return state

    def __setstate__(
        self,
        state: dict,
    ) -> None:
        """Sets the state for unpickling.

        Parameters:
            state: State
        """
        self.__dict__ = state

    @abstractmethod
    def __eq__(
        self,
        other: object,
    ) -> bool:
        """Compares the channels.

        Parameters:
            other: Other channel

        Returns:
            True if the channels are equal, False otherwise
        """

    def __len__(self) -> int:
        """Computes the batch size.

        Returns:
            Batch size
        """
        return len(self._data)

    @overload
    def __getitem__(
        self,
        index: int,
    ) -> object:
        ...

    @overload
    def __getitem__(
        self,
        index: slice,
    ) -> list[object]:
        ...

    def __getitem__(
        self,
        index: int | slice,
    ) -> object | list[object]:
        """Returns the data item or the sliced data.

        Parameters:
            index: Index or slice of the data item

        Returns:
            Data item or data
        """
        return self._data[index]

    def __iter__(self) -> Iterator[object]:
        """Iterates over the data.

        Yields:
            Data item
        """
        yield from self._data

    def __add__(
        self,
        other: Channel,
    ) -> Channel:
        """Adds the channels.

        Parameters:
            other: Other channel

        Returns:
            Channel

        Raises:
            AviaryUserError: Invalid other (the names of the channels are not equal)
            AviaryUserError: Invalid other (the buffer sizes of the channels are not equal)
            AviaryUserError: Invalid other (the time steps of the channels are not equal)
        """
        if self._name != other.name:
            message = (
                'Invalid other! '
                'The names of the channels must be equal.'
            )
            raise AviaryUserError(message)

        if self._buffer_size != other.buffer_size:
            message = (
                'Invalid other! '
                'The buffer sizes of the channels must be equal.'
            )
            raise AviaryUserError(message)

        if self._time_step != other.time_step:
            message = (
                'Invalid other! '
                'The time steps of the channels must be equal.'
            )
            raise AviaryUserError(message)

        data = self._data + other.data
        return self.__class__(
            data=data,
            name=self._name,
            buffer_size=self._buffer_size,
            time_step=self._time_step,
            copy=True,
        )

    def append(
        self,
        data: object | list[object],
        inplace: bool = False,
    ) -> Channel:
        """Appends the data.

        Parameters:
            data: Data
            inplace: If True, the data is appended inplace

        Returns:
            Channel
        """
        if not isinstance(data, list):
            data = [data]

        if inplace:
            self._data.extend(data)
            self._validate()
            return self

        data = self._data + data
        return self.__class__(
            data=data,
            name=self._name,
            buffer_size=self._buffer_size,
            time_step=self._time_step,
            copy=True,
        )

    @abstractmethod
    def copy(self) -> Channel:
        """Copies the channel.

        Returns:
            Channel
        """

    @abstractmethod
    def remove_buffer(
        self,
        inplace: bool = False,
    ) -> Channel:
        """Removes the buffer.

        Parameters:
            inplace: If True, the buffer is removed inplace

        Returns:
            Channel
        """


class RasterChannel(Channel, Iterable[npt.NDArray]):
    """Channel that contains batched raster data

    Notes:
        - The data items are assumed to be in shape (n, n), where n is the spatial extent in x and y direction
        - The `data` property returns a reference to the data
        - The dunder methods `__getitem__` and `__iter__` return or yield a reference to a data item
    """
    _data: list[npt.NDArray]

    def __init__(
        self,
        data: npt.NDArray | list[npt.NDArray],
        name: ChannelName | str,
        buffer_size: FractionalBufferSize = 0.,
        time_step: TimeStep | None = None,
        copy: bool = False,
    ) -> None:
        """
        Parameters:
            data: Data
            name: Name
            buffer_size: Buffer size as a fraction of the spatial extent of the data
            time_step: Time step
            copy: If True, the data is copied during initialization
        """
        super().__init__(
            data=data,
            name=name,
            buffer_size=buffer_size,
            time_step=time_step,
            copy=copy,
        )

        self._buffer_size_pixels = self._compute_buffer_size_pixels()

    def _validate_data(self) -> None:
        """Validates `data`.

        Raises:
            AviaryUserError: Invalid `data` (the data contains no data items)
        """
        if len(self._data) == 0:
            message = (
                'Invalid data! '
                'The data must contain at least one data item.'
            )
            raise AviaryUserError(message)

        for data_item in self:
            self._validate_data_item(data_item=data_item)

    def _validate_data_item(
        self,
        data_item: npt.NDArray,
    ) -> None:
        """Validates the data item.

        Parameters:
            data_item: Data item

        Raises:
            AviaryUserError: Invalid `data` (the data item is not in shape (n, n))
            AviaryUserError: Invalid `data` (the shapes of the data items are not equal)
        """
        first_data_item = self[0]

        if data_item.ndim != 2:  # noqa: PLR2004
            message = (
                'Invalid data! '
                'The data item must be in shape (n, n).'
            )
            raise AviaryUserError(message)

        if data_item.shape[0] != data_item.shape[1]:
            message = (
                'Invalid data! '
                'The data item must be in shape (n, n).'
            )
            raise AviaryUserError(message)

        if data_item.shape != first_data_item.shape:
            message = (
                'Invalid data! '
                'The shapes of the data items must be equal.'
            )
            raise AviaryUserError(message)

    def _copy_data(self) -> None:
        """Copies `data`."""
        self._data = [data_item.copy() for data_item in self]

    def _compute_buffer_size_pixels(self) -> BufferSize:
        """Computes the buffer size in pixels.

        Returns:
            Buffer size in pixels

        Raises:
            AviaryUserError: Invalid `buffer_size` (the buffer size does not match the spatial extent of the data,
                resulting in a fractional number of pixels)
        """
        buffer_size_pixels = self._buffer_size * self[0].shape[0] / (1. + 2. * self._buffer_size)

        if not buffer_size_pixels.is_integer():
            message = (
                'Invalid buffer_size! '
                'The buffer size must must match the spatial extent of the data, '
                'resulting in a whole number of pixels.'
            )
            raise AviaryUserError(message)

        return int(buffer_size_pixels)

    @property
    def data(self) -> list[npt.NDArray]:
        """
        Returns:
            Data
        """
        return self._data

    @classmethod
    def from_channels(
        cls,
        channels: list[RasterChannel],
        copy: bool = False,
    ) -> RasterChannel:
        """Creates a raster channel from raster channels.

        Parameters:
            channels: Raster channels
            copy: If True, the data is copied during initialization

        Returns:
            Raster channel
        """
        return super().from_channels(
            channels=channels,
            copy=copy,
        )

    def __repr__(self) -> str:
        """Returns the string representation.

        Returns:
            String representation
        """
        data_repr = len(self)
        return (
            'RasterChannel(\n'
            f'    data={data_repr},\n'
            f'    name={self._name},\n'
            f'    buffer_size={self._buffer_size},\n'
            f'    time_step={self._time_step},\n'
            f'    copy={self._copy},\n'
            ')'
        )

    def __getstate__(self) -> dict:
        """Gets the state for pickling.

        Returns:
            State
        """
        return super().__getstate__()

    def __setstate__(
        self,
        state: dict,
    ) -> None:
        """Sets the state for unpickling.

        Parameters:
            state: State
        """
        super().__setstate__(state=state)

    def __eq__(
        self,
        other: object,
    ) -> bool:
        """Compares the raster channels.

        Parameters:
            other: Other raster channel

        Returns:
            True if the raster channels are equal, False otherwise
        """
        if not isinstance(other, RasterChannel):
            return False

        conditions = [
            len(self) == len(other),
            all(
                np.array_equal(data_item, other_data_item)
                for data_item, other_data_item in zip(self, other, strict=False)
            ),
            self._name == other.name,
            self._buffer_size == other.buffer_size,
            self._time_step == other.time_step,
        ]
        return all(conditions)

    @overload
    def __getitem__(
        self,
        index: int,
    ) -> npt.NDArray:
        ...

    @overload
    def __getitem__(
        self,
        index: slice,
    ) -> list[npt.NDArray]:
        ...

    def __getitem__(
        self,
        index: int | slice,
    ) -> npt.NDArray | list[npt.NDArray]:
        """Returns the data item.

        Parameters:
            index: Index or slice of the data item

        Returns:
            Data item or sliced data
        """
        return super().__getitem__(index=index)

    def __iter__(self) -> Iterator[npt.NDArray]:
        """Iterates over the data.

        Yields:
            Data item
        """
        return super().__iter__()

    def __add__(
        self,
        other: RasterChannel,
    ) -> RasterChannel:
        """Adds the raster channels.

        Parameters:
            other: Other raster channel

        Returns:
            Raster channel
        """
        return super().__add__(other=other)

    def append(
        self,
        data: npt.NDArray | list[npt.NDArray],
        inplace: bool = False,
    ) -> RasterChannel:
        """Appends the data.

        Parameters:
            data: Data
            inplace: If True, the data is appended inplace

        Returns:
            Raster channel
        """
        return super().append(
            data=data,
            inplace=inplace,
        )

    def copy(self) -> RasterChannel:
        """Copies the raster channel.

        Returns:
            Raster channel
        """
        return RasterChannel(
            data=self._data,
            name=self._name,
            buffer_size=self._buffer_size,
            time_step=self._time_step,
            copy=True,
        )

    def remove_buffer(
        self,
        inplace: bool = False,
    ) -> RasterChannel:
        """Removes the buffer.

        Parameters:
            inplace: If True, the buffer is removed inplace

        Returns:
            Raster channel
        """
        if self._buffer_size == 0.:
            if inplace:
                return self

            return self.copy()

        if inplace:
            self._data = [
                self._remove_buffer_item(data_item=data_item)
                for data_item in self
            ]
            self._buffer_size = 0.
            self._validate()
            self._buffer_size_pixels = self._compute_buffer_size_pixels()
            return self

        data = [
            self._remove_buffer_item(data_item=data_item)
            for data_item in self
        ]
        buffer_size = 0.
        return RasterChannel(
            data=data,
            name=self._name,
            buffer_size=buffer_size,
            time_step=self._time_step,
            copy=True,
        )

    def _remove_buffer_item(
        self,
        data_item: npt.NDArray,
    ) -> npt.NDArray:
        """Removes the buffer from the data item.

        Parameters:
            data_item: Data item

        Returns:
            Data item
        """
        return data_item[
            self._buffer_size_pixels:-self._buffer_size_pixels,
            self._buffer_size_pixels:-self._buffer_size_pixels,
        ]


class VectorChannel(Channel, Iterable[gpd.GeoDataFrame]):
    """Channel that contains batched vector data

    Notes:
        - The data items are assumed to be normalized to the spatial extent [0, 1] in x and y direction
            without a coordinate reference system
        - The `data` property returns a reference to the data
        - The dunder methods `__getitem__` and `__iter__` return or yield a reference to a data item
    """
    _data: list[gpd.GeoDataFrame]

    def __init__(
        self,
        data: gpd.GeoDataFrame | list[gpd.GeoDataFrame],
        name: ChannelName | str,
        buffer_size: FractionalBufferSize = 0.,
        time_step: TimeStep | None = None,
        copy: bool = False,
    ) -> None:
        """
        Parameters:
            data: Data
            name: Name
            buffer_size: Buffer size as a fraction of the spatial extent of the data
            time_step: Time step
            copy: If True, the data is copied during initialization
        """
        super().__init__(
            data=data,
            name=name,
            buffer_size=buffer_size,
            time_step=time_step,
            copy=copy,
        )

        self._buffer_size_coordinate_units = self._compute_buffer_size_coordinate_units()
        self._unbuffered_bounding_box = self._compute_unbuffered_bounding_box()

    def _validate_data(self) -> None:
        """Validates `data`.

        Raises:
            AviaryUserError: Invalid `data` (the data contains no data items)
        """
        if not self._data:
            message = (
                'Invalid data! '
                'The data must contain at least one data item.'
            )
            raise AviaryUserError(message)

        for data_item in self:
            self._validate_data_item(data_item=data_item)

    @staticmethod
    def _validate_data_item(
        data_item: gpd.GeoDataFrame,
    ) -> None:
        """Validates the data item.

        Parameters:
            data_item: Data item

        Raises:
            AviaryUserError: Invalid `data` (the data item has a coordinate reference system)
            AviaryUserError: Invalid `data` (the data item is not normalized to the spatial extent [0, 1]
                in x and y direction)
        """
        if data_item.empty:
            return

        if data_item.crs is not None:
            message = (
                'Invalid data! '
                'The data item must not have a coordinate reference system.'
            )
            raise AviaryUserError(message)

        x_min, y_min, x_max, y_max = data_item.total_bounds
        conditions = [
            x_min < 0.,
            y_min < 0.,
            x_max > 1.,
            y_max > 1.,
        ]

        if any(conditions):
            message = (
                'Invalid data! '
                'The data item must be normalized to the spatial extent [0, 1] in x and y direction.'
            )
            raise AviaryUserError(message)

    def _copy_data(self) -> None:
        """Copies `data`."""
        self._data = [data_item.copy() for data_item in self]

    def _compute_buffer_size_coordinate_units(self) -> BufferSize:
        """Computes the buffer size in coordinate units.

        Returns:
            Buffer size in coordinate units
        """
        return self._buffer_size / (1. + 2. * self._buffer_size)

    def _compute_unbuffered_bounding_box(self) -> tuple[float, float, float, float]:
        """Computes the unbuffered bounding box.

        Returns:
            Bounding box
        """
        x_min = 0. + self._buffer_size_coordinate_units
        y_min = 0. + self._buffer_size_coordinate_units
        x_max = 1. - self._buffer_size_coordinate_units
        y_max = 1. - self._buffer_size_coordinate_units
        return x_min, y_min, x_max, y_max

    @staticmethod
    def _scale_data_item(
        data_item: gpd.GeoDataFrame,
        bounding_box: tuple[float, float, float, float],
        new_bounding_box: tuple[float, float, float, float],
    ) -> gpd.GeoDataFrame:
        """Scales the data item to the spatial extent [0, 1] in x and y direction.

        Parameters:
            data_item: Data item
            bounding_box: Bounding box
            new_bounding_box: New bounding box

        Returns:
            Data item
        """
        source_size = bounding_box[2] - bounding_box[0]
        target_size = new_bounding_box[2] - new_bounding_box[0]

        scale = target_size / source_size

        translate_x = new_bounding_box[0] - bounding_box[0] * scale
        translate_y = new_bounding_box[1] - bounding_box[1] * scale

        transform = [scale, 0., 0., scale, translate_x, translate_y]
        data_item.geometry = data_item.geometry.affine_transform(transform)
        return data_item

    @property
    def data(self) -> list[gpd.GeoDataFrame]:
        """
        Returns:
            Data
        """
        return self._data

    @classmethod
    def from_channels(
        cls,
        channels: list[VectorChannel],
        copy: bool = False,
    ) -> VectorChannel:
        """Creates a vector channel from vector channels.

        Parameters:
            channels: Vector channels
            copy: If True, the data is copied during initialization

        Returns:
            Vector channel
        """
        return super().from_channels(
            channels=channels,
            copy=copy,
        )

    @classmethod
    def from_unnormalized_data(  # noqa: C901
        cls,
        data: gpd.GeoDataFrame | list[gpd.GeoDataFrame],
        name: ChannelName | str,
        coordinates: Coordinates | CoordinatesSet,
        tile_size: TileSize,
        buffer_size: BufferSize = 0,
        time_step: TimeStep | None = None,
        copy: bool = False,
    ) -> VectorChannel:
        """Creates a vector channel from unnormalized data.

        Parameters:
            data: Data
            name: Name
            coordinates: Coordinates (x_min, y_min) of the tile or of each tile in meters
            tile_size: Tile size in meters
            buffer_size: Buffer size in meters
            time_step: Time step
            copy: If True, the data is copied during initialization

        Raises:
            AviaryUserError: Invalid `data` (the data contains no data items)
            AviaryUserError: Invalid `coordinates` (the coordinates are not in shape (n, 2) and data type int32)
            AviaryUserError: Invalid `coordinates` (the coordinates contain duplicate coordinates)
            AviaryUserError: Invalid `coordinates` (the number of coordinates is not equal to the number of data items)
            AviaryUserError: Invalid `tile_size` (the tile size is negative or zero)
            AviaryUserError: Invalid `buffer_size` (the buffer size is negative)
        """
        if not isinstance(data, list):
            data = [data]

        if not data:
            message = (
                'Invalid data! '
                'The data must contain at least one data item.'
            )
            raise AviaryUserError(message)

        if not isinstance(coordinates, np.ndarray):
            coordinates = np.array([coordinates], dtype=np.int32)

        if coordinates.ndim != 2:  # noqa: PLR2004
            message = (
                'Invalid coordinates! '
                'The coordinates must be in shape (n, 2) and data type int32.'
            )
            raise AviaryUserError(message)

        conditions = [
            coordinates.shape[1] != 2,  # noqa: PLR2004
            coordinates.dtype != np.int32,
        ]

        if any(conditions):
            message = (
                'Invalid coordinates! '
                'The coordinates must be in shape (n, 2) and data type int32.'
            )
            raise AviaryUserError(message)

        unique_coordinates = duplicates_filter(coordinates=coordinates)

        if len(coordinates) != len(unique_coordinates):
            message = (
                'Invalid coordinates! '
                'The coordinates must contain unique coordinates.'
            )
            raise AviaryUserError(message)

        if len(coordinates) != len(data):
            message = (
                'Invalid coordinates! '
                'The number of coordinates must be equal to the number of data items.'
            )
            raise AviaryUserError(message)

        if tile_size <= 0:
            message = (
                'Invalid tile_size! '
                'The tile size must be positive.'
            )
            raise AviaryUserError(message)

        if buffer_size < 0:
            message = (
                'Invalid buffer_size! '
                'The buffer size must be positive or zero.'
            )
            raise AviaryUserError(message)

        if copy:
            data = [data_item.copy() for data_item in data]

        coordinates = [
            (int(x_min), int(y_min))
            for x_min, y_min in coordinates
        ]
        data = [
            cls._from_unnormalized_data_item(
                data_item=data_item,
                coordinates=coordinates_item,
                tile_size=tile_size,
                buffer_size=buffer_size,
            )
            for data_item, coordinates_item in zip(data, coordinates, strict=True)
        ]
        buffer_size = buffer_size / tile_size
        vector_channel = cls(
            data=data,
            name=name,
            buffer_size=buffer_size,
            time_step=time_step,
            copy=False,
        )

        if copy:
            vector_channel._mark_as_copied()

        return vector_channel

    @classmethod
    def _from_unnormalized_data_item(
        cls,
        data_item: gpd.GeoDataFrame,
        coordinates: Coordinates,
        tile_size: TileSize,
        buffer_size: BufferSize = 0,
    ) -> gpd.GeoDataFrame:
        """Creates a data item from an unnormalized data item.

        Parameters:
            data_item: Data item
            coordinates: Coordinates (x_min, y_min) of the tile in meters
            tile_size: Tile size in meters
            buffer_size: Buffer size in meters

        Returns:
            Data item
        """
        data_item = data_item.set_crs(
            crs=None,
            allow_override=True,
        )

        if data_item.empty:
            return data_item

        bounding_box = (
            float(coordinates[0] - buffer_size),
            float(coordinates[1] - buffer_size),
            float(coordinates[0] + tile_size + buffer_size),
            float(coordinates[1] + tile_size + buffer_size),
        )
        new_bounding_box = (0., 0., 1., 1.)
        return cls._scale_data_item(
            data_item=data_item,
            bounding_box=bounding_box,
            new_bounding_box=new_bounding_box,
        )

    def __repr__(self) -> str:
        """Returns the string representation.

        Returns:
            String representation
        """
        data_repr = len(self)
        return (
            'VectorChannel(\n'
            f'    data={data_repr},\n'
            f'    name={self._name},\n'
            f'    buffer_size={self._buffer_size},\n'
            f'    time_step={self._time_step},\n'
            f'    copy={self._copy},\n'
            ')'
        )

    def __getstate__(self) -> dict:
        """Gets the state for pickling.

        Returns:
            State
        """
        return super().__getstate__()

    def __setstate__(
        self,
        state: dict,
    ) -> None:
        """Sets the state for unpickling.

        Parameters:
            state: State
        """
        super().__setstate__(state=state)

    def __eq__(
        self,
        other: object,
    ) -> bool:
        """Compares the vector channels.

        Parameters:
            other: Other vector channel

        Returns:
            True if the vector channels are equal, False otherwise
        """
        if not isinstance(other, VectorChannel):
            return False

        conditions = [
            len(self) == len(other),
            all(
                data_item.equals(other_data_item)
                for data_item, other_data_item in zip(self, other, strict=False)
            ),
            self._name == other.name,
            self._buffer_size == other.buffer_size,
            self._time_step == other.time_step,
        ]
        return all(conditions)

    @overload
    def __getitem__(
        self,
        index: int,
    ) -> gpd.GeoDataFrame:
        ...

    @overload
    def __getitem__(
        self,
        index: slice,
    ) -> list[gpd.GeoDataFrame]:
        ...

    def __getitem__(
        self,
        index: int | slice,
    ) -> gpd.GeoDataFrame | list[gpd.GeoDataFrame]:
        """Returns the data item.

        Parameters:
            index: Index or slice of the data item

        Returns:
            Data item or sliced data
        """
        return super().__getitem__(index=index)

    def __iter__(self) -> Iterator[gpd.GeoDataFrame]:
        """Iterates over the data.

        Yields:
            Data item
        """
        return super().__iter__()

    def __add__(
        self,
        other: VectorChannel,
    ) -> VectorChannel:
        """Adds the vector channels.

        Parameters:
            other: Other vector channel

        Returns:
            Vector channel
        """
        return super().__add__(other=other)

    def append(
        self,
        data: gpd.GeoDataFrame | list[gpd.GeoDataFrame],
        inplace: bool = False,
    ) -> VectorChannel:
        """Appends the data.

        Parameters:
            data: Data
            inplace: If True, the data is appended inplace

        Returns:
            Vector channel
        """
        return super().append(
            data=data,
            inplace=inplace,
        )

    def copy(self) -> VectorChannel:
        """Copies the vector channel.

        Returns:
            Vector channel
        """
        return VectorChannel(
            data=self._data,
            name=self._name,
            buffer_size=self._buffer_size,
            time_step=self._time_step,
            copy=True,
        )

    def remove_buffer(
        self,
        inplace: bool = False,
    ) -> VectorChannel:
        """Removes the buffer.

        Parameters:
            inplace: If True, the buffer is removed inplace

        Returns:
            Vector channel
        """
        if self._buffer_size == 0.:
            if inplace:
                return self

            return self.copy()

        if inplace:
            self._data = [
                self._remove_buffer_item(data_item=data_item)
                for data_item in self
            ]
            self._buffer_size = 0.
            self._validate()
            self._buffer_size_coordinate_units = self._compute_buffer_size_coordinate_units()
            self._unbuffered_bounding_box = self._compute_unbuffered_bounding_box()
            return self

        data = [
            self._remove_buffer_item(data_item=data_item)
            for data_item in self
        ]
        buffer_size = 0.
        vector_channel = VectorChannel(
            data=data,
            name=self._name,
            buffer_size=buffer_size,
            time_step=self._time_step,
            copy=False,
        )
        vector_channel._mark_as_copied()
        return vector_channel

    def _remove_buffer_item(
        self,
        data_item: gpd.GeoDataFrame,
    ) -> gpd.GeoDataFrame:
        """Removes the buffer from the data item.

        Parameters:
            data_item: Data item

        Returns:
            Data item
        """
        if data_item.empty:
            return data_item.copy()

        bounding_box = self._unbuffered_bounding_box
        new_bounding_box = (0., 0., 1., 1.)

        data_item = data_item.clip(
            mask=self._unbuffered_bounding_box,
            keep_geom_type=True,
        )
        data_item = data_item.reset_index(drop=True)
        return self._scale_data_item(
            data_item=data_item,
            bounding_box=bounding_box,
            new_bounding_box=new_bounding_box,
        )

    def to_denormalized_data(
        self,
        coordinates: CoordinatesSet,
        tile_size: TileSize,
    ) -> list[gpd.GeoDataFrame]:
        """Converts the data to denormalized data.

        Parameters:
            coordinates: Coordinates (x_min, y_min) of each tile in meters
            tile_size: Tile size in meters

        Returns:
            Data

        Raises:
            AviaryUserError: Invalid `coordinates` (the coordinates are not in shape (n, 2) and data type int32)
            AviaryUserError: Invalid `coordinates` (the coordinates contain duplicate coordinates)
            AviaryUserError: Invalid `coordinates` (the number of coordinates is not equal to the number of data items)
            AviaryUserError: Invalid `tile_size` (the tile size is negative or zero)
        """
        if coordinates.ndim != 2:  # noqa: PLR2004
            message = (
                'Invalid coordinates! '
                'The coordinates must be in shape (n, 2) and data type int32.'
            )
            raise AviaryUserError(message)

        conditions = [
            coordinates.shape[1] != 2,  # noqa: PLR2004
            coordinates.dtype != np.int32,
        ]

        if any(conditions):
            message = (
                'Invalid coordinates! '
                'The coordinates must be in shape (n, 2) and data type int32.'
            )
            raise AviaryUserError(message)

        unique_coordinates = duplicates_filter(coordinates=coordinates)

        if len(coordinates) != len(unique_coordinates):
            message = (
                'Invalid coordinates! '
                'The coordinates must contain unique coordinates.'
            )
            raise AviaryUserError(message)

        if len(coordinates) != len(self):
            message = (
                'Invalid coordinates! '
                'The number of coordinates must be equal to the number of data items.'
            )
            raise AviaryUserError(message)

        if tile_size <= 0:
            message = (
                'Invalid tile_size! '
                'The tile size must be positive.'
            )
            raise AviaryUserError(message)

        data = [data_item.copy() for data_item in self]

        coordinates = [
            (int(x_min), int(y_min))
            for x_min, y_min in coordinates
        ]
        buffer_size = self._buffer_size * tile_size
        return [
            self._to_denormalized_data_item(
                data_item=data_item,
                coordinates=coordinates_item,
                tile_size=tile_size,
                buffer_size=buffer_size,
            )
            for data_item, coordinates_item in zip(data, coordinates, strict=True)
        ]

    def _to_denormalized_data_item(
        self,
        data_item: gpd.GeoDataFrame,
        coordinates: Coordinates,
        tile_size: TileSize,
        buffer_size: BufferSize = 0,
    ) -> gpd.GeoDataFrame:
        """Converts the data item to a denormalized data item.

        Parameters:
            data_item: Data item
            coordinates: Coordinates (x_min, y_min) of the tile in meters
            tile_size: Tile size in meters
            buffer_size: Buffer size in meters

        Returns:
            Data item
        """
        if data_item.empty:
            return data_item

        bounding_box = (0., 0., 1., 1.)
        new_bounding_box = (
            float(coordinates[0] - buffer_size),
            float(coordinates[1] - buffer_size),
            float(coordinates[0] + tile_size + buffer_size),
            float(coordinates[1] + tile_size + buffer_size),
        )
        return self._scale_data_item(
            data_item=data_item,
            bounding_box=bounding_box,
            new_bounding_box=new_bounding_box,
        )

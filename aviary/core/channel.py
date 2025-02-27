from __future__ import annotations

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

from aviary.core.enums import (
    ChannelName,
    _parse_channel_name,
)
from aviary.core.exceptions import AviaryUserError

if TYPE_CHECKING:
    from aviary.core.type_aliases import (
        BufferSize,
        ChannelKey,
        Coordinates,
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

    def _validate(self) -> None:
        """Validates the channel."""
        self._parse_data()
        self._validate_data()
        self._name = _parse_channel_name(channel_name=self._name)
        self._validate_buffer_size()

    def _parse_data(self) -> None:
        """Parses `data`."""
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

    @property
    @abstractmethod
    def data(self) -> object:
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
    def key(self) -> ChannelKey:
        """
        Returns:
            Name and time step combination
        """
        return self._name, self._time_step

    @abstractmethod
    def __repr__(self) -> str:
        """Returns the string representation.

        Returns:
            String representation
        """

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
    def data(self) -> npt.NDArray:
        """
        Returns:
            Data
        """
        return self._data

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

            return RasterChannel(
                data=self._data,
                name=self._name,
                buffer_size=self._buffer_size,
                time_step=self._time_step,
                copy=True,
            )

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
        - The data items are assumed to be scaled to the spatial extent [0, 1] in x and y direction
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
            AviaryUserError: Invalid `data` (the data item is not scaled to the spatial extent [0, 1]
                in x and y direction)
        """
        if data_item.crs is not None:
            message = (
                'Invalid data! '
                'The data item must not have a coordinate reference system.'
            )
            raise AviaryUserError(message)

        if data_item.empty:
            return

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
                'The data item must be scaled to the spatial extent [0, 1] in x and y direction.'
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
        source_bounding_box: tuple[float, float, float, float],
        target_bounding_box: tuple[float, float, float, float],
    ) -> gpd.GeoDataFrame:
        """Scales the data item to the spatial extent [0, 1] in x and y direction.

        Parameters:
            data_item: Data item
            source_bounding_box: Source bounding box
            target_bounding_box: Target bounding box

        Returns:
            Data item
        """
        source_size = source_bounding_box[2] - source_bounding_box[0]
        target_size = target_bounding_box[2] - target_bounding_box[0]

        scale = target_size / source_size

        translate_x = target_bounding_box[0] - source_bounding_box[0] * scale
        translate_y = target_bounding_box[1] - source_bounding_box[1] * scale

        transform = [scale, 0., 0., scale, translate_x, translate_y]
        data_item.geometry = data_item.geometry.affine_transform(transform)
        return data_item

    @property
    def data(self) -> gpd.GeoDataFrame:
        """
        Returns:
            Data
        """
        return self._data

    @classmethod
    def from_unscaled_data(
        cls,
        data: gpd.GeoDataFrame | list[gpd.GeoDataFrame],
        name: ChannelName | str,
        coordinates: Coordinates,
        tile_size: TileSize,
        buffer_size: BufferSize = 0,
        time_step: TimeStep | None = None,
        copy: bool = False,
    ) -> VectorChannel:
        """Creates a vector channel from unscaled data.

        Parameters:
            data: Data
            name: Name
            coordinates: Coordinates (x_min, y_min) of the tile in meters
            tile_size: Tile size in meters
            buffer_size: Buffer size in meters
            time_step: Time step
            copy: If True, the data is copied during initialization

        Raises:
            AviaryUserError: Invalid `data` (the data contains no data items)
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

        data = [
            cls._from_unscaled_data_item(
                data_item=data_item,
                coordinates=coordinates,
                tile_size=tile_size,
                buffer_size=buffer_size,
            )
            for data_item in data
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
            vector_channel._mark_as_copied()  # noqa: SLF001

        return vector_channel

    @classmethod
    def _from_unscaled_data_item(
        cls,
        data_item: gpd.GeoDataFrame,
        coordinates: Coordinates,
        tile_size: TileSize,
        buffer_size: BufferSize = 0,
    ) -> gpd.GeoDataFrame:
        """Creates a data item from unscaled data.

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

        source_bounding_box = (
            float(coordinates[0] - buffer_size),
            float(coordinates[1] - buffer_size),
            float(coordinates[0] + tile_size + buffer_size),
            float(coordinates[1] + tile_size + buffer_size),
        )
        target_bounding_box = (0., 0., 1., 1.)
        return cls._scale_data_item(
            data_item=data_item,
            source_bounding_box=source_bounding_box,
            target_bounding_box=target_bounding_box,
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

            return VectorChannel(
                data=self._data,
                name=self._name,
                buffer_size=self._buffer_size,
                time_step=self._time_step,
                copy=True,
            )

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
        vector_channel._mark_as_copied()  # noqa: SLF001
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

        source_bounding_box = self._unbuffered_bounding_box
        target_bounding_box = (0., 0., 1., 1.)

        data_item = data_item.clip(  # returns a copy
            mask=self._unbuffered_bounding_box,
            keep_geom_type=True,
        )
        data_item = data_item.reset_index(drop=True)
        return self._scale_data_item(
            data_item=data_item,
            source_bounding_box=source_bounding_box,
            target_bounding_box=target_bounding_box,
        )

from __future__ import annotations

from abc import (
    ABC,
    abstractmethod,
)
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    import geopandas as gpd
    import numpy.typing as npt

from aviary.core.enums import ChannelName
from aviary.core.exceptions import AviaryUserError

if TYPE_CHECKING:
    from aviary.core.type_aliases import (
        BufferSize,
        Coordinates,
        FractionalBufferSize,
        TileSize,
        TimeStep,
    )


class Channel(ABC):
    """Abstract class for channels

    Notes:
        - The `data` property returns a reference to the data

    Implemented channels:
        - `RasterChannel`: Contains raster data
        - `VectorChannel`: Contains vector data
    """
    _built_in_channel_names = frozenset(channel_name.value for channel_name in ChannelName)

    def __init__(
        self,
        data: object,
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
        self._validate_data()
        self._cast_name()
        self._validate_buffer_size()

    @abstractmethod
    def _validate_data(self) -> None:
        """Validates `data`."""

    @abstractmethod
    def _copy_data(self) -> None:
        """Copies `data`."""

    def _mark_as_copied(self) -> None:
        """Sets `_copy` to True if the data is copied before the initialization."""
        self._copy = True

    def _cast_name(self) -> None:
        """Casts the name to `ChannelName`."""
        if isinstance(self._name, str) and self._name in self._built_in_channel_names:
            self._name = ChannelName(self._name)

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


class RasterChannel(Channel):
    """Channel that contains raster data

    Notes:
        - The data is assumed to be in shape (n, n), where n is the spatial extent in x and y direction
        - The `data` property returns a reference to the data
    """
    _data: npt.NDArray

    def __init__(
        self,
        data: npt.NDArray,
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
            AviaryUserError: Invalid `data` (the data is not in shape (n, n))
        """
        conditions = [
            self._data.ndim != 2,  # noqa: PLR2004
            self._data.shape[0] != self._data.shape[1],
        ]

        if any(conditions):
            message = (
                'Invalid data! '
                'The data must be in shape (n, n).'
            )
            raise AviaryUserError(message)

    def _copy_data(self) -> None:
        """Copies `data`."""
        self._data = self._data.copy()

    def _compute_buffer_size_pixels(self) -> BufferSize:
        """Computes the buffer size in pixels.

        Returns:
            Buffer size

        Raises:
            AviaryUserError: Invalid `buffer_size` (the buffer size does not match the spatial extent of the data,
                resulting in a fractional number of pixels)
        """
        buffer_size_pixels = self._buffer_size * self._data.shape[0]

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
        data_repr = self._data.shape
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
        other: RasterChannel,
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
            np.array_equal(self._data, other.data),
            self._name == other.name,
            self._buffer_size == other.buffer_size,
            self._time_step == other.time_step,
        ]
        return all(conditions)

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
            self._data = self._data[
                self._buffer_size_pixels:-self._buffer_size_pixels,
                self._buffer_size_pixels:-self._buffer_size_pixels,
            ]
            self._buffer_size = 0.
            self._validate()
            self._buffer_size_pixels = self._compute_buffer_size_pixels()
            return self

        data = self._data[
            self._buffer_size_pixels:-self._buffer_size_pixels,
            self._buffer_size_pixels:-self._buffer_size_pixels,
        ]
        buffer_size = 0.
        return RasterChannel(
            data=data,
            name=self._name,
            buffer_size=buffer_size,
            time_step=self._time_step,
            copy=True,
        )


class VectorChannel(Channel):
    """Channel that contains vector data

    Notes:
        - The data is assumed to be scaled to the spatial extent [0, 1] in x and y direction
        - The `data` property returns a reference to the data
    """
    _data: gpd.GeoDataFrame

    def __init__(
        self,
        data: gpd.GeoDataFrame,
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
            AviaryUserError: Invalid `data` (the data is not scaled to the spatial extent [0, 1] in x and y direction)
        """
        if len(self._data) == 0:
            return

        x_min, y_min, x_max, y_max = self._data.total_bounds
        conditions = [
            x_min < 0.,
            y_min < 0.,
            x_max > 1.,
            y_max > 1.,
        ]

        if any(conditions):
            message = (
                'Invalid data! '
                'The data must be scaled to the spatial extent [0, 1] in x and y direction.'
            )
            raise AviaryUserError(message)

    def _copy_data(self) -> None:
        """Copies `data`."""
        self._data = self._data.copy()

    def _compute_buffer_size_coordinate_units(self) -> BufferSize:
        """Computes the buffer size in coordinate units.

        Returns:
            Buffer size
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
        data: gpd.GeoDataFrame,
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
            AviaryUserError: Invalid `tile_size` (the tile size is negative or zero)
            AviaryUserError: Invalid `buffer_size` (the buffer size is negative)
        """
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
            data = data.copy()

        source_bounding_box = (
            float(coordinates[0] - buffer_size),
            float(coordinates[1] - buffer_size),
            float(coordinates[0] + tile_size + buffer_size),
            float(coordinates[1] + tile_size + buffer_size),
        )
        target_bounding_box = (0., 0., 1., 1.)
        data = cls._scale_data(
            data=data,
            source_bounding_box=source_bounding_box,
            target_bounding_box=target_bounding_box,
            inplace=True,
        )
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

    def __repr__(self) -> str:
        """Returns the string representation.

        Returns:
            String representation
        """
        data_repr = len(self._data)
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
        other: VectorChannel,
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
            self._data.equals(other.data),
            self._name == other.name,
            self._buffer_size == other.buffer_size,
            self._time_step == other.time_step,
        ]
        return all(conditions)

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
        if len(self._data) == 0:
            if inplace:
                self._buffer_size = 0.
                self._validate()
                self._buffer_size_coordinate_units = self._compute_buffer_size_coordinate_units()
                self._unbuffered_bounding_box = self._compute_unbuffered_bounding_box()
                return self

            buffer_size = 0.
            return VectorChannel(
                data=self._data,
                name=self._name,
                buffer_size=buffer_size,
                time_step=self._time_step,
                copy=True,
            )

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

        source_bounding_box = self._unbuffered_bounding_box
        target_bounding_box = (0., 0., 1., 1.)

        if inplace:
            self._data = self._data.clip(
                mask=self._unbuffered_bounding_box,
                keep_geom_type=True,
            )
            self._data = self._scale_data(
                data=self._data,
                source_bounding_box=source_bounding_box,
                target_bounding_box=target_bounding_box,
                inplace=True,
            )
            self._buffer_size = 0.
            self._validate()
            self._buffer_size_coordinate_units = self._compute_buffer_size_coordinate_units()
            self._unbuffered_bounding_box = self._compute_unbuffered_bounding_box()
            return self

        data = self._data.clip(  # returns a copy
            mask=list(self._unbuffered_bounding_box),
            keep_geom_type=True,
        )
        data = self._scale_data(
            data=data,
            source_bounding_box=source_bounding_box,
            target_bounding_box=target_bounding_box,
            inplace=True,
        )
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

    @staticmethod
    def _scale_data(
        data: gpd.GeoDataFrame,
        source_bounding_box: tuple[float, float, float, float],
        target_bounding_box: tuple[float, float, float, float],
        inplace: bool = False,
    ) -> gpd.GeoDataFrame:
        """Scales the data to the spatial extent [0, 1] in x and y direction.

        Parameters:
            data: Data
            source_bounding_box: Source bounding box
            target_bounding_box: Target bounding box
            inplace: If True, the data is scaled inplace

        Returns:
            Data
        """
        if not inplace:
            data = data.copy()

        source_size = source_bounding_box[2] - source_bounding_box[0]
        target_size = target_bounding_box[2] - target_bounding_box[0]

        scale = target_size / source_size

        translate_x = target_bounding_box[0] - source_bounding_box[0] * scale
        translate_y = target_bounding_box[1] - source_bounding_box[1] * scale

        transform = [scale, 0., 0., scale, translate_x, translate_y]
        data['geometry'] = data['geometry'].affine_transform(transform)
        return data

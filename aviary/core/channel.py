from typing import (
    Any,
    Protocol,
)

import geopandas as gpd
import numpy.typing as npt

from aviary.core.enums import ChannelName
from aviary.core.type_aliases import BufferSize


class Channel(Protocol):
    """Protocol for channels

    Currently implemented channels:
        - `ArrayChannel`: Contains an array
        - `GdfChannel`: Contains a geodataframe
    """

    @property
    def data(self) -> Any:  # noqa: ANN401
        """
        Returns:
            Data
        """
        ...

    @property
    def name(self) -> ChannelName | str:
        """
        Returns:
            Name
        """
        ...

    @property
    def buffer_size(self) -> BufferSize:
        """
        Returns:
            Buffer size in meters
        """
        ...

    @property
    def data_type(self) -> type:
        """
        Returns:
            Data type
        """
        ...


class ArrayChannel:
    """Channel that contains an array

    Implements the `Channel` protocol.
    """

    def __init__(
        self,
        data: npt.NDArray,
        name: ChannelName | str,
        buffer_size: BufferSize,
    ) -> None:
        """
        Parameters:
            data: Data
            name: Name
            buffer_size: Buffer size in meters
        """
        self._data = data
        self._name = name
        self._buffer_size = buffer_size

        self._validate()

    def _validate(self) -> None:
        """Validates the array channel."""

    @property
    def data(self) -> npt.NDArray:
        """
        Returns:
            Data
        """
        return self._data

    @property
    def name(self) -> ChannelName | str:
        """
        Returns:
            Name
        """
        return self._name

    @property
    def buffer_size(self) -> BufferSize:
        """
        Returns:
            Buffer size in meters
        """
        return self._buffer_size

    @property
    def data_type(self) -> type:
        """
        Returns:
            Data type
        """
        return type(self._data)


class GdfChannel:
    """Channel that contains a geodataframe

    Implements the `Channel` protocol.
    """

    def __init__(
        self,
        data: gpd.GeoDataFrame,
        name: ChannelName | str,
        buffer_size: BufferSize,
    ) -> None:
        """
        Parameters:
            data: Data
            name: Name
            buffer_size: Buffer size in meters
        """
        self._data = data
        self._name = name
        self._buffer_size = buffer_size

        self._validate()

    def _validate(self) -> None:
        """Validates the geodataframe channel."""

    @property
    def data(self) -> gpd.GeoDataFrame:
        """
        Returns:
            Data
        """
        return self._data

    @property
    def name(self) -> ChannelName | str:
        """
        Returns:
            Name
        """
        return self._name

    @property
    def buffer_size(self) -> BufferSize:
        """
        Returns:
            Buffer size in meters
        """
        return self._buffer_size

    @property
    def data_type(self) -> type:
        """
        Returns:
            Data type
        """
        return type(self._data)

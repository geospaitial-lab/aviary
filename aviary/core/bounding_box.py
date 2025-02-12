from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
)
from math import (
    ceil,
    floor,
)

import geopandas as gpd
from shapely.geometry import box

from aviary.core.exceptions import AviaryUserError
from aviary.core.type_aliases import (
    BufferSize,
    Coordinate,
    EPSGCode,
)


class BoundingBox(Iterable[Coordinate]):
    """A bounding box specifies the spatial extent of an area of interest."""
    _COORDINATES = (
        'x_min',
        'y_min',
        'x_max',
        'y_max',
    )

    def __init__(
        self,
        x_min: Coordinate,
        y_min: Coordinate,
        x_max: Coordinate,
        y_max: Coordinate,
    ) -> None:
        """
        Parameters:
            x_min: Minimum x coordinate in meters
            y_min: Minimum y coordinate in meters
            x_max: Maximum x coordinate in meters
            y_max: Maximum y coordinate in meters
        """
        self._x_min = x_min
        self._y_min = y_min
        self._x_max = x_max
        self._y_max = y_max

        self._validate()

    def _validate(self) -> None:
        """Validates the bounding box.

        Raises:
            AviaryUserError: Invalid `bounding_box` (`x_min` is greater than or equal to `x_max` or
                `y_min` is greater than or equal to `y_max`)
        """
        conditions = [
            self._x_min >= self._x_max,
            self._y_min >= self._y_max,
        ]

        if any(conditions):
            message = (
                'Invalid bounding_box! '
                'x_min must be less than x_max and y_min must be less than y_max.'
            )
            raise AviaryUserError(message)

    @property
    def x_min(self) -> Coordinate:
        """
        Returns:
            Minimum x coordinate in meters
        """
        return self._x_min

    @property
    def y_min(self) -> Coordinate:
        """
        Returns:
            Minimum y coordinate in meters
        """
        return self._y_min

    @property
    def x_max(self) -> Coordinate:
        """
        Returns:
            Maximum x coordinate in meters
        """
        return self._x_max

    @property
    def y_max(self) -> Coordinate:
        """
        Returns:
            Maximum y coordinate in meters
        """
        return self._y_max

    @property
    def area(self) -> int:
        """
        Returns:
            Area in square meters
        """
        return (self._x_max - self._x_min) * (self._y_max - self._y_min)

    @classmethod
    def from_gdf(
        cls,
        gdf: gpd.GeoDataFrame,
    ) -> BoundingBox:
        """Creates a bounding box from a geodataframe.

        Parameters:
            gdf: Geodataframe

        Returns:
            Bounding box
        """
        x_min, y_min, x_max, y_max = gdf.total_bounds
        x_min = floor(x_min)
        y_min = floor(y_min)
        x_max = ceil(x_max)
        y_max = ceil(y_max)
        return cls(
            x_min=x_min,
            y_min=y_min,
            x_max=x_max,
            y_max=y_max,
        )

    def __repr__(self) -> str:
        """Returns the string representation.

        Returns:
            String representation
        """
        return (
            'BoundingBox(\n'
            f'    x_min={self._x_min},\n'
            f'    y_min={self._y_min},\n'
            f'    x_max={self._x_max},\n'
            f'    y_max={self._y_max},\n'
            ')'
        )

    def __eq__(
        self,
        other: BoundingBox,
    ) -> bool:
        """Compares the bounding boxes.

        Parameters:
            other: Other bounding box

        Returns:
            True if the bounding boxes are equal, False otherwise
        """
        if not isinstance(other, BoundingBox):
            return False

        conditions = [
            self._x_min == other.x_min,
            self._y_min == other.y_min,
            self._x_max == other.x_max,
            self._y_max == other.y_max,
        ]
        return all(conditions)

    def __len__(self) -> int:
        """Computes the number of coordinates.

        Returns:
            Number of coordinates
        """
        return len(self._COORDINATES)

    def __getitem__(
        self,
        index: int,
    ) -> Coordinate:
        """Returns the coordinate.

        Parameters:
            index: Index of the coordinate

        Returns:
            Coordinate in meters
        """
        return getattr(self, self._COORDINATES[index])

    def __iter__(self) -> Iterator[Coordinate]:
        """Iterates over the coordinates.

        Yields:
            Coordinate in meters
        """
        for coordinate in self._COORDINATES:
            yield getattr(self, coordinate)

    def buffer(
        self,
        buffer_size: BufferSize,
        inplace: bool = False,
    ) -> BoundingBox:
        """Buffers the bounding box.

        Notes:
            - A positive buffer size expands the bounding box
            - A negative buffer size shrinks the bounding box

        Examples:
            Assume the area of interest is specified by `x_min`=363084, `y_min`=5715326, `x_max`=363340, and
            `y_max`=5715582.

            You can expand the area of interest by buffering the bounding box.

            >>> bounding_box = BoundingBox(
            ...     x_min=363084,
            ...     y_min=5715326,
            ...     x_max=363340,
            ...     y_max=5715582,
            ... )
            >>> bounding_box.buffer(buffer_size=64)
            BoundingBox(
                x_min=363020,
                y_min=5715262,
                x_max=363404,
                y_max=5715646,
            )

        Parameters:
            buffer_size: Buffer size in meters
            inplace: If True, the bounding box is buffered inplace

        Returns:
            Bounding box

        Raises:
            AviaryUserError: Invalid `buffer_size` (the absolute value of a negative `buffer_size` is greater than or
                equal to half the width or height of the bounding box)
        """
        conditions = [
            buffer_size < 0,
            abs(buffer_size) >= (self._x_max - self._x_min) / 2 or
            abs(buffer_size) >= (self._y_max - self._y_min) / 2,
        ]

        if all(conditions):
            message = (
                'Invalid buffer_size! '
                'The absolute value of a negative buffer_size must be less than half the width and height '
                'of the bounding box.'
            )
            raise AviaryUserError(message)

        x_min = self._x_min - buffer_size
        y_min = self._y_min - buffer_size
        x_max = self._x_max + buffer_size
        y_max = self._y_max + buffer_size

        if inplace:
            self._x_min, self._y_min, self._x_max, self._y_max = x_min, y_min, x_max, y_max
            self._validate()
            return self

        return BoundingBox(
            x_min=x_min,
            y_min=y_min,
            x_max=x_max,
            y_max=y_max,
        )

    def quantize(
        self,
        value: int,
        inplace: bool = False,
    ) -> BoundingBox:
        """Quantizes the bounding box.

        Examples:
            Assume the area of interest is specified by `x_min`=363084, `y_min`=5715326, `x_max`=363340, and
            `y_max`=5715582.

            You can align the area of interest to a grid by quantizing the bounding box.

            >>> bounding_box = BoundingBox(
            ...     x_min=363084,
            ...     y_min=5715326,
            ...     x_max=363340,
            ...     y_max=5715582,
            ... )
            >>> bounding_box.quantize(value=128)
            BoundingBox(
                x_min=363008,
                y_min=5715200,
                x_max=363392,
                y_max=5715584,
            )

        Parameters:
            value: Value to quantize the coordinates to in meters
            inplace: If True, the bounding box is quantized inplace

        Returns:
            Bounding box

        Raises:
            AviaryUserError: Invalid `value` (the value is negative or zero)
        """
        if value <= 0:
            message = (
                'Invalid value! '
                'The value must be positive.'
            )
            raise AviaryUserError(message)

        x_min = self._x_min - self._x_min % value
        y_min = self._y_min - self._y_min % value
        x_max = self._x_max + (value - self._x_max % value) % value
        y_max = self._y_max + (value - self._y_max % value) % value

        if inplace:
            self._x_min, self._y_min, self._x_max, self._y_max = x_min, y_min, x_max, y_max
            self._validate()
            return self

        return BoundingBox(
            x_min=x_min,
            y_min=y_min,
            x_max=x_max,
            y_max=y_max,
        )

    def to_gdf(
        self,
        epsg_code: EPSGCode,
    ) -> gpd.GeoDataFrame:
        """Converts the bounding box to a geodataframe.

        Parameters:
            epsg_code: EPSG code

        Returns:
            Geodataframe
        """
        return gpd.GeoDataFrame(
            geometry=[box(self._x_min, self._y_min, self._x_max, self._y_max)],
            crs=f'EPSG:{epsg_code}',
        )

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
)
from dataclasses import (
    dataclass,
    fields,
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


@dataclass
class BoundingBox(Iterable[Coordinate]):
    """A bounding box specifies the spatial extent of an area of interest.

    Attributes:
        x_min: minimum x coordinate
        y_min: minimum y coordinate
        x_max: maximum x coordinate
        y_max: maximum y coordinate
    """
    x_min: Coordinate
    y_min: Coordinate
    x_max: Coordinate
    y_max: Coordinate

    def __init__(
        self,
        x_min: Coordinate,
        y_min: Coordinate,
        x_max: Coordinate,
        y_max: Coordinate,
    ) -> None:
        """
        Parameters:
            x_min: minimum x coordinate
            y_min: minimum y coordinate
            x_max: maximum x coordinate
            y_max: maximum y coordinate

        Raises:
            AviaryUserError: Invalid bounding box (`x_min` >= `x_max` or `y_min` >= `y_max`)
        """
        self._x_min = x_min
        self._y_min = y_min
        self._x_max = x_max
        self._y_max = y_max

        if self._x_min >= self._x_max:
            message = (
                'Invalid bounding box! '
                'x_min must be less than x_max.'
            )
            raise AviaryUserError(message)

        if self._y_min >= self._y_max:
            message = (
                'Invalid bounding box! '
                'y_min must be less than y_max.'
            )
            raise AviaryUserError(message)

    @property
    def x_min(self) -> Coordinate:
        """
        Returns:
            minimum x coordinate
        """
        return self._x_min

    @x_min.setter
    def x_min(
        self,
        value: Coordinate,
    ) -> None:
        """
        Parameters:
            value: minimum x coordinate

        Raises:
            AviaryUserError: Invalid bounding box (`x_min` >= `x_max`)
        """
        if value >= self._x_max:
            message = (
                'Invalid bounding box! '
                'x_min must be less than x_max.'
            )
            raise AviaryUserError(message)

        self._x_min = value

    @property
    def y_min(self) -> Coordinate:
        """
        Returns:
            minimum y coordinate
        """
        return self._y_min

    @y_min.setter
    def y_min(
        self,
        value: Coordinate,
    ) -> None:
        """
        Parameters:
            value: minimum y coordinate

        Raises:
            AviaryUserError: Invalid bounding box (`y_min` >= `y_max`)
        """
        if value >= self._y_max:
            message = (
                'Invalid bounding box! '
                'y_min must be less than y_max.'
            )
            raise AviaryUserError(message)

        self._y_min = value

    @property
    def x_max(self) -> Coordinate:
        """
        Returns:
            maximum x coordinate
        """
        return self._x_max

    @x_max.setter
    def x_max(
        self,
        value: Coordinate,
    ) -> None:
        """
        Parameters:
            value: maximum x coordinate

        Raises:
            AviaryUserError: Invalid bounding box (`x_min` >= `x_max`)
        """
        if value <= self._x_min:
            message = (
                'Invalid bounding box! '
                'x_min must be less than x_max.'
            )
            raise AviaryUserError(message)

        self._x_max = value

    @property
    def y_max(self) -> Coordinate:
        """
        Returns:
            maximum y coordinate
        """
        return self._y_max

    @y_max.setter
    def y_max(
        self,
        value: Coordinate,
    ) -> None:
        """
        Parameters:
            value: maximum y coordinate

        Raises:
            AviaryUserError: Invalid bounding box (`y_min` >= `y_max`)
        """
        if value <= self._y_min:
            message = (
                'Invalid bounding box! '
                'y_min must be less than y_max.'
            )
            raise AviaryUserError(message)

        self._y_max = value

    @property
    def area(self) -> int:
        """
        Returns:
            area in square meters
        """
        return (self._x_max - self._x_min) * (self._y_max - self._y_min)

    @classmethod
    def from_gdf(
        cls,
        gdf: gpd.GeoDataFrame,
    ) -> BoundingBox:
        """Creates a bounding box from a geodataframe.

        Parameters:
            gdf: geodataframe

        Returns:
            bounding box
        """
        x_min, y_min, x_max, y_max = gdf.total_bounds
        return cls(
            x_min=floor(x_min),
            y_min=floor(y_min),
            x_max=ceil(x_max),
            y_max=ceil(y_max),
        )

    def __repr__(self) -> str:
        """Returns the string representation.

        Returns:
            string representation
        """
        return (
            'BoundingBox(\n'
            f'    x_min={self._x_min},\n'
            f'    y_min={self._y_min},\n'
            f'    x_max={self._x_max},\n'
            f'    y_max={self._y_max},\n'
            ')'
        )

    def __len__(self) -> int:
        """Computes the number of coordinates.

        Returns:
            number of coordinates
        """
        return len(fields(self))

    def __getitem__(
        self,
        index: int,
    ) -> Coordinate:
        """Returns the coordinate.

        Parameters:
            index: index of the coordinate

        Returns:
            coordinate
        """
        field = fields(self)[index]
        return getattr(self, field.name)

    def __iter__(self) -> Iterator[Coordinate]:
        """Iterates over the coordinates.

        Yields:
            coordinate
        """
        for field in fields(self):
            yield getattr(self, field.name)

    def buffer(
        self,
        buffer_size: BufferSize,
        inplace: bool = False,
    ) -> BoundingBox:
        """Buffers the bounding box.

        Examples:
            Assume the area of interest is specified by `x_min`=363084, `y_min`=5715326, `x_max`=363340 and
            `y_max`=5715582.

            You can expand the area of interest by buffering the bounding box.

            >>> bounding_box = BoundingBox(
            ...     x_min=363084,
            ...     y_min=5715326,
            ...     x_max=363340,
            ...     y_max=5715582,
            ... )
            >>> bounding_box.buffer(buffer_size=64)
            BoundingBox(x_min=363020, y_min=5715262, x_max=363404, y_max=5715646)

        Parameters:
            buffer_size: buffer size in meters
            inplace: if True, the bounding box is buffered inplace

        Returns:
            buffered bounding box

        Raises:
            AviaryUserError: Invalid buffer size (abs(`buffer_size`) >= half the width or height of the bounding box)
        """
        conditions = [
            buffer_size < 0,
            abs(buffer_size) >= (self._x_max - self._x_min) / 2 or
            abs(buffer_size) >= (self._y_max - self._y_min) / 2,
        ]

        if all(conditions):
            message = (
                'Invalid buffer size! '
                'buffer_size must be less than half the width or height of the bounding box.'
            )
            raise AviaryUserError(message)

        x_min = self._x_min - buffer_size
        y_min = self._y_min - buffer_size
        x_max = self._x_max + buffer_size
        y_max = self._y_max + buffer_size

        if inplace:
            self.x_min, self.y_min, self.x_max, self.y_max = x_min, y_min, x_max, y_max
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
        """Quantizes the coordinates to the specified value.

        Examples:
            Assume the area of interest is specified by `x_min`=363084, `y_min`=5715326, `x_max`=363340 and
            `y_max`=5715582.

            You can align the area of interest to a grid by quantizing the bounding box.

            >>> bounding_box = BoundingBox(
            ...     x_min=363084,
            ...     y_min=5715326,
            ...     x_max=363340,
            ...     y_max=5715582,
            ... )
            >>> bounding_box.quantize(value=128)
            BoundingBox(x_min=363008, y_min=5715200, x_max=363392, y_max=5715584)

        Parameters:
            value: value to quantize the coordinates to in meters
            inplace: if True, the bounding box is quantized inplace

        Returns:
            quantized bounding box

        Raises:
            AviaryUserError: Invalid value (`value` <= 0)
        """
        if value <= 0:
            message = (
                'Invalid value! '
                'value must be positive.'
            )
            raise AviaryUserError(message)

        x_min = self._x_min - self._x_min % value
        y_min = self._y_min - self._y_min % value
        x_max = self._x_max + (value - self._x_max % value) % value
        y_max = self._y_max + (value - self._y_max % value) % value

        if inplace:
            self.x_min, self.y_min, self.x_max, self.y_max = x_min, y_min, x_max, y_max
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
            bounding box
        """
        return gpd.GeoDataFrame(
            geometry=[box(self._x_min, self._y_min, self._x_max, self._y_max)],
            crs=f'EPSG:{epsg_code}',
        )

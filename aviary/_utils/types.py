from __future__ import annotations

import json
from collections.abc import (
    Iterable,
    Iterator,
)
from dataclasses import dataclass, fields
from enum import Enum
from math import ceil, floor
from pathlib import Path  # noqa: TC003
from typing import (
    TYPE_CHECKING,
    TypeAlias,
    cast,
    overload,
)

import geopandas as gpd
import numpy as np
import numpy.typing as npt
import pydantic
import rasterio as rio
from shapely.geometry import box

# noinspection PyProtectedMember
from aviary._functional.geodata.coordinates_filter import (
    duplicates_filter,
    geospatial_filter,
    set_filter,
)

# noinspection PyProtectedMember
from aviary._functional.geodata.grid_generator import compute_coordinates
from aviary._utils.exceptions import AviaryUserError

if TYPE_CHECKING:
    from aviary.geodata.coordinates_filter import CoordinatesFilter

BufferSize: TypeAlias = int
Coordinate: TypeAlias = int
Coordinates: TypeAlias = tuple[Coordinate, Coordinate]
CoordinatesSet: TypeAlias = npt.NDArray[np.int32]
EPSGCode: TypeAlias = int
GroundSamplingDistance: TypeAlias = float
TileSize: TypeAlias = int


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


class Device(Enum):
    """
    Attributes:
        CPU: CPU device
        CUDA: CUDA device
    """
    CPU = 'cpu'
    CUDA = 'cuda'


class GeospatialFilterMode(Enum):
    """
    Attributes:
        DIFFERENCE: difference mode
        INTERSECTION: intersection mode
    """
    DIFFERENCE = 'difference'
    INTERSECTION = 'intersection'


class InterpolationMode(Enum):
    """
    Attributes:
        BILINEAR: bilinear mode
        NEAREST: nearest mode
    """
    BILINEAR = 'bilinear'
    NEAREST = 'nearest'

    def to_rio(self) -> rio.enums.Resampling:
        """Converts the interpolation mode to the rasterio resampling mode.

        Returns:
            rasterio resampling mode
        """
        mapping = {
            InterpolationMode.BILINEAR: rio.enums.Resampling.bilinear,
            InterpolationMode.NEAREST: rio.enums.Resampling.nearest,
        }
        return mapping[self]


@dataclass
class ProcessArea(Iterable[Coordinates]):
    """A process area specifies the area of interest by a set of coordinates of the bottom left corner of each tile
    and the tile size.

    Notes:
        - The `+` operator can be used to add two process areas
        - The `-` operator can be used to subtract two process areas
        - The `&` operator can be used to intersect two process areas

    Attributes:
        coordinates: coordinates (x_min, y_min) of each tile
        tile_size: tile size in meters
    """
    coordinates: CoordinatesSet
    tile_size: TileSize

    def __init__(
        self,
        tile_size: TileSize,
        coordinates: CoordinatesSet | None = None,
    ) -> None:
        """
        Parameters:
            tile_size: tile size in meters
            coordinates: coordinates (x_min, y_min) of each tile
        """
        self.tile_size = tile_size

        if coordinates is None:
            coordinates = np.empty(
                shape=(0, 2),
                dtype=np.int32,
            )

        self.coordinates = coordinates

    @property
    def tile_size(self) -> TileSize:
        """
        Returns:
            tile size in meters
        """
        return self._tile_size

    @tile_size.setter
    def tile_size(
        self,
        value: TileSize,
    ) -> None:
        """
        Parameters:
            value: tile size in meters

        Raises:
            AviaryUserError: Invalid tile size (`tile_size` <= 0)
        """
        if value <= 0:
            message = (
                'Invalid tile size! '
                'tile_size must be positive.'
            )
            raise AviaryUserError(message)

        self._tile_size = value

    @property
    def coordinates(self) -> CoordinatesSet:
        """
        Returns:
            coordinates (x_min, y_min) of each tile
        """
        return self._coordinates

    @coordinates.setter
    def coordinates(
        self,
        value: CoordinatesSet,
    ) -> None:
        """
        Parameters:
            value: coordinates (x_min, y_min) of each tile

        Raises:
            AviaryUserError: Invalid coordinates (`coordinates` is not an array of shape (n, 2) and data type int32)
        """
        conditions = [
            value.ndim != 2,  # noqa: PLR2004
            value.shape[1] != 2,  # noqa: PLR2004
            value.dtype != np.int32,
        ]

        if any(conditions):
            message = (
                'Invalid coordinates! '
                'coordinates must be an array of shape (n, 2) and data type int32.'
            )
            raise AviaryUserError(message)

        self._coordinates = value

    @property
    def area(self) -> int:
        """
        Returns:
            area in square meters
        """
        return len(self) * self._tile_size ** 2

    @classmethod
    def from_bounding_box(
        cls,
        bounding_box: BoundingBox,
        tile_size: TileSize,
        quantize: bool = True,
    ) -> ProcessArea:
        """Creates a process area from a bounding box.

        Parameters:
            bounding_box: bounding box
            tile_size: tile size in meters
            quantize: if True, the bounding box is quantized to `tile_size`

        Returns:
            process area
        """
        coordinates = compute_coordinates(
            bounding_box=bounding_box,
            tile_size=tile_size,
            quantize=quantize,
        )
        return cls(
            coordinates=coordinates,
            tile_size=tile_size,
        )

    @classmethod
    def from_gdf(
        cls,
        gdf: gpd.GeoDataFrame,
        tile_size: TileSize,
        quantize: bool = True,
    ) -> ProcessArea:
        """Creates a process area from a geodataframe.

        Parameters:
            gdf: geodataframe
            tile_size: tile size in meters
            quantize: if True, the bounding box is quantized to `tile_size`

        Returns:
            process area
        """
        bounding_box = BoundingBox.from_gdf(gdf)
        coordinates = compute_coordinates(
            bounding_box=bounding_box,
            tile_size=tile_size,
            quantize=quantize,
        )
        coordinates = geospatial_filter(
            coordinates=coordinates,
            tile_size=tile_size,
            gdf=gdf,
            mode=GeospatialFilterMode.INTERSECTION,
        )
        return cls(
            coordinates=coordinates,
            tile_size=tile_size,
        )

    @classmethod
    def from_json(
        cls,
        json_string: str,
    ) -> ProcessArea:
        """Creates a process area from a JSON string.

        Notes:
            - The JSON string contains a list of coordinates (x_min, y_min) of each tile and the tile size

        Examples:
            Assume the JSON string is '{"coordinates":
            [[363084, 5715326], [363212, 5715326], [363084, 5715454], [363212, 5715454]],
            "tile_size": 1}'.

            You can create a process area from the JSON string.

            >>> process_area = ProcessArea.from_json(
            ...     json_string=(
            ...         '{"coordinates": '
            ...         '[[363084, 5715326], '
            ...         '[363212, 5715326], '
            ...         '[363084, 5715454], '
            ...         '[363212, 5715454]], '
            ...         '"tile_size": 128}'
            ...     ),
            ... )

        Parameters:
            json_string: JSON string

        Returns:
            process area
        """
        dict_ = json.loads(json_string)
        coordinates, tile_size = dict_['coordinates'], dict_['tile_size']
        coordinates = np.array(coordinates, dtype=np.int32) if coordinates else None
        return cls(
            coordinates=coordinates,
            tile_size=tile_size,
        )

    @classmethod
    def from_config(
        cls,
        config: ProcessAreaConfig,
    ) -> ProcessArea:
        """Creates a process area from the configuration.

        Parameters:
            config: configuration

        Returns:
            process area

        Raises:
            AviaryUserError: Invalid configuration
        """
        if config.json_string is not None:
            process_area = cls.from_json(
                json_string=cast(str, config.json_string),
            )

            if config.processed_coordinates_json_string is not None:
                processed_process_area = cls.from_json(
                    json_string=cast(str, config.processed_coordinates_json_string),
                )
                process_area = process_area - processed_process_area

            return process_area

        if config.gdf is not None:
            process_area = cls.from_gdf(
                gdf=cast(gpd.GeoDataFrame, config.gdf),
                tile_size=config.tile_size,
                quantize=config.quantize,
            )

            if config.processed_coordinates_json_string is not None:
                processed_process_area = cls.from_json(
                    json_string=cast(str, config.processed_coordinates_json_string),
                )
                process_area = process_area - processed_process_area

            return process_area

        if config.bounding_box is not None:
            process_area = cls.from_bounding_box(
                bounding_box=cast(BoundingBox, config.bounding_box),
                tile_size=config.tile_size,
                quantize=config.quantize,
            )

            if config.processed_coordinates_json_string is not None:
                processed_process_area = cls.from_json(
                    json_string=cast(str, config.processed_coordinates_json_string),
                )
                process_area = process_area - processed_process_area

            return process_area

        message = (
            'Invalid configuration! '
            'config must have one of the following field sets: '
            'json_string | gdf, tile_size | bounding_box, tile_size'
        )
        raise AviaryUserError(message)

    def __repr__(self) -> str:
        """Returns the string representation.

        Returns:
            string representation
        """
        max_coordinates = 4
        coordinates = self._coordinates.tolist()

        if len(coordinates) > max_coordinates:
            coordinates = coordinates[:max_coordinates // 2] + [Ellipsis] + coordinates[-max_coordinates // 2:]

        coordinates = str(coordinates).replace('Ellipsis', '...')
        return (
            'ProcessArea(\n'
            f'    coordinates={coordinates},\n'
            f'    tile_size={self._tile_size},\n'
            ')'
        )

    def __eq__(
        self,
        other: ProcessArea,
    ) -> bool:
        """Compares the process areas.

        Parameters:
            other: other process area

        Returns:
            True if the process areas are equal, False otherwise
        """
        conditions = [
            np.array_equal(self._coordinates, other.coordinates),
            self._tile_size == other.tile_size,
        ]
        return all(conditions)

    def __len__(self) -> int:
        """Computes the number of coordinates.

        Returns:
            number of coordinates
        """
        return len(self._coordinates)

    @overload
    def __getitem__(
        self,
        index: int,
    ) -> Coordinates:
        ...

    @overload
    def __getitem__(
        self,
        index: slice,
    ) -> ProcessArea:
        ...

    def __getitem__(
        self,
        index: int | slice,
    ) -> Coordinates | ProcessArea:
        """Returns the coordinates or the sliced process area.

        Parameters:
            index: index or slice of the coordinates

        Returns:
            coordinates or sliced process area
        """
        if isinstance(index, slice):
            coordinates = self._coordinates[index]
            return ProcessArea(
                coordinates=coordinates,
                tile_size=self._tile_size,
            )

        x_min, y_min = self._coordinates[index]
        return int(x_min), int(y_min)

    def __iter__(self) -> Iterator[Coordinates]:
        """Iterates over the coordinates.

        Yields:
            coordinates
        """
        for x_min, y_min in self._coordinates:
            yield int(x_min), int(y_min)

    def __add__(
        self,
        other: ProcessArea,
    ) -> ProcessArea:
        """Adds the process areas.

        Notes:
            - This method is equivalent to applying the set filter with the `UNION` set filter mode
              to the coordinates

        Parameters:
            other: other process area

        Returns:
            union of the process areas

        Raises:
            AviaryUserError: Invalid tile size (`tile_size` != `other.tile_size`)
        """
        if self._tile_size != other.tile_size:
            message = (
                'Invalid tile size! '
                'The tile sizes of the process areas must be equal.'
            )
            raise AviaryUserError(message)

        coordinates = set_filter(
            coordinates=self._coordinates,
            other=other.coordinates,
            mode=SetFilterMode.UNION,
        )
        return ProcessArea(
            coordinates=coordinates,
            tile_size=self._tile_size,
        )

    def __sub__(
        self,
        other: ProcessArea,
    ) -> ProcessArea:
        """Subtracts the process areas.

        Notes:
            - This method is equivalent to applying the set filter with the `DIFFERENCE` set filter mode
              to the coordinates

        Parameters:
            other: other process area

        Returns:
            difference of the process areas

        Raises:
            AviaryUserError: Invalid tile size (`tile_size` != `other.tile_size`)
        """
        if self._tile_size != other.tile_size:
            message = (
                'Invalid tile size! '
                'The tile sizes of the process areas must be equal.'
            )
            raise AviaryUserError(message)

        coordinates = set_filter(
            coordinates=self._coordinates,
            other=other.coordinates,
            mode=SetFilterMode.DIFFERENCE,
        )
        return ProcessArea(
            coordinates=coordinates,
            tile_size=self._tile_size,
        )

    def __and__(
        self,
        other: ProcessArea,
    ) -> ProcessArea:
        """Intersects the process areas.

        Notes:
            - This method is equivalent to applying the set filter with the `INTERSECTION` set filter mode
              to the coordinates

        Parameters:
            other: other process area

        Returns:
            intersection of the process areas

        Raises:
            AviaryUserError: Invalid tile size (`tile_size` != `other.tile_size`)
        """
        if self._tile_size != other.tile_size:
            message = (
                'Invalid tile size! '
                'The tile sizes of the process areas must be equal.'
            )
            raise AviaryUserError(message)

        coordinates = set_filter(
            coordinates=self._coordinates,
            other=other.coordinates,
            mode=SetFilterMode.INTERSECTION,
        )
        return ProcessArea(
            coordinates=coordinates,
            tile_size=self._tile_size,
        )

    def append(
        self,
        other: Coordinates,
        inplace: bool = False,
    ) -> ProcessArea:
        """Appends the coordinates to the process area.

        Parameters:
            other: other coordinates
            inplace: if True, the coordinates are appended inplace

        Returns:
            process area
        """
        other = np.array([other], dtype=np.int32)
        coordinates = np.concatenate([self._coordinates, other], axis=0)
        coordinates = duplicates_filter(coordinates)

        if inplace:
            self._coordinates = coordinates
            return self

        return ProcessArea(
            coordinates=coordinates,
            tile_size=self._tile_size,
        )

    def chunk(
        self,
        num_chunks: int,
    ) -> list[ProcessArea]:
        """Chunks the process area.

        Parameters:
            num_chunks: number of chunks

        Returns:
            list of process areas
        """
        return [
            ProcessArea(
                coordinates=coordinates,
                tile_size=self._tile_size,
            )
            for coordinates
            in np.array_split(self._coordinates, indices_or_sections=num_chunks)
        ]

    def filter(
        self,
        coordinates_filter: CoordinatesFilter,
        inplace: bool = False,
    ) -> ProcessArea:
        """Filters the process area.

        Parameters:
            coordinates_filter: coordinates filter
            inplace: if True, the coordinates are filtered inplace

        Returns:
            filtered process area
        """
        coordinates = coordinates_filter(self._coordinates)

        if inplace:
            self._coordinates = coordinates
            return self

        return ProcessArea(
            coordinates=coordinates,
            tile_size=self._tile_size,
        )

    def to_gdf(
        self,
        epsg_code: EPSGCode,
    ) -> gpd.GeoDataFrame:
        """Converts the process area to a geodataframe.

        Parameters:
            epsg_code: EPSG code

        Returns:
            geodataframe
        """
        geometry = [
            box(x_min, y_min, x_min + self._tile_size, y_min + self._tile_size)
            for x_min, y_min in self._coordinates
        ]
        return gpd.GeoDataFrame(
            geometry=geometry,
            crs=f'EPSG:{epsg_code}',
        )

    def to_json(self) -> str:
        """Converts the process area to a JSON string.

        Notes:
            - The JSON string contains a list of coordinates (x_min, y_min) of each tile and the tile size

        Returns:
            JSON string
        """
        dict_ = {
            'coordinates': self._coordinates.tolist(),
            'tile_size': self._tile_size,
        }
        return json.dumps(dict_)


class ProcessAreaConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `ProcessArea`

    The configuration must have one of the following field sets:
        - `json_string`
        - `gdf` and `tile_size`
        - `bounding_box` and `tile_size`

    Attributes:
        bounding_box: bounding box (x_min, y_min, x_max, y_max)
        gdf: path to the geodataframe
        json_string: path to the JSON file containing the coordinates (x_min, y_min) of each tile
        processed_coordinates_json_string: path to the JSON file containing the coordinates (x_min, y_min)
            of the processed tiles
        tile_size: tile size in meters
        quantize: if True, the bounding box is quantized to `tile_size`
    """
    bounding_box: list[Coordinate] | None = None
    gdf: Path | None = None
    json_string: Path | None = None
    processed_coordinates_json_string: Path | None = None
    tile_size: TileSize | None = None
    quantize: bool = True

    # noinspection PyNestedDecorators
    @pydantic.field_validator('bounding_box')
    @classmethod
    def parse_bounding_box(
        cls,
        bounding_box: list[Coordinate],
    ) -> BoundingBox:
        """Parses the bounding box."""
        if len(bounding_box) != 4:  # noqa: PLR2004
            message = (
                'Invalid bounding box! '
                'bounding_box must be a list of length 4.'
            )
            raise ValueError(message)

        return BoundingBox(
            x_min=bounding_box[0],
            y_min=bounding_box[1],
            x_max=bounding_box[2],
            y_max=bounding_box[3],
        )

    # noinspection PyNestedDecorators
    @pydantic.field_validator('gdf')
    @classmethod
    def parse_gdf(
        cls,
        gdf: Path,
    ) -> gpd.GeoDataFrame:
        """Parses the geodataframe."""
        return gpd.read_file(gdf)

    # noinspection PyNestedDecorators
    @pydantic.field_validator('json_string')
    @classmethod
    def parse_json_string(
        cls,
        json_string: Path,
    ) -> str:
        """Parses the JSON string containing the coordinates (x_min, y_min) of each tile."""
        with json_string.open() as file:
            return json.load(file)

    # noinspection PyNestedDecorators
    @pydantic.field_validator('processed_coordinates_json_string')
    @classmethod
    def parse_processed_coordinates_json_string(
        cls,
        processed_coordinates_json_string: Path,
    ) -> str:
        """Parses the JSON string containing the coordinates (x_min, y_min) of the processed tiles."""
        with processed_coordinates_json_string.open() as file:
            return json.load(file)

    @pydantic.model_validator(mode='after')
    def validate(self) -> ProcessAreaConfig:
        """Validates the configuration."""
        conditions = [
            self.json_string is not None,
            self.gdf is not None and self.tile_size is not None,
            self.bounding_box is not None and self.tile_size is not None,
        ]

        if any(conditions) is False:
            message = (
                'Invalid configuration! '
                'config must have one of the following field sets: '
                'json_string | gdf, tile_size | bounding_box, tile_size'
            )
            raise ValueError(message)

        return self


class SetFilterMode(Enum):
    """
    Attributes:
        DIFFERENCE: difference mode
        INTERSECTION: intersection mode
        UNION: union mode
    """
    DIFFERENCE = 'difference'
    INTERSECTION = 'intersection'
    UNION = 'union'


class WMSVersion(Enum):
    """
    Attributes:
        V1_1_1: version 1.1.1
        V1_3_0: version 1.3.0
    """
    V1_1_1 = '1.1.1'
    V1_3_0 = '1.3.0'

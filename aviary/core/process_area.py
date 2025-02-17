from __future__ import annotations

import json
import warnings
from collections.abc import (
    Iterable,
    Iterator,
)
from pathlib import Path  # noqa: TC003
from typing import (
    TYPE_CHECKING,
    cast,
    overload,
)

import geopandas as gpd
import numpy as np
import pydantic
from shapely.geometry import box

# noinspection PyProtectedMember
from aviary._functional.geodata.coordinates_filter import (
    duplicates_filter,
    geospatial_filter,
    set_filter,
)

# noinspection PyProtectedMember
from aviary._functional.geodata.grid_generator import compute_coordinates
from aviary.core.bounding_box import BoundingBox
from aviary.core.enums import (
    GeospatialFilterMode,
    SetFilterMode,
)
from aviary.core.exceptions import (
    AviaryUserError,
    AviaryUserWarning,
)
from aviary.core.type_aliases import (
    Coordinate,
    Coordinates,
    CoordinatesSet,
    EPSGCode,
    TileSize,
)

if TYPE_CHECKING:
    from aviary.geodata.coordinates_filter import CoordinatesFilter


class ProcessArea(Iterable[Coordinates]):
    """A process area specifies the spatial extent of an area of interest by a set of coordinates
    of the bottom left corner of each tile and the tile size.

    Notes:
        - The coordinates are assumed to be in shape (n, 2) and data type int32, where n is the number of coordinates
        - The `+` operator can be used to add two process areas
        - The `-` operator can be used to subtract two process areas
        - The `&` operator can be used to intersect two process areas
    """

    def __init__(
        self,
        coordinates: CoordinatesSet | None,
        tile_size: TileSize,
    ) -> None:
        """
        Parameters:
            coordinates: Coordinates (x_min, y_min) of each tile in meters
            tile_size: Tile size in meters
        """
        self._coordinates = coordinates
        self._tile_size = tile_size

        self._validate()

    def _validate(self) -> None:
        """Validates the process area."""
        self._validate_coordinates()
        self._validate_tile_size()

    def _validate_coordinates(self) -> None:
        """Validates `coordinates`.

        Raises:
            AviaryUserError: Invalid `coordinates` (the coordinates are not in shape (n, 2) and data type int32)
        """
        if self._coordinates is None:
            self._coordinates = np.empty(
                shape=(0, 2),
                dtype=np.int32,
            )
            return

        if self._coordinates.ndim != 2:  # noqa: PLR2004
            message = (
                'Invalid coordinates! '
                'The coordinates must be in shape (n, 2) and data type int32.'
            )
            raise AviaryUserError(message)

        conditions = [
            self._coordinates.shape[1] != 2,  # noqa: PLR2004
            self._coordinates.dtype != np.int32,
        ]

        if any(conditions):
            message = (
                'Invalid coordinates! '
                'The coordinates must be in shape (n, 2) and data type int32.'
            )
            raise AviaryUserError(message)

        unique_coordinates = duplicates_filter(coordinates=self._coordinates)  # returns a copy

        if len(self._coordinates) != len(unique_coordinates):
            message = (
                'Invalid coordinates! '
                'The coordinates must contain unique coordinates. '
                'Duplicates are removed.'
            )
            warnings.warn(
                message=message,
                category=AviaryUserWarning,
                stacklevel=2,
            )

        self._coordinates = unique_coordinates

    def _validate_tile_size(self) -> None:
        """Validates `tile_size`.

        Raises:
            AviaryUserError: Invalid `tile_size` (the tile size is negative or zero)
        """
        if self._tile_size <= 0:
            message = (
                'Invalid tile_size! '
                'The tile size must be positive.'
            )
            raise AviaryUserError(message)

    @property
    def coordinates(self) -> CoordinatesSet:
        """
        Returns:
            Coordinates (x_min, y_min) of each tile in meters
        """
        return self._coordinates.copy()

    @property
    def tile_size(self) -> TileSize:
        """
        Returns:
            Tile size in meters
        """
        return self._tile_size

    @property
    def area(self) -> int:
        """
        Returns:
            Area in square meters
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
            bounding_box: Bounding box
            tile_size: Tile size in meters
            quantize: If True, the bounding box is quantized to `tile_size`

        Returns:
            Process area

        Raises:
            AviaryUserError: Invalid `tile_size` (the tile size is negative or zero)
        """
        if tile_size <= 0:
            message = (
                'Invalid tile_size! '
                'The tile size must be positive.'
            )
            raise AviaryUserError(message)

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
            gdf: Geodataframe
            tile_size: Tile size in meters
            quantize: If True, the bounding box is quantized to `tile_size`

        Returns:
            Process area

        Raises:
            AviaryUserError: Invalid `gdf` (the geodataframe contains no geometries)
            AviaryUserError: Invalid `tile_size` (the tile size is negative or zero)
        """
        if gdf.empty:
            message = (
                'Invalid gdf! '
                'The geodataframe must contain at least one geometry.'
            )
            raise AviaryUserError(message)

        if tile_size <= 0:
            message = (
                'Invalid tile_size! '
                'The tile size must be positive.'
            )
            raise AviaryUserError(message)

        bounding_box = BoundingBox.from_gdf(gdf=gdf)
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
            Process area

        Raises:
            AviaryUserError: Invalid `json_string` (the JSON string does not contain the keys coordinates and tile_size)
        """
        dict_ = json.loads(json_string)

        if 'coordinates' not in dict_ or 'tile_size' not in dict_:
            message = (
                'Invalid json_string! '
                'The JSON string must contain the keys coordinates and tile_size.'
            )
            raise AviaryUserError(message)

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
            config: Configuration

        Returns:
            Process area

        Raises:
            AviaryUserError: Invalid config
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
            'Invalid config! '
            'The configuration must have one of the following field sets: '
            'json_string | gdf, tile_size | bounding_box, tile_size'
        )
        raise AviaryUserError(message)

    def __repr__(self) -> str:
        """Returns the string representation.

        Returns:
            String representation
        """
        coordinates_repr = len(self)
        return (
            'ProcessArea(\n'
            f'    coordinates={coordinates_repr},\n'
            f'    tile_size={self._tile_size},\n'
            ')'
        )

    def __eq__(
        self,
        other: ProcessArea,
    ) -> bool:
        """Compares the process areas.

        Parameters:
            other: Other process area

        Returns:
            True if the process areas are equal, False otherwise
        """
        if not isinstance(other, ProcessArea):
            return False

        conditions = [
            np.array_equal(self._coordinates, other.coordinates),
            self._tile_size == other.tile_size,
        ]
        return all(conditions)

    def __len__(self) -> int:
        """Computes the number of coordinates.

        Returns:
            Number of coordinates
        """
        return len(self._coordinates)

    def __contains__(
        self,
        coordinates: Coordinates,
    ) -> bool:
        """Checks if the coordinates are in the process area.

        Parameters:
            coordinates: Coordinates (x_min, y_min) of the tile in meters

        Returns:
            True if the coordinates are in the process area, False otherwise
        """
        coordinates = np.array([coordinates], dtype=np.int32)
        coordinates = np.concatenate([self._coordinates, coordinates], axis=0)
        unique_coordinates = duplicates_filter(coordinates=coordinates)
        return len(coordinates) == len(unique_coordinates)


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
            index: Index or slice of the coordinates

        Returns:
            Coordinates in meters or sliced process area
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
            Coordinates in meters
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
            other: Other process area

        Returns:
            Process area

        Raises:
            AviaryUserError: Invalid `other` (the tile sizes of the process areas are not equal)
        """
        if self._tile_size != other.tile_size:
            message = (
                'Invalid other! '
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
            other: Other process area

        Returns:
            Process area

        Raises:
            AviaryUserError: Invalid `other` (the tile sizes of the process areas are not equal)
        """
        if self._tile_size != other.tile_size:
            message = (
                'Invalid other! '
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
            other: Other process area

        Returns:
            Process area

        Raises:
            AviaryUserError: Invalid `other` (the tile sizes of the process areas are not equal)
        """
        if self._tile_size != other.tile_size:
            message = (
                'Invalid other! '
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
        coordinates: Coordinates,
        inplace: bool = False,
    ) -> ProcessArea:
        """Appends the coordinates to the process area.

        Parameters:
            coordinates: Coordinates (x_min, y_min) of the tile in meters
            inplace: If True, the coordinates are appended inplace

        Returns:
            Process area
        """
        coordinates = np.array([coordinates], dtype=np.int32)
        coordinates = np.concatenate([self._coordinates, coordinates], axis=0)
        unique_coordinates = duplicates_filter(coordinates=coordinates)

        if len(coordinates) != len(unique_coordinates):
            message = (
                'Invalid coordinates! '
                'The coordinates are already in the process area.'
            )
            warnings.warn(
                message=message,
                category=AviaryUserWarning,
                stacklevel=2,
            )

        coordinates = unique_coordinates

        if inplace:
            self._coordinates = coordinates
            self._validate()
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
            num_chunks: Number of chunks

        Returns:
            Process areas
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
            coordinates_filter: Coordinates filter
            inplace: If True, the coordinates are filtered inplace

        Returns:
            Process area
        """
        coordinates = coordinates_filter(coordinates=self._coordinates)

        if inplace:
            self._coordinates = coordinates
            self._validate()
            return self

        return ProcessArea(
            coordinates=coordinates,
            tile_size=self._tile_size,
        )

    def remove(
        self,
        coordinates: Coordinates,
        inplace: bool = False,
    ) -> ProcessArea:
        """Removes the coordinates from the process area.

        Parameters:
            coordinates: Coordinates (x_min, y_min) of the tile in meters
            inplace: If True, the coordinates are removed inplace

        Returns:
            Process area
        """
        coordinates = np.array([coordinates], dtype=np.int32)
        coordinates = set_filter(
            coordinates=self._coordinates,
            other=coordinates,
            mode=SetFilterMode.DIFFERENCE,
        )

        if np.array_equal(self._coordinates, coordinates):
            message = (
                'Invalid coordinates! '
                'The coordinates are not in the process area.'
            )
            warnings.warn(
                message=message,
                category=AviaryUserWarning,
                stacklevel=2,
            )

        if inplace:
            self._coordinates = coordinates
            self._validate()
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
            Geodataframe
        """
        geometry = [
            box(x_min, y_min, x_min + self._tile_size, y_min + self._tile_size)
            for x_min, y_min in self
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
        bounding_box: Bounding box (x_min, y_min, x_max, y_max)
        gdf: Path to the geodataframe
        json_string: Path to the JSON file containing the coordinates (x_min, y_min) of each tile
            and the tile size
        processed_coordinates_json_string: Path to the JSON file containing the coordinates (x_min, y_min)
            of each tile and the tile size of the processed tiles
        tile_size: Tile size in meters
        quantize: If True, the bounding box is quantized to `tile_size`
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
        """Parses `bounding_box`."""
        if len(bounding_box) != 4:  # noqa: PLR2004
            message = (
                'Invalid bounding_box! '
                'The bounding box must be a list of length 4.'
            )
            raise ValueError(message)

        x_min, y_min, x_max, y_max = bounding_box
        return BoundingBox(
            x_min=x_min,
            y_min=y_min,
            x_max=x_max,
            y_max=y_max,
        )

    # noinspection PyNestedDecorators
    @pydantic.field_validator('gdf')
    @classmethod
    def parse_gdf(
        cls,
        gdf: Path,
    ) -> gpd.GeoDataFrame:
        """Parses `gdf`."""
        return gpd.read_file(gdf)

    # noinspection PyNestedDecorators
    @pydantic.field_validator('json_string')
    @classmethod
    def parse_json_string(
        cls,
        json_string: Path,
    ) -> str:
        """Parses `json_string`."""
        with json_string.open() as file:
            return json.load(file)

    # noinspection PyNestedDecorators
    @pydantic.field_validator('processed_coordinates_json_string')
    @classmethod
    def parse_processed_coordinates_json_string(
        cls,
        processed_coordinates_json_string: Path,
    ) -> str:
        """Parses `processed_coordinates_json_string`."""
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
                'Invalid config! '
                'The configuration must have one of the following field sets: '
                'json_string | gdf, tile_size | bounding_box, tile_size'
            )
            raise ValueError(message)

        return self

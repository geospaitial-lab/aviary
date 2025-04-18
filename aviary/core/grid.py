from __future__ import annotations

import json
from collections.abc import (
    Iterable,
    Iterator,
)
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    overload,
)

import geopandas as gpd
import numpy as np
import pydantic
from shapely.geometry import box

# noinspection PyProtectedMember
from aviary._functional.utils.coordinates_filter import (
    duplicates_filter,
    geospatial_filter,
    set_filter,
)
from aviary.core.bounding_box import BoundingBox
from aviary.core.enums import (
    GeospatialFilterMode,
    SetFilterMode,
)
from aviary.core.exceptions import AviaryUserError
from aviary.core.type_aliases import (
    Coordinate,
    Coordinates,
    CoordinatesSet,
    EPSGCode,
    TileSize,
)

if TYPE_CHECKING:
    from aviary.utils.coordinates_filter import CoordinatesFilter


class Grid(Iterable[Coordinates]):
    """A grid specifies the spatial extent of an area of interest by a set of coordinates
    of the bottom left corner of each tile and the tile size.

    Notes:
        - The coordinates are assumed to be in shape (n, 2) and data type int32, where n is the number of coordinates
        - The coordinates are sorted
    """
    _coordinates: CoordinatesSet

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
        """Validates the grid."""
        self._validate_tile_size()  # valid tile_size is necessary for _validate_coordinates
        self._coerce_coordinates()
        self._validate_coordinates()

    def _coerce_coordinates(self) -> None:
        """Coerces `coordinates`."""
        if self._coordinates is None:
            self._coordinates = np.empty(
                shape=(0, 2),
                dtype=np.int32,
            )

    def _validate_coordinates(self) -> None:
        """Validates `coordinates`.

        Raises:
            AviaryUserError: Invalid `coordinates` (the coordinates are not in shape (n, 2) and data type int32)
            AviaryUserError: Invalid `coordinates` (the coordinates are not evenly distributed)
        """
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

        self._coordinates = duplicates_filter(coordinates=self._coordinates)

        coordinates_x_remainders = self._coordinates[:, 0] % self._tile_size
        coordinates_y_remainders = self._coordinates[:, 1] % self._tile_size
        unique_coordinates_x_remainders = np.unique(coordinates_x_remainders)
        unique_coordinates_y_remainders = np.unique(coordinates_y_remainders)
        conditions = [
            len(unique_coordinates_x_remainders) > 1,
            len(unique_coordinates_y_remainders) > 1,
        ]

        if any(conditions):
            message = (
                'Invalid coordinates! '
                'The coordinates must be evenly distributed.'
            )
            raise AviaryUserError(message)

        sorted_indices = np.lexsort((self._coordinates[:, 0], self._coordinates[:, 1]))
        self._coordinates = self._coordinates[sorted_indices]

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
        snap: bool = True,
    ) -> Grid:
        """Creates a grid from a bounding box.

        Parameters:
            bounding_box: Bounding box
            tile_size: Tile size in meters
            snap: If True, the bounding box is snapped to `tile_size`

        Returns:
            Grid

        Raises:
            AviaryUserError: Invalid `tile_size` (the tile size is negative or zero)
        """
        if tile_size <= 0:
            message = (
                'Invalid tile_size! '
                'The tile size must be positive.'
            )
            raise AviaryUserError(message)

        coordinates = cls._compute_coordinates(
            bounding_box=bounding_box,
            tile_size=tile_size,
            snap=snap,
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
        snap: bool = True,
    ) -> Grid:
        """Creates a grid from a geodataframe.

        Parameters:
            gdf: Geodataframe
            tile_size: Tile size in meters
            snap: If True, the bounding box is snapped to `tile_size`

        Returns:
            Grid

        Raises:
            AviaryUserError: Invalid `gdf` (the geodataframe contains no geometries)
            AviaryUserError: Invalid `gdf` (the geodataframe contains geometries other than polygons)
            AviaryUserError: Invalid `tile_size` (the tile size is negative or zero)
        """
        if gdf.empty:
            message = (
                'Invalid gdf! '
                'The geodataframe must contain at least one geometry.'
            )
            raise AviaryUserError(message)

        if not all(gdf.geometry.geom_type.isin(['Polygon', 'MultiPolygon'])):
            message = (
                'Invalid gdf! '
                'The geodataframe must contain only polygons.'
            )
            raise AviaryUserError(message)

        if tile_size <= 0:
            message = (
                'Invalid tile_size! '
                'The tile size must be positive.'
            )
            raise AviaryUserError(message)

        bounding_box = BoundingBox.from_gdf(gdf=gdf)
        coordinates = cls._compute_coordinates(
            bounding_box=bounding_box,
            tile_size=tile_size,
            snap=snap,
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

    @staticmethod
    def _compute_coordinates(
        bounding_box: BoundingBox,
        tile_size: TileSize,
        snap: bool = True,
    ) -> CoordinatesSet:
        """Computes the coordinates of the bottom left corner of each tile.

        Parameters:
            bounding_box: Bounding box
            tile_size: Tile size in meters
            snap: If True, the bounding box is snapped to `tile_size`

        Returns:
            Coordinates (x_min, y_min) of each tile in meters
        """
        if snap:
            bounding_box = bounding_box.snap(
                value=tile_size,
                inplace=False,
            )

        coordinates_range_x = np.arange(bounding_box.x_min, bounding_box.x_max, tile_size)
        coordinates_range_y = np.arange(bounding_box.y_min, bounding_box.y_max, tile_size)
        coordinates_x, coordinates_y = np.meshgrid(coordinates_range_x, coordinates_range_y)

        coordinates_x = coordinates_x.reshape(-1)[..., np.newaxis]
        coordinates_y = coordinates_y.reshape(-1)[..., np.newaxis]
        return np.concatenate((coordinates_x, coordinates_y), axis=-1).astype(np.int32)

    @classmethod
    def from_json(
        cls,
        json_string: str,
    ) -> Grid:
        """Creates a grid from a JSON string.

        Notes:
            - The JSON string contains a list of coordinates (x_min, y_min) of each tile and the tile size

        Example:
            Assume the JSON string is '{"coordinates":
            [[363084, 5715326], [363212, 5715326], [363084, 5715454], [363212, 5715454]],
            "tile_size": 128}'.

            You can create a grid from the JSON string.

            ``` python
            grid = Grid.from_json(
                json_string=(
                    '{"coordinates": '
                    '[[363084, 5715326], '
                    '[363212, 5715326], '
                    '[363084, 5715454], '
                    '[363212, 5715454]], '
                    '"tile_size": 128}'
                ),
            )
            ```

        Parameters:
            json_string: JSON string

        Returns:
            Grid

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
    def from_grids(
        cls,
        grids: list[Grid],
    ) -> Grid:
        """Creates a grid from grids.

        Parameters:
            grids: Grids

        Returns:
            Grid

        Raises:
            AviaryUserError: Invalid `grids` (the grids contain no grids)
            AviaryUserError: Invalid `grids` (the tile sizes of the grids are not equal)
        """
        if not grids:
            message = (
                'Invalid grids! '
                'The grids must contain at least one grid.'
            )
            raise AviaryUserError(message)

        tile_sizes = {grid.tile_size for grid in grids}

        if len(tile_sizes) > 1:
            message = (
                'Invalid grids! '
                'The tile sizes of the grids must be equal.'
            )
            raise AviaryUserError(message)

        coordinates = np.concatenate([grid.coordinates for grid in grids], axis=0)
        tile_size = grids[0].tile_size
        return cls(
            coordinates=coordinates,
            tile_size=tile_size,
        )

    @classmethod
    def from_config(
        cls,
        config: GridConfig,
    ) -> Grid:
        """Creates a grid from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Grid

        Raises:
            AviaryUserError: Invalid `config`
        """
        if config.bounding_box is not None:
            grid = cls.from_bounding_box(
                bounding_box=config.bounding_box,
                tile_size=config.tile_size,
                snap=config.snap,
            )
        elif config.gdf is not None:
            grid = cls.from_gdf(
                gdf=config.gdf,
                tile_size=config.tile_size,
                snap=config.snap,
            )
        elif config.json_string is not None:
            grid = cls.from_json(
                json_string=config.json_string,
            )
        else:
            message = (
                'Invalid config! '
                'The configuration must have exactly one of the following field combinations: '
                'bounding_box_coordinates, tile_size | gpkg_path, tile_size | json_path'
            )
            raise AviaryUserError(message)

        if config.ignore_bounding_box is not None:
            ignore_grid = cls.from_bounding_box(
                bounding_box=config.ignore_bounding_box,
                tile_size=config.tile_size,
                snap=config.snap,
            )
            grid -= ignore_grid

        if config.ignore_gdf is not None:
            ignore_grid = cls.from_gdf(
                gdf=config.ignore_gdf,
                tile_size=config.tile_size,
                snap=config.snap,
            )
            grid -= ignore_grid

        if config.ignore_json_string is not None:
            ignore_grid = cls.from_json(
                json_string=config.ignore_json_string,
            )
            grid -= ignore_grid

        return grid

    def __repr__(self) -> str:
        """Returns the string representation.

        Returns:
            String representation
        """
        coordinates_repr = len(self)
        return (
            'Grid(\n'
            f'    coordinates={coordinates_repr},\n'
            f'    tile_size={self._tile_size},\n'
            ')'
        )

    def __eq__(
        self,
        other: object,
    ) -> bool:
        """Compares the grids.

        Parameters:
            other: Other grid

        Returns:
            True if the grids are equal, False otherwise
        """
        if not isinstance(other, Grid):
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

    def __bool__(self) -> bool:
        """Checks if the grid contains coordinates.

        Returns:
            True if the grid contains coordinates, False otherwise
        """
        return bool(len(self))

    def __contains__(
        self,
        coordinates: Coordinates | CoordinatesSet,
    ) -> bool:
        """Checks if the coordinates are in the grid.

        Parameters:
            coordinates: Coordinates (x_min, y_min) of the tile in meters

        Returns:
            True if the coordinates are in the grid, False otherwise

        Raises:
            AviaryUserError: Invalid `coordinates` (the coordinates are not in shape (n, 2) and data type int32)
        """
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

        coordinates = np.concatenate([self._coordinates, coordinates], axis=0)
        unique_coordinates = duplicates_filter(coordinates=coordinates)
        return len(self) == len(unique_coordinates)

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
    ) -> Grid:
        ...

    def __getitem__(
        self,
        index: int | slice,
    ) -> Coordinates | Grid:
        """Returns the coordinates or the sliced grid.

        Parameters:
            index: Index or slice of the coordinates

        Returns:
            Coordinates (x_min, y_min) of the tile in meters or grid
        """
        if isinstance(index, slice):
            coordinates = self._coordinates[index]
            return Grid(
                coordinates=coordinates,
                tile_size=self._tile_size,
            )

        x_min, y_min = self._coordinates[index]
        return int(x_min), int(y_min)

    def __iter__(self) -> Iterator[Coordinates]:
        """Iterates over the coordinates.

        Yields:
            Coordinates (x_min, y_min) of the tile in meters
        """
        for x_min, y_min in self._coordinates:
            yield int(x_min), int(y_min)

    def __add__(
        self,
        other: Grid,
    ) -> Grid:
        """Adds the grids.

        Parameters:
            other: Other grid

        Returns:
            Grid

        Raises:
            AviaryUserError: Invalid `other` (the tile sizes of the grids are not equal)
        """
        if self._tile_size != other.tile_size:
            message = (
                'Invalid other! '
                'The tile sizes of the grids must be equal.'
            )
            raise AviaryUserError(message)

        coordinates = set_filter(
            coordinates=self._coordinates,
            other=other.coordinates,
            mode=SetFilterMode.UNION,
        )
        return Grid(
            coordinates=coordinates,
            tile_size=self._tile_size,
        )

    def __sub__(
        self,
        other: Grid,
    ) -> Grid:
        """Subtracts the grids.

        Parameters:
            other: Other grid

        Returns:
            Grid

        Raises:
            AviaryUserError: Invalid `other` (the tile sizes of the grids are not equal)
        """
        if self._tile_size != other.tile_size:
            message = (
                'Invalid other! '
                'The tile sizes of the grids must be equal.'
            )
            raise AviaryUserError(message)

        coordinates = set_filter(
            coordinates=self._coordinates,
            other=other.coordinates,
            mode=SetFilterMode.DIFFERENCE,
        )
        return Grid(
            coordinates=coordinates,
            tile_size=self._tile_size,
        )

    def __and__(
        self,
        other: Grid,
    ) -> Grid:
        """Intersects the grids.

        Parameters:
            other: Other grid

        Returns:
            Grid

        Raises:
            AviaryUserError: Invalid `other` (the tile sizes of the grids are not equal)
        """
        if self._tile_size != other.tile_size:
            message = (
                'Invalid other! '
                'The tile sizes of the grids must be equal.'
            )
            raise AviaryUserError(message)

        coordinates = set_filter(
            coordinates=self._coordinates,
            other=other.coordinates,
            mode=SetFilterMode.INTERSECTION,
        )
        return Grid(
            coordinates=coordinates,
            tile_size=self._tile_size,
        )

    def __or__(
        self,
        other: Grid,
    ) -> Grid:
        """Unions the grids.

        Parameters:
            other: Other grid

        Returns:
            Grid

        Raises:
            AviaryUserError: Invalid `other` (the tile sizes of the grids are not equal)
        """
        if self._tile_size != other.tile_size:
            message = (
                'Invalid other! '
                'The tile sizes of the grids must be equal.'
            )
            raise AviaryUserError(message)

        coordinates = set_filter(
            coordinates=self._coordinates,
            other=other.coordinates,
            mode=SetFilterMode.UNION,
        )
        return Grid(
            coordinates=coordinates,
            tile_size=self._tile_size,
        )

    def append(
        self,
        coordinates: Coordinates | CoordinatesSet,
        inplace: bool = False,
    ) -> Grid:
        """Appends the coordinates.

        Parameters:
            coordinates: Coordinates (x_min, y_min) of the tile or of each tile in meters
            inplace: If True, the coordinates are appended inplace

        Returns:
            Grid

        Raises:
            AviaryUserError: Invalid `coordinates` (the coordinates are not in shape (n, 2) and data type int32)
        """
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

        coordinates = set_filter(
            coordinates=self._coordinates,
            other=coordinates,
            mode=SetFilterMode.UNION,
        )

        if inplace:
            self._coordinates = coordinates
            self._validate()
            return self

        return Grid(
            coordinates=coordinates,
            tile_size=self._tile_size,
        )

    def chunk(
        self,
        num_chunks: int,
    ) -> list[Grid]:
        """Chunks the grid.

        Parameters:
            num_chunks: Number of chunks

        Returns:
            Grids

        Raises:
            AviaryUserError: Invalid `num_chunks` (the number of chunks is not in the range [1, n])
        """
        if num_chunks < 1 or num_chunks > len(self):
            message = (
                'Invalid num_chunks! '
                'The number of chunks must be in the range [1, n].'
            )
            raise AviaryUserError(message)

        return [
            Grid(
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
    ) -> Grid:
        """Filters the grid.

        Parameters:
            coordinates_filter: Coordinates filter
            inplace: If True, the coordinates are filtered inplace

        Returns:
            Grid
        """
        coordinates = coordinates_filter(coordinates=self._coordinates)

        if inplace:
            self._coordinates = coordinates
            self._validate()
            return self

        return Grid(
            coordinates=coordinates,
            tile_size=self._tile_size,
        )

    def remove(
        self,
        coordinates: Coordinates | CoordinatesSet,
        inplace: bool = False,
    ) -> Grid:
        """Removes the coordinates.

        Parameters:
            coordinates: Coordinates (x_min, y_min) of the tile or of each tile in meters
            inplace: If True, the coordinates are removed inplace

        Returns:
            Grid

        Raises:
            AviaryUserError: Invalid `coordinates` (the coordinates are not in shape (n, 2) and data type int32)
        """
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

        coordinates = set_filter(
            coordinates=self._coordinates,
            other=coordinates,
            mode=SetFilterMode.DIFFERENCE,
        )

        if inplace:
            self._coordinates = coordinates
            self._validate()
            return self

        return Grid(
            coordinates=coordinates,
            tile_size=self._tile_size,
        )

    def to_gdf(
        self,
        epsg_code: EPSGCode | None,
    ) -> gpd.GeoDataFrame:
        """Converts the grid to a geodataframe.

        Parameters:
            epsg_code: EPSG code

        Returns:
            Geodataframe
        """
        geometry = [
            box(x_min, y_min, x_min + self._tile_size, y_min + self._tile_size)
            for x_min, y_min in self
        ]
        epsg_code = f'EPSG:{epsg_code}' if epsg_code is not None else None
        return gpd.GeoDataFrame(
            geometry=geometry,
            crs=epsg_code,
        )

    def to_json(self) -> str:
        """Converts the grid to a JSON string.

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


class GridConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `Grid`

    The configuration must have exactly one of the following field combinations:
        - `bounding_box_coordinates` and `tile_size`
        - `gpkg_path` and `tile_size`
        - `json_path`

    Create the configuration from a config file:
        - Use null instead of None
        - Use false or true instead of False or True

    Example:
        You can create a configuration from a config file.

        ``` yaml title="config.yaml"
        bounding_box_coordinates:
          - 363084
          - 5715326
          - 363340
          - 5715582
        gpkg_path: null
        json_path: null
        ignore_bounding_box_coordinates: null
        ignore_gpkg_path: null
        ignore_json_path: null
        tile_size: 128
        snap: true
        ```

    Attributes:
        bounding_box_coordinates: Bounding box coordinates (x_min, y_min, x_max, y_max) in meters -
            defaults to None
        gpkg_path: Path to the geopackage (.gpkg file) -
            defaults to None
        json_path: Path to the JSON file (.json file) -
            defaults to None
        ignore_bounding_box_coordinates: Bounding box coordinates to ignore (x_min, y_min, x_max, y_max) in meters -
            defaults to None
        ignore_gpkg_path: Path to the geopackage (.gpkg file) to ignore -
            defaults to None
        ignore_json_path: Path to the JSON file (.json file) to ignore -
            defaults to None
        tile_size: Tile size in meters -
            defaults to None
        snap: If True, the bounding box is snapped to `tile_size` -
            defaults to True
    """
    bounding_box_coordinates: tuple[Coordinate, Coordinate, Coordinate, Coordinate] | None = None
    gpkg_path: Path | None = None
    json_path: Path | None = None
    ignore_bounding_box_coordinates: tuple[Coordinate, Coordinate, Coordinate, Coordinate] | None = None
    ignore_gpkg_path: Path | None = None
    ignore_json_path: Path | None = None
    tile_size: TileSize | None = None
    snap: bool = True

    @property
    def bounding_box(self) -> BoundingBox | None:
        """
        Returns:
            Bounding box
        """
        if self.bounding_box_coordinates is None:
            return None

        x_min, y_min, x_max, y_max = self.bounding_box_coordinates
        return BoundingBox(
            x_min=x_min,
            y_min=y_min,
            x_max=x_max,
            y_max=y_max,
        )

    @property
    def gdf(self) -> gpd.GeoDataFrame | None:
        """
        Returns:
            Geodataframe
        """
        if self.gpkg_path is None:
            return None

        return gpd.read_file(self.gpkg_path)

    @property
    def json_string(self) -> str | None:
        """
        Returns:
            JSON string
        """
        if self.json_path is None:
            return None

        with self.json_path.open() as file:
            return json.load(file)

    @property
    def ignore_bounding_box(self) -> BoundingBox | None:
        """
        Returns:
            Bounding box
        """
        if self.ignore_bounding_box_coordinates is None:
            return None

        x_min, y_min, x_max, y_max = self.ignore_bounding_box_coordinates
        return BoundingBox(
            x_min=x_min,
            y_min=y_min,
            x_max=x_max,
            y_max=y_max,
        )

    @property
    def ignore_gdf(self) -> gpd.GeoDataFrame | None:
        """
        Returns:
            Geodataframe
        """
        if self.ignore_gpkg_path is None:
            return None

        return gpd.read_file(self.ignore_gpkg_path)

    @property
    def ignore_json_string(self) -> str | None:
        """
        Returns:
            JSON string
        """
        if self.ignore_json_path is None:
            return None

        with self.ignore_json_path.open() as file:
            return json.load(file)

    @pydantic.model_validator(mode='after')
    def _validate(self) -> GridConfig:
        """Validates the configuration."""
        conditions = [
            self.bounding_box is not None and self.tile_size is not None,
            self.gdf is not None and self.tile_size is not None,
            self.json_string is not None,
        ]

        if sum(conditions) != 1:
            message = (
                'Invalid config! '
                'The configuration must have exactly one of the following field combinations: '
                'bounding_box_coordinates, tile_size | gpkg_path, tile_size | json_path'
            )
            raise ValueError(message)

        return self


class _GridFactory:
    """Factory for grids"""

    @staticmethod
    def create(
        config: GridConfig,
    ) -> Grid:
        """Creates a grid from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Grid
        """
        return Grid.from_config(config=config)

import geopandas as gpd

from src.functional.data.grid_generator import (
    compute_coordinates,
    generate_grid,
    validate_grid_generator,
)
from src.utils.types import (
    BoundingBox,
    Coordinates,
    EPSGCode,
    TileSize,
    XMax,
    XMin,
    YMax,
    YMin,
)


class GridGenerator:

    def __init__(
        self,
        bounding_box: BoundingBox,
        epsg_code: EPSGCode,
    ) -> None:
        """
        :param bounding_box: bounding box (x_min, y_min, x_max, y_max)
        :param epsg_code: EPSG code
        """
        validate_grid_generator(
            bounding_box=bounding_box,
            epsg_code=epsg_code,
        )

        self.bounding_box = bounding_box
        self.epsg_code = epsg_code

        self._x_min, self._y_min, self._x_max, self._y_max = self.bounding_box

    @property
    def x_min(self) -> XMin:
        """
        | Minimum x coordinate of the bounding box.

        :return: x_min
        """
        return self._x_min

    @property
    def y_min(self) -> YMin:
        """
        | Minimum y coordinate of the bounding box.

        :return: y_min
        """
        return self._y_min

    @property
    def x_max(self) -> XMax:
        """
        | Maximum x coordinate of the bounding box.

        :return: x_max
        """
        return self._x_max

    @property
    def y_max(self) -> YMax:
        """
        | Maximum y coordinate of the bounding box.

        :return: y_max
        """
        return self._y_max

    def compute_coordinates(
        self,
        tile_size: TileSize,
        quantize: bool = True,
    ) -> Coordinates:
        """
        | Computes the coordinates of the bottom left corner of each tile.

        :param tile_size: tile size in meters
        :param quantize: if True, the bounding box is quantized to tile_size
        :return: coordinates (x_min, y_min) of each tile
        """
        return compute_coordinates(
            tile_size=tile_size,
            x_min=self._x_min,
            y_min=self._y_min,
            x_max=self._x_max,
            y_max=self._y_max,
            quantize=quantize,
        )

    def generate_grid(
        self,
        tile_size: TileSize,
        quantize: bool = True,
    ) -> gpd.GeoDataFrame:
        """
        | Generates a geodataframe of the grid.

        :param tile_size: tile size in meters
        :param quantize: if True, the bounding box is quantized to tile_size
        :return: grid
        """
        return generate_grid(
            tile_size=tile_size,
            x_min=self._x_min,
            y_min=self._y_min,
            x_max=self._x_max,
            y_max=self._y_max,
            epsg_code=self.epsg_code,
            quantize=quantize,
        )

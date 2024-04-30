import geopandas as gpd

from src.functional.geodata.grid_generator import (
    compute_coordinates,
    generate_grid,
)
from src.utils.types import (
    BoundingBox,
    Coordinates,
    EPSGCode,
    TileSize,
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
        self.bounding_box = bounding_box
        self.epsg_code = epsg_code

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
            bounding_box=self.bounding_box,
            tile_size=tile_size,
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
            bounding_box=self.bounding_box,
            tile_size=tile_size,
            epsg_code=self.epsg_code,
            quantize=quantize,
        )

import geopandas as gpd

from .._functional.geodata.grid_generator import (
    compute_coordinates,
    generate_grid,
)
from .._utils.types import (
    BoundingBox,
    Coordinates,
    EPSGCode,
    TileSize,
)


class GridGenerator:
    """Grid generator

    A grid generator generates a grid of tiles.
    The grid generator can be used to compute the coordinates of the bottom left corner of each tile
    or to generate a geodataframe of the grid for aggregation.
    """

    def __init__(
        self,
        bounding_box: BoundingBox,
        epsg_code: EPSGCode,
    ) -> None:
        """
        Parameters:
            bounding_box: bounding box
            epsg_code: EPSG code
        """
        self.bounding_box = bounding_box
        self.epsg_code = epsg_code

    def compute_coordinates(
        self,
        tile_size: TileSize,
        quantize: bool = True,
    ) -> Coordinates:
        """Computes the coordinates of the bottom left corner of each tile.

        Parameters:
            tile_size: tile size in meters
            quantize: if True, the bounding box is quantized to `tile_size`

        Returns:
            coordinates (x_min, y_min) of each tile
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
        """Generates a geodataframe of the grid.

        Parameters:
            tile_size: tile size in meters
            quantize: if True, the bounding box is quantized to `tile_size`

        Returns:
            grid
        """
        return generate_grid(
            bounding_box=self.bounding_box,
            tile_size=tile_size,
            epsg_code=self.epsg_code,
            quantize=quantize,
        )

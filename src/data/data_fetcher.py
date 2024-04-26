from pathlib import Path
from typing import Protocol

import numpy.typing as npt

from src.functional.data.data_fetcher import (
    vrt_data_fetcher,
    vrt_data_fetcher_info,
)
from src.utils.types import (
    BoundingBox,
    BufferSize,
    DType,
    EPSGCode,
    GroundSamplingDistance,
    InterpolationMode,
    TileSize,
    XMin,
    YMin,
)


class DataFetcher(Protocol):

    def __call__(
        self,
        x_min: XMin,
        y_min: YMin,
    ) -> npt.NDArray:
        """
        | Fetches the data.

        :param x_min: minimum x coordinate
        :param y_min: minimum y coordinate
        :return: data
        """
        ...


class VRTDataFetcher:
    _FILL_VALUE = 0

    def __init__(
        self,
        path: Path,
        tile_size: TileSize,
        ground_sampling_distance: GroundSamplingDistance,
        interpolation_mode: InterpolationMode = InterpolationMode.BILINEAR,
        buffer_size: BufferSize = None,
        drop_channels: list[int] = None,
    ) -> None:
        """
        :param path: path to the VRT file
        :param tile_size: tile size in meters
        :param ground_sampling_distance: ground sampling distance in meters
        :param interpolation_mode: interpolation mode (InterpolationMode.BILINEAR or InterpolationMode.NEAREST)
        :param buffer_size: buffer size in meters
        :param drop_channels: channel indices to drop
        """
        self.path = path
        self.tile_size = tile_size
        self.ground_sampling_distance = ground_sampling_distance
        self.interpolation_mode = interpolation_mode
        self.buffer_size = buffer_size
        self.drop_channels = drop_channels

        self._data_fetcher_info = vrt_data_fetcher_info(
            path=self.path,
        )

    @property
    def src_bounding_box(self) -> BoundingBox:
        """
        | Bounding box of the VRT file.

        :return: bounding box (x_min, y_min, x_max, y_max)
        """
        return self._data_fetcher_info.bounding_box

    @property
    def src_dtype(self) -> list[DType]:
        """
        | Data type of each channel of the VRT file.

        :return: data type of each channel
        """
        return self._data_fetcher_info.dtype

    @property
    def src_epsg_code(self) -> EPSGCode:
        """
        | EPSG code of the VRT file.

        :return: EPSG code
        """
        return self._data_fetcher_info.epsg_code

    @property
    def src_ground_sampling_distance_(self) -> GroundSamplingDistance:
        """
        | Ground sampling distance of the VRT file.

        :return: ground sampling distance
        """
        return self._data_fetcher_info.ground_sampling_distance

    @property
    def src_num_channels(self) -> int:
        """
        | Number of channels of the VRT file.

        :return: number of channels
        """
        return self._data_fetcher_info.num_channels

    def __call__(
        self,
        x_min: XMin,
        y_min: YMin,
    ) -> npt.NDArray:
        """
        | Fetches the data from the VRT file.

        :param x_min: minimum x coordinate
        :param y_min: minimum y coordinate
        :return: data
        """
        return vrt_data_fetcher(
            x_min=x_min,
            y_min=y_min,
            path=self.path,
            tile_size=self.tile_size,
            ground_sampling_distance=self.ground_sampling_distance,
            interpolation_mode=self.interpolation_mode,
            buffer_size=self.buffer_size,
            drop_channels=self.drop_channels,
            fill_value=self._FILL_VALUE,
        )

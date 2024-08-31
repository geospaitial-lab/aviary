from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pydantic
from rich.progress import track

# noinspection PyProtectedMember
from aviary._utils.types import (
    ProcessArea,
    ProcessAreaConfig,
)
from aviary.data.data_fetcher import (  # noqa: F401,TCH001
    CompositeFetcher,
    CompositeFetcherConfig,
    VRTFetcher,
    VRTFetcherConfig,
    WMSFetcher,
    WMSFetcherConfig,
)
from aviary.data.data_loader import DataLoader
from aviary.data.data_preprocessor import (  # noqa: F401,TCH001
    CompositePreprocessor,
    CompositePreprocessorConfig,
    NormalizePreprocessor,
    NormalizePreprocessorConfig,
    StandardizePreprocessor,
    StandardizePreprocessorConfig,
)
from aviary.data.dataset import Dataset
from aviary.inference.exporter import (  # noqa: TCH001
    SegmentationExporter,
    SegmentationExporterConfig,
)
from aviary.inference.model import (  # noqa: F401,TCH001
    ONNXSegmentationModel,
    SegmentationModelConfig,
)

if TYPE_CHECKING:
    from aviary.data.data_fetcher import DataFetcher
    from aviary.data.data_preprocessor import DataPreprocessor
    from aviary.inference.model import SegmentationModel


class SegmentationPipeline:
    """Pre-built segmentation pipeline"""

    def __init__(
        self,
        data_fetcher: DataFetcher,
        data_preprocessor: DataPreprocessor,
        process_area: ProcessArea,
        model: SegmentationModel,
        exporter: SegmentationExporter,
        batch_size: int = 1,
        num_workers: int = 4,
    ) -> None:
        """
        Parameters:
            data_fetcher: data fetcher
            data_preprocessor: data preprocessor
            process_area: process area
            model: model
            exporter: exporter
            batch_size: batch size
            num_workers: number of workers
        """
        self.data_fetcher = data_fetcher
        self.data_preprocessor = data_preprocessor
        self.process_area = process_area
        self.model = model
        self.exporter = exporter
        self.batch_size = batch_size
        self.num_workers = num_workers

    @classmethod
    def from_config(
        cls,
        config: SegmentationPipelineConfig,
    ) -> SegmentationPipeline:
        """Creates a segmentation pipeline from the configuration.

        Parameters:
            config: configuration

        Returns:
            segmentation pipeline
        """
        data_fetcher_class = globals()[config.data_fetcher_config.name]
        data_fetcher = data_fetcher_class.from_config(config.data_fetcher_config.config)

        data_preprocessor_class = globals()[config.data_preprocessor_config.name]
        data_preprocessor = data_preprocessor_class.from_config(config.data_preprocessor_config.config)

        process_area = ProcessArea.from_config(config.process_area_config)

        model_class = globals()[config.segmentation_model_config.name]
        model = model_class.from_config(config.segmentation_model_config.config)

        exporter_class = globals()[config.exporter_config.name]
        exporter = exporter_class.from_config(config.exporter_config.config)

        return cls(
            data_fetcher=data_fetcher,
            data_preprocessor=data_preprocessor,
            process_area=process_area,
            model=model,
            exporter=exporter,
            batch_size=config.batch_size,
            num_workers=config.num_workers,
        )

    def __call__(self) -> None:  # pragma: no cover
        """Runs the segmentation pipeline."""
        dataset = Dataset(
            data_fetcher=self.data_fetcher,
            data_preprocessor=self.data_preprocessor,
            coordinates=self.process_area.coordinates,
        )
        data_loader = DataLoader(
            dataset=dataset,
            batch_size=self.batch_size,
            num_workers=self.num_workers,
        )

        for data, x_min, y_min in track(data_loader, description='Processing'):
            preds = self.model(data)
            coordinates = np.column_stack((x_min, y_min))
            self.exporter(preds, coordinates)


class SegmentationPipelineConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `SegmentationPipeline`

    Attributes:
        data_fetcher_config: configuration of the data fetcher
        data_preprocessor_config: configuration of the data preprocessor
        process_area_config: configuration of the process area
        segmentation_model_config: configuration of the model
        exporter_config: configuration of the exporter
        batch_size: batch size
        num_workers: number of workers
    """
    data_fetcher_config: DataFetcherConfig = pydantic.Field(alias='data_fetcher')
    data_preprocessor_config: DataPreprocessorConfig = pydantic.Field(alias='data_preprocessor')
    process_area_config: ProcessAreaConfig = pydantic.Field(alias='process_area')
    # model_config is a reserved name in Pydantic's namespace, hence the alias segmentation_model_config
    segmentation_model_config: ModelConfig = pydantic.Field(alias='model')
    exporter_config: ExporterConfig = pydantic.Field(alias='exporter')
    batch_size: int = 1
    num_workers: int = 4


class DataFetcherConfig(pydantic.BaseModel):
    """Configuration for data fetchers

    Attributes:
        name: name of the data fetcher
        config: configuration of the data fetcher
    """
    name: str
    config: (
        CompositeFetcherConfig |
        VRTFetcherConfig |
        WMSFetcherConfig
    )


class DataPreprocessorConfig(pydantic.BaseModel):
    """Configuration for data preprocessors

    Attributes:
        name: name of the data preprocessor
        config: configuration of the data preprocessor
    """
    name: str
    config: (
        CompositePreprocessorConfig |
        NormalizePreprocessorConfig |
        StandardizePreprocessorConfig
    )


class ModelConfig(pydantic.BaseModel):
    """Configuration for models

    Attributes:
        name: name of the model
        config: configuration of the model
    """
    name: str
    config: SegmentationModelConfig


class ExporterConfig(pydantic.BaseModel):
    """Configuration for exporters

    Attributes:
        name: name of the exporter
        config: configuration of the exporter
    """
    name: str
    config: SegmentationExporterConfig

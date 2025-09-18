from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pydantic

from aviary.core.type_aliases import EPSGCode
from aviary.vector.vector_processor import _VectorProcessorFactory

if TYPE_CHECKING:
    from aviary.core.vector import Vector

_PACKAGE = 'aviary'


class VectorExporter:
    """Vector processor that exports a layer

    The vector data is exported to a geopackage.

    Implements the `VectorProcessor` protocol.
    """

    def __init__(
        self,
        layer_name: str,
        epsg_code: EPSGCode | None,
        dir_path: Path,
        gpkg_name: str,
        remove_layer: bool = True,
    ) -> None:
        """
        Parameters:
            layer_name: Layer name
            epsg_code: EPSG code
            dir_path: Path to the directory
            gpkg_name: Name of the geopackage (.gpkg file)
            remove_layer: If True, the layer is removed
        """
        self._layer_name = layer_name
        self._epsg_code = epsg_code
        self._dir_path = dir_path
        self._gpkg_name = gpkg_name
        self._remove_layer = remove_layer

    @classmethod
    def from_config(
        cls,
        config: VectorExporterConfig,
    ) -> VectorExporter:
        """Creates a vector exporter from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Vector exporter
        """
        config = config.model_dump()
        return cls(**config)

    def __call__(
        self,
        vector: Vector,
    ) -> Vector:
        """Exports the layer.

        Parameters:
            vector: Vector

        Returns:
            Vector
        """


class VectorExporterConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `VectorExporter`

    Create the configuration from a config file:
        - Use null instead of None
        - Use false or true instead of False or True

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'VectorExporter'
        config:
          layer_name: 'my_layer'
          epsg_code: 25832
          dir_path: 'path/to/my/directory'
          gpkg_name: 'my_layer.gpkg'
          remove_layer: true
        ```

    Attributes:
        layer_name: Layer name
        epsg_code: EPSG code
        dir_path: Path to the directory
        gpkg_name: Name of the geopackage (.gpkg file)
        remove_layer: If True, the layer is removed -
            defaults to True
    """
    layer_name: str
    epsg_code: EPSGCode | None
    dir_path: Path
    gpkg_name: str
    remove_layer: bool = True


_VectorProcessorFactory.register(
    vector_processor_class=VectorExporter,
    config_class=VectorExporterConfig,
    package=_PACKAGE,
)

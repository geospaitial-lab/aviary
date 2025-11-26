#  Copyright (C) 2024-2025 Marius Maryniak
#
#  This file is part of aviary.
#
#  aviary is free software: you can redistribute it and/or modify it under the terms of the
#  GNU General Public License as published by the Free Software Foundation,
#  either version 3 of the License, or (at your option) any later version.
#
#  aviary is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with aviary.
#  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Protocol,
)

if TYPE_CHECKING:
    from collections.abc import Callable

import pydantic

if TYPE_CHECKING:
    from pydantic_core.core_schema import ValidationInfo

# noinspection PyProtectedMember
from aviary._functional.vector.vector_loader import (
    bounding_box_loader,
    composite_loader,
    gpkg_loader,
)
from aviary.core.bounding_box import BoundingBox
from aviary.core.exceptions import AviaryUserError
from aviary.core.type_aliases import (
    Coordinate,
    EPSGCode,
)

if TYPE_CHECKING:
    from aviary.core.vector import Vector

_PACKAGE = 'aviary'


class VectorLoader(Protocol):
    """Protocol for vector loaders

    Vector loaders are callables that load a vector from a source.

    Implemented vector loaders:
        - `CompositeLoader`: Composes multiple vector loaders
        - `BoundingBoxLoader`: Loads a vector from a bounding box
        - `GPKGLoader`: Loads a vector from a geopackage or a directory containing geopackages
    """

    def __call__(self) -> Vector:
        """Loads a vector from the source.

        Returns:
            Vector
        """
        ...


class VectorLoaderConfig(pydantic.BaseModel):
    """Configuration for vector loaders

    Create the configuration from a config file:
        - Use null instead of None

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'VectorLoader'
        config:
          ...
        ```

    Attributes:
        package: Package -
            defaults to 'aviary'
        name: Name
        config: Configuration -
            defaults to None
    """
    package: str = 'aviary'
    name: str
    config: pydantic.BaseModel | None = None

    # noinspection PyNestedDecorators
    @pydantic.field_validator(
        'config',
        mode='before',
    )
    @classmethod
    def _validate_config(
        cls,
        value: Any,  # noqa: ANN401
        info: ValidationInfo,
    ) -> pydantic.BaseModel:
        package = info.data['package']
        name = info.data['name']
        key = (package, name)
        registry_entry = _VectorLoaderFactory.registry.get(key)

        if registry_entry is None:
            message = (
                'Invalid config! '
                f'The vector loader {name} from {package} must be registered.'
            )
            raise ValueError(message)

        _, config_class = registry_entry

        if value is None:
            return config_class()

        if isinstance(value, config_class):
            return value

        return config_class(**value)


class _VectorLoaderFactory:
    """Factory for vector loaders"""
    registry: dict[tuple[str, str], tuple[type[VectorLoader], type[pydantic.BaseModel]]] = {}  # noqa: RUF012

    @staticmethod
    def create(
        config: VectorLoaderConfig,
    ) -> VectorLoader:
        """Creates a vector loader from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Vector loader

        Raises:
            AviaryUserError: Invalid `config` (the vector loader is not registered)
        """
        key = (config.package, config.name)
        registry_entry = _VectorLoaderFactory.registry.get(key)

        if registry_entry is None:
            message = (
                'Invalid config! '
                f'The vector loader {config.name} from {config.package} must be registered.'
            )
            raise AviaryUserError(message) from None

        vector_loader_class, _ = registry_entry
        # noinspection PyUnresolvedReferences
        return vector_loader_class.from_config(config=config.config)

    @staticmethod
    def register(
        vector_loader_class: type[VectorLoader],
        config_class: type[pydantic.BaseModel],
        package: str = _PACKAGE,
    ) -> None:
        """Registers a vector loader.

        Parameters:
            vector_loader_class: Vector loader class
            config_class: Configuration class
            package: Package
        """
        key = (package, vector_loader_class.__name__)
        _VectorLoaderFactory.registry[key] = (vector_loader_class, config_class)


def register_vector_loader(
    config_class: type[pydantic.BaseModel],
) -> Callable:
    """Registers a vector loader.

    Parameters:
        config_class: Configuration class

    Returns:
        Decorator

    Raises:
        AviaryUserError: Invalid registration (the package is equal to aviary)
    """
    def decorator(
        cls: type[VectorLoader],
    ) -> type[VectorLoader]:
        package = cls.__module__.split('.')[0]

        if package == _PACKAGE:
            message = (
                'Invalid registration! '
                f'The package must be different from {_PACKAGE}.'
            )
            raise AviaryUserError(message)

        _VectorLoaderFactory.register(
            vector_loader_class=cls,
            config_class=config_class,
            package=package,
        )
        return cls
    return decorator


class CompositeLoader:
    """Vector loader that composes multiple vector loaders

    Notes:
        - The vector loaders are called concurrently depending on the maximum number of threads
        - If the maximum number of threads is 1, the vector loaders are composed vertically, i.e., in sequence
        - If the maximum number of threads is greater than 1, the vector loaders are composed horizontally, i.e.,
            in parallel

    Implements the `VectorLoader` protocol.
    """

    def __init__(
        self,
        vector_loaders: list[VectorLoader],
        max_num_threads: int | None = None,
    ) -> None:
        """
        Parameters:
            vector_loaders: Vector loaders
            max_num_threads: Maximum number of threads
        """
        self._vector_loaders = vector_loaders
        self._max_num_threads = max_num_threads

    @classmethod
    def from_config(
        cls,
        config: CompositeLoaderConfig,
    ) -> CompositeLoader:
        """Creates a composite loader from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Composite loader
        """
        vector_loaders = [
            _VectorLoaderFactory.create(config=vector_loader_config)
            for vector_loader_config in config.vector_loader_configs
        ]
        return cls(
            vector_loaders=vector_loaders,
            max_num_threads=config.max_num_threads,
        )

    def __call__(self) -> Vector:
        """Loads a vector from the sources.

        Returns:
            Vector
        """
        return composite_loader(
            vector_loaders=self._vector_loaders,
            max_num_threads=self._max_num_threads,
        )


class CompositeLoaderConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `CompositeLoader`

    Create the configuration from a config file:
        - Use null instead of None

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'CompositeLoader'
        config:
          vector_loader_configs:
            - ...
            ...
          max_num_threads: null
        ```

    Attributes:
        vector_loader_configs: Configurations of the vector loaders
        max_num_threads: Maximum number of threads -
            defaults to None
    """
    vector_loader_configs: list[VectorLoaderConfig]
    max_num_threads: int | None = None


_VectorLoaderFactory.register(
    vector_loader_class=CompositeLoader,
    config_class=CompositeLoaderConfig,
    package=_PACKAGE,
)


class BoundingBoxLoader:
    """Vector loader for bounding boxes

    Implements the `VectorLoader` protocol.
    """

    def __init__(
        self,
        bounding_box: BoundingBox,
        epsg_code: EPSGCode,
        layer_name: str,
    ) -> None:
        """
        Parameters:
            bounding_box: Bounding box
            epsg_code: EPSG code
            layer_name: Layer name
        """
        self._bounding_box = bounding_box
        self._epsg_code = epsg_code
        self._layer_name = layer_name

    @classmethod
    def from_config(
        cls,
        config: BoundingBoxLoaderConfig,
    ) -> BoundingBoxLoader:
        """Creates a bounding box loader from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Bounding box loader
        """
        return cls(
            bounding_box=config.bounding_box,
            epsg_code=config.epsg_code,
            layer_name=config.layer_name,
        )

    def __call__(self) -> Vector:
        """Loads a vector from the bounding box.

        Returns:
            Vector
        """
        return bounding_box_loader(
            bounding_box=self._bounding_box,
            epsg_code=self._epsg_code,
            layer_name=self._layer_name,
        )


class BoundingBoxLoaderConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `BoundingBoxLoader`

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'BoundingBoxLoader'
        config:
          bounding_box_coordinates:
          - 363084
          - 5715326
          - 363340
          - 5715582
          epsg_code: 25832
          layer_name: 'my_layer'
        ```

    Attributes:
        bounding_box_coordinates: Bounding box coordinates (x_min, y_min, x_max, y_max) in meters
        epsg_code: EPSG code
        layer_name: Layer name
    """
    bounding_box_coordinates: tuple[Coordinate, Coordinate, Coordinate, Coordinate]
    epsg_code: EPSGCode
    layer_name: str

    @property
    def bounding_box(self) -> BoundingBox:
        """
        Returns:
            Bounding box
        """
        x_min, y_min, x_max, y_max = self.bounding_box_coordinates
        return BoundingBox(
            x_min=x_min,
            y_min=y_min,
            x_max=x_max,
            y_max=y_max,
        )


_VectorLoaderFactory.register(
    vector_loader_class=BoundingBoxLoader,
    config_class=BoundingBoxLoaderConfig,
    package=_PACKAGE,
)


class GPKGLoader:
    """Vector loader for geopackages

    Implements the `VectorLoader` protocol.
    """

    def __init__(
        self,
        path: Path,
        layer_name: str,
        max_num_threads: int | None = None,
    ) -> None:
        """
        Parameters:
            path: Path to the geopackage (.gpkg file) or to the directory containing geopackages (.gpkg files)
                exported by the `tile.VectorExporter`
            layer_name: Layer name
            max_num_threads: Maximum number of threads
        """
        self._path = path
        self._layer_name = layer_name
        self._max_num_threads = max_num_threads

    @classmethod
    def from_config(
        cls,
        config: GPKGLoaderConfig,
    ) -> GPKGLoader:
        """Creates a GPKG loader from the configuration.

        Parameters:
            config: Configuration

        Returns:
            GPKG loader
        """
        config = config.model_dump()
        return cls(**config)

    def __call__(self) -> Vector:
        """Loads a vector from the geopackage or the directory containing geopackages.

        Returns:
            Vector
        """
        return gpkg_loader(
            path=self._path,
            layer_name=self._layer_name,
            max_num_threads=self._max_num_threads,
        )


class GPKGLoaderConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `GPKGLoader`

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'GPKGLoader'
        config:
          path: 'path/to/my_gpkg.gpkg'
          layer_name: 'my_layer'
          max_num_threads: null
        ```

    Attributes:
        path: Path to the geopackage (.gpkg file) or to the directory containing geopackages (.gpkg files)
            exported by the `tile.VectorExporter`
        layer_name: Layer name
        max_num_threads: Maximum number of threads
    """
    path: Path
    layer_name: str
    max_num_threads: int | None = None


_VectorLoaderFactory.register(
    vector_loader_class=GPKGLoader,
    config_class=GPKGLoaderConfig,
    package=_PACKAGE,
)

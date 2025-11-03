from __future__ import annotations

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
from aviary._functional.vector.vector_processor import (
    copy_processor,
    parallel_composite_processor,
    query_processor,
    remove_processor,
    select_processor,
    sequential_composite_processor,
)
from aviary.core.exceptions import AviaryUserError

if TYPE_CHECKING:
    from aviary.core.vector import Vector

_PACKAGE = 'aviary'


class VectorProcessor(Protocol):
    """Protocol for vector processors

    Vector processors are callables that process vectors.

    Implemented vector processors:
        - `AggregateProcessor`: Aggregates a layer
        - `ClipProcessor`: Clips a layer
        - `CopyProcessor`: Copies a layer
        - `FillProcessor`: Fills a layer
        - `ParallelCompositeProcessor`: Composes multiple vector processors in parallel
        - `QueryProcessor`: Queries a layer
        - `RemoveProcessor`: Removes layers
        - `SelectProcessor`: Selects layers
        - `SequentialCompositeProcessor`: Composes multiple vector processors in sequence
        - `SieveProcessor`: Sieves a layer
        - `SimplifyProcessor`: Simplifies a layer

    Implemented exporters:
        - `VectorExporter`: Exports a layer
    """

    def __call__(
        self,
        vector: Vector,
    ) -> Vector:
        """Processes the vector.

        Parameters:
            vector: Vector

        Returns:
            Vector
        """
        ...


class VectorProcessorConfig(pydantic.BaseModel):
    """Configuration for vector processors

    Create the configuration from a config file:
        - Use null instead of None

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'VectorProcessor'
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
        registry_entry = _VectorProcessorFactory.registry.get(key)

        if registry_entry is None:
            message = (
                'Invalid config! '
                f'The vector processor {name} from {package} must be registered.'
            )
            raise ValueError(message)

        _, config_class = registry_entry

        if value is None:
            return config_class()

        if isinstance(value, config_class):
            return value

        return config_class(**value)


class _VectorProcessorFactory:
    """Factory for vector processors"""
    registry: dict[tuple[str, str], tuple[type[VectorProcessor], type[pydantic.BaseModel]]] = {}  # noqa: RUF012

    @staticmethod
    def create(
        config: VectorProcessorConfig,
    ) -> VectorProcessor:
        """Creates a vector processor from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Vector processor

        Raises:
            AviaryUserError: Invalid `config` (the vector processor is not registered)
        """
        key = (config.package, config.name)
        registry_entry = _VectorProcessorFactory.registry.get(key)

        if registry_entry is None:
            message = (
                'Invalid config! '
                f'The vector processor {config.name} from {config.package} must be registered.'
            )
            raise AviaryUserError(message) from None

        vector_processor_class, _ = registry_entry
        # noinspection PyUnresolvedReferences
        return vector_processor_class.from_config(config=config.config)

    @staticmethod
    def register(
        vector_processor_class: type[VectorProcessor],
        config_class: type[pydantic.BaseModel],
        package: str = _PACKAGE,
    ) -> None:
        """Registers a vector processor.

        Parameters:
            vector_processor_class: Vector processor class
            config_class: Configuration class
            package: Package
        """
        key = (package, vector_processor_class.__name__)
        _VectorProcessorFactory.registry[key] = (vector_processor_class, config_class)


def register_vector_processor(
    config_class: type[pydantic.BaseModel],
) -> Callable:
    """Registers a vector processor.

    Parameters:
        config_class: Configuration class

    Returns:
        Decorator

    Raises:
        AviaryUserError: Invalid registration (the package name is equal to aviary)
    """
    def decorator(
        cls: type[VectorProcessor],
    ) -> type[VectorProcessor]:
        package = cls.__module__.split('.')[0]

        if package == _PACKAGE:
            message = (
                'Invalid registration! '
                f'The package name must be different from {_PACKAGE}.'
            )
            raise AviaryUserError(message)

        _VectorProcessorFactory.register(
            vector_processor_class=cls,
            config_class=config_class,
            package=package,
        )
        return cls
    return decorator


class AggregateProcessor:
    """Vector processor that aggregates a layer

    The polygons are aggregated by class into the aggregation layer with absolute and relative area fields.

    Implements the `VectorProcessor` protocol.
    """

    def __init__(
        self,
        layer_name: str,
        aggregation_layer_name: str,
        field: str = 'class',
        classes: list[str | int] | None = None,
        background_class: str | int | None = None,
        absolute_area_field_suffix: str = 'absolute_area',
        relative_area_field_suffix: str = 'relative_area',
        new_aggregation_layer_name: str | None = None,
    ) -> None:
        """
        Parameters:
            layer_name: Layer name
            aggregation_layer_name: Aggregation layer name
            field: Field
            classes: Classes (if None, the classes are inferred from the layer)
            background_class: Background class (if None, the background class is ignored)
            absolute_area_field_suffix: Suffix of the absolute area field
            relative_area_field_suffix: Suffix of the relative area field
            new_aggregation_layer_name: New aggregation layer name
        """
        self._layer_name = layer_name
        self._aggregation_layer_name = aggregation_layer_name
        self._field = field
        self._classes = classes
        self._background_class = background_class
        self._absolute_area_field_suffix = absolute_area_field_suffix
        self._relative_area_field_suffix = relative_area_field_suffix
        self._new_aggregation_layer_name = new_aggregation_layer_name

    @classmethod
    def from_config(
        cls,
        config: AggregateProcessorConfig,
    ) -> AggregateProcessor:
        """Creates an aggregate processor from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Aggregate processor
        """
        config = config.model_dump()
        return cls(**config)

    def __call__(
        self,
        vector: Vector,
    ) -> Vector:
        """Aggregates the layer.

        Parameters:
            vector: Vector

        Returns:
            Vector
        """


class AggregateProcessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `AggregateProcessor`

    Create the configuration from a config file:
        - Use null instead of None

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'AggregateProcessor'
        config:
          layer_name: 'my_layer'
          aggregation_layer_name: 'my_aggregation_layer'
          field: 'class'
          classes:
            - 'a'
            - 'b'
            - 'c'
          background_class: null
          absolute_area_field_suffix: 'absolute_area'
          relative_area_field_suffix: 'relative_area'
          new_aggregation_layer_name: 'my_new_aggregation_layer'
        ```

    Attributes:
        layer_name: Layer name
        aggregation_layer_name: Aggregation layer name
        field: Field -
            defaults to 'class'
        classes: Classes (if None, the classes are inferred from the layer) -
            defaults to None
        background_class: Background class (if None, the background class is ignored) -
            defaults to None
        absolute_area_field_suffix: Suffix of the absolute area field -
            defaults to 'absolute_area'
        relative_area_field_suffix: Suffix of the relative area field -
            defaults to 'relative_area'
        new_aggregation_layer_name: New aggregation layer name -
            defaults to None
    """
    layer_name: str
    aggregation_layer_name: str
    field: str = 'class'
    classes: list[str | int] | None = None
    background_class: str | int | None = None
    absolute_area_field_suffix: str = 'absolute_area'
    relative_area_field_suffix: str = 'relative_area'
    new_aggregation_layer_name: str | None = None


class ClipProcessor:
    """Vector processor that clips a layer

    Implements the `VectorProcessor` protocol.
    """

    def __init__(
        self,
        layer_name: str,
        mask_layer_name: str,
        new_layer_name: str | None = None,
    ) -> None:
        """
        Parameters:
            layer_name: Layer name
            mask_layer_name: Mask layer name
            new_layer_name: New layer name
        """
        self._layer_name = layer_name
        self._mask_layer_name = mask_layer_name
        self._new_layer_name = new_layer_name

    @classmethod
    def from_config(
        cls,
        config: ClipProcessorConfig,
    ) -> ClipProcessor:
        """Creates a clip processor from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Clip processor
        """
        config = config.model_dump()
        return cls(**config)

    def __call__(
        self,
        vector: Vector,
    ) -> Vector:
        """Clips the layer.

        Parameters:
            vector: Vector

        Returns:
            Vector
        """


class ClipProcessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `ClipProcessor`

    Create the configuration from a config file:
        - Use null instead of None

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'ClipProcessor'
        config:
          layer_name: 'my_layer'
          mask_layer_name: 'my_mask_layer'
          new_layer_name: 'my_new_layer'
        ```

    Attributes:
        layer_name: Layer name
        mask_layer_name: Mask layer name
        new_layer_name: New layer name -
            defaults to None
    """
    layer_name: str
    mask_layer_name: str
    new_layer_name: str | None = None


_VectorProcessorFactory.register(
    vector_processor_class=ClipProcessor,
    config_class=ClipProcessorConfig,
    package=_PACKAGE,
)


class CopyProcessor:
    """Vector processor that copies a layer

    Implements the `VectorProcessor` protocol.
    """

    def __init__(
        self,
        layer_name: str,
        new_layer_name: str | None = None,
    ) -> None:
        """
        Parameters:
            layer_name: Layer name
            new_layer_name: New layer name
        """
        self._layer_name = layer_name
        self._new_layer_name = new_layer_name

    @classmethod
    def from_config(
        cls,
        config: CopyProcessorConfig,
    ) -> CopyProcessor:
        """Creates a copy processor from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Copy processor
        """
        config = config.model_dump()
        return cls(**config)

    def __call__(
        self,
        vector: Vector,
    ) -> Vector:
        """Copies the layer.

        Parameters:
            vector: Vector

        Returns:
            Vector
        """
        return copy_processor(
            vector=vector,
            layer_name=self._layer_name,
            new_layer_name=self._new_layer_name,
        )


class CopyProcessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `CopyProcessor`

    Create the configuration from a config file:
        - Use null instead of None

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'CopyProcessor'
        config:
          layer_name: 'my_layer'
          new_layer_name: 'my_new_layer'
        ```

    Attributes:
        layer_name: Layer name
        new_layer_name: New layer name -
            defaults to None
    """
    layer_name: str
    new_layer_name: str | None = None


_VectorProcessorFactory.register(
    vector_processor_class=CopyProcessor,
    config_class=CopyProcessorConfig,
    package=_PACKAGE,
)


class FillProcessor:
    """Vector processor that fills a layer

    Implements the `VectorProcessor` protocol.
    """

    def __init__(
        self,
        layer_name: str,
        threshold: float,
        new_layer_name: str | None = None,
    ) -> None:
        """
        Parameters:
            layer_name: Layer name
            threshold: Threshold (the maximum area of the hole within a polygon to retain) in square meters
            new_layer_name: New layer name
        """
        self._layer_name = layer_name
        self._threshold = threshold
        self._new_layer_name = new_layer_name

    @classmethod
    def from_config(
        cls,
        config: FillProcessorConfig,
    ) -> FillProcessor:
        """Creates a fill processor from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Fill processor
        """
        config = config.model_dump()
        return cls(**config)

    def __call__(
        self,
        vector: Vector,
    ) -> Vector:
        """Fills the layer.

        Parameters:
            vector: Vector

        Returns:
            vector: Vector
        """


class FillProcessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `FillProcessor`

    Create the configuration from a config file:
        - Use null instead of None

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'FillProcessor'
        config:
          layer_name: 'my_layer'
          threshold: 1.
          new_layer_name: 'my_new_layer'
        ```

    Attributes:
        layer_name: Layer name
        threshold: Threshold (the maximum area of the hole within a polygon to retain) in square meters
        new_layer_name: New layer name -
            defaults to None
    """
    layer_name: str
    threshold: float
    new_layer_name: str | None = None


_VectorProcessorFactory.register(
    vector_processor_class=FillProcessor,
    config_class=FillProcessorConfig,
    package=_PACKAGE,
)


class ParallelCompositeProcessor:
    """Vector processor that composes multiple vector processors in parallel

    Notes:
        - The vector processors are not called concurrently, but each one gets a copy of the vector
            and the resulting vectors are combined
        - The vector processors are composed horizontally, i.e., in parallel

    Implements the `VectorProcessor` protocol.
    """

    def __init__(
        self,
        vector_processors: list[VectorProcessor],
    ) -> None:
        """
        Parameters:
            vector_processors: Vector processors
        """
        self._vector_processors = vector_processors

    @classmethod
    def from_config(
        cls,
        config: ParallelCompositeProcessorConfig,
    ) -> ParallelCompositeProcessor:
        """Creates a parallel composite processor from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Parallel composite processor
        """
        vector_processors = [
            _VectorProcessorFactory.create(config=vector_processor_config)
            for vector_processor_config in config.vector_processor_configs
        ]
        return cls(
            vector_processors=vector_processors,
        )

    def __call__(
        self,
        vector: Vector,
    ) -> Vector:
        """Processes the vector with each vector processor.

        Parameters:
            vector: Vector

        Returns:
            Vector
        """
        return parallel_composite_processor(
            vector=vector,
            vector_processors=self._vector_processors,
        )


class ParallelCompositeProcessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `ParallelCompositeProcessor`

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'ParallelCompositeProcessor'
        config:
          vector_processor_configs:
            - ...
            ...
        ```

    Attributes:
        vector_processor_configs: Configurations of the vector processors
    """
    vector_processor_configs: list[VectorProcessorConfig]


_VectorProcessorFactory.register(
    vector_processor_class=ParallelCompositeProcessor,
    config_class=ParallelCompositeProcessorConfig,
    package=_PACKAGE,
)


class QueryProcessor:
    """Vector processor that queries a layer

    Implements the `VectorProcessor` protocol.
    """

    def __init__(
        self,
        layer_name: str,
        query_string: str,
        new_layer_name: str | None = None,
    ) -> None:
        """
        Parameters:
            layer_name: Layer name
            query_string: Query string based on the pandas query syntax
            new_layer_name: New layer name
        """
        self._layer_name = layer_name
        self._query_string = query_string
        self._new_layer_name = new_layer_name

    @classmethod
    def from_config(
        cls,
        config: QueryProcessorConfig,
    ) -> QueryProcessor:
        """Creates a query processor from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Query processor
        """
        config = config.model_dump()
        return cls(**config)

    def __call__(
        self,
        vector: Vector,
    ) -> Vector:
        """Queries the layer.

        Parameters:
            vector: Vector

        Returns:
            vector: Vector
        """
        return query_processor(
            vector=vector,
            layer_name=self._layer_name,
            query_string=self._query_string,
            new_layer_name=self._new_layer_name,
        )


class QueryProcessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `QueryProcessor`

    Create the configuration from a config file:
        - Use null instead of None

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'QueryProcessor'
        config:
          layer_name: 'my_layer'
          query_string: 'area > 1'
          new_layer_name: 'my_new_layer'
        ```

    Attributes:
        layer_name: Layer name
        query_string: Query string based on the pandas query syntax
        new_layer_name: New layer name -
            defaults to None
    """
    layer_name: str
    query_string: str
    new_layer_name: str | None = None


_VectorProcessorFactory.register(
    vector_processor_class=QueryProcessor,
    config_class=QueryProcessorConfig,
    package=_PACKAGE,
)


class RemoveProcessor:
    """Vector processor that removes layers

    Implements the `VectorProcessor` protocol.
    """

    def __init__(
        self,
        layer_names: str | set[str] | bool | None = True,
    ) -> None:
        """
        Parameters:
            layer_names: Layer name, layer names, no layers (False or None), or all layers (True)
        """
        self._layer_names = layer_names

    @classmethod
    def from_config(
        cls,
        config: RemoveProcessorConfig,
    ) -> RemoveProcessor:
        """Creates a remove processor from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Remove processor
        """
        config = config.model_dump()
        return cls(**config)

    def __call__(
        self,
        vector: Vector,
    ) -> Vector:
        """Removes the layers.

        Parameters:
            vector: Vector

        Returns:
            Vector
        """
        return remove_processor(
            vector=vector,
            layer_names=self._layer_names,
        )


class RemoveProcessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `RemoveProcessor`

    Create the configuration from a config file:
        - Use null instead of None
        - Use false or true instead of False or True

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'RemoveProcessor'
        config:
          layer_names: true
        ```

    Attributes:
        layer_names: Layer name, layer names, no layers (False or None), or all layers (True) -
            defaults to True
    """
    layer_names: str | set[str] | bool | None = True


_VectorProcessorFactory.register(
    vector_processor_class=RemoveProcessor,
    config_class=RemoveProcessorConfig,
    package=_PACKAGE,
)


class SelectProcessor:
    """Vector processor that selects layers

    Implements the `VectorProcessor` protocol.
    """

    def __init__(
        self,
        layer_names: str | set[str] | bool | None = True,
    ) -> None:
        """
        Parameters:
            layer_names: Layer name, layer names, no layers (False or None), or all layers (True)
        """
        self._layer_names = layer_names

    @classmethod
    def from_config(
        cls,
        config: SelectProcessorConfig,
    ) -> SelectProcessor:
        """Creates a select processor from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Select processor
        """
        config = config.model_dump()
        return cls(**config)

    def __call__(
        self,
        vector: Vector,
    ) -> Vector:
        """Selects the layers.

        Parameters:
            vector: Vector

        Returns:
            Vector
        """
        return select_processor(
            vector=vector,
            layer_names=self._layer_names,
        )


class SelectProcessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `SelectProcessor`

    Create the configuration from a config file:
        - Use null instead of None
        - Use false or true instead of False or True

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'SelectProcessor'
        config:
          layer_names: true
        ```

    Attributes:
        layer_names: Layer name, layer names, no layers (False or None), or all layers (True) -
            defaults to True
    """
    layer_names: str | set[str] | bool | None = True


_VectorProcessorFactory.register(
    vector_processor_class=SelectProcessor,
    config_class=SelectProcessorConfig,
    package=_PACKAGE,
)


class SequentialCompositeProcessor:
    """Vector processor that composes multiple vector processors in sequence

    Notes:
        - The vector processors are composed vertically, i.e., in sequence

    Implements the `VectorProcessor` protocol.
    """

    def __init__(
        self,
        vector_processors: list[VectorProcessor],
    ) -> None:
        """
        Parameters:
            vector_processors: Vector processors
        """
        self._vector_processors = vector_processors

    @classmethod
    def from_config(
        cls,
        config: SequentialCompositeProcessorConfig,
    ) -> SequentialCompositeProcessor:
        """Creates a sequential composite processor from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Sequential composite processor
        """
        vector_processors = [
            _VectorProcessorFactory.create(config=vector_processor_config)
            for vector_processor_config in config.vector_processor_configs
        ]
        return cls(
            vector_processors=vector_processors,
        )

    def __call__(
        self,
        vector: Vector,
    ) -> Vector:
        """Processes the vector with each vector processor.

        Parameters:
            vector: Vector

        Returns:
            Vector
        """
        return sequential_composite_processor(
            vector=vector,
            vector_processors=self._vector_processors,
        )


class SequentialCompositeProcessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `SequentialCompositeProcessor`

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'SequentialCompositeProcessor'
        config:
          vector_processor_configs:
            - ...
            ...
        ```

    Attributes:
        vector_processor_configs: Configurations of the vector processors
    """
    vector_processor_configs: list[VectorProcessorConfig]


_VectorProcessorFactory.register(
    vector_processor_class=SequentialCompositeProcessor,
    config_class=SequentialCompositeProcessorConfig,
    package=_PACKAGE,
)


class SieveProcessor:
    """Vector processor that sieves a layer

    Implements the `VectorProcessor` protocol.
    """

    def __init__(
        self,
        layer_name: str,
        threshold: float,
        new_layer_name: str | None = None,
    ) -> None:
        """
        Parameters:
            layer_name: Layer name
            threshold: Threshold (the minimum area of the polygon to retain) in square meters
            new_layer_name: New layer name
        """
        self._layer_name = layer_name
        self._threshold = threshold
        self._new_layer_name = new_layer_name

    @classmethod
    def from_config(
        cls,
        config: SieveProcessorConfig,
    ) -> SieveProcessor:
        """Creates a sieve processor from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Sieve processor
        """
        config = config.model_dump()
        return cls(**config)

    def __call__(
        self,
        vector: Vector,
    ) -> Vector:
        """Sieves the layer.

        Parameters:
            vector: Vector

        Returns:
            vector: Vector
        """


class SieveProcessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `SieveProcessor`

    Create the configuration from a config file:
        - Use null instead of None

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'SieveProcessor'
        config:
          layer_name: 'my_layer'
          threshold: 1.
          new_layer_name: 'my_new_layer'
        ```

    Attributes:
        layer_name: Layer name
        threshold: Threshold (the minimum area of the polygon to retain) in square meters
        new_layer_name: New layer name -
            defaults to None
    """
    layer_name: str
    threshold: float
    new_layer_name: str | None = None


_VectorProcessorFactory.register(
    vector_processor_class=SieveProcessor,
    config_class=SieveProcessorConfig,
    package=_PACKAGE,
)


class SimplifyProcessor:
    """Vector processor that simplifies a layer

    The polygons are simplified using a topology-preserving Visvalingam-Whyatt algorithm.

    Implements the `VectorProcessor` protocol.
    """

    def __init__(
        self,
        layer_name: str,
        threshold: float,
        new_layer_name: str | None = None,
    ) -> None:
        """
        Parameters:
            layer_name: Layer name
            threshold: Threshold (the minimum area of the triangle defined by three consecutive vertices to retain)
                in square meters
            new_layer_name: New layer name
        """
        self._layer_name = layer_name
        self._threshold = threshold
        self._new_layer_name = new_layer_name

    @classmethod
    def from_config(
        cls,
        config: SimplifyProcessorConfig,
    ) -> SimplifyProcessor:
        """Creates a simplify processor from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Simplify processor
        """
        config = config.model_dump()
        return cls(**config)

    def __call__(
        self,
        vector: Vector,
    ) -> Vector:
        """Simplifies the layer.

        Parameters:
            vector: Vector

        Returns:
            vector: Vector
        """


class SimplifyProcessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `SimplifyProcessor`

    Create the configuration from a config file:
        - Use null instead of None

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'SimplifyProcessor'
        config:
          layer_name: 'my_layer'
          threshold: 1.
          new_layer_name: 'my_new_layer'
        ```

    Attributes:
        layer_name: Layer name
        threshold: Threshold (the minimum area of the triangle defined by three consecutive vertices to retain)
            in square meters
        new_layer_name: New layer name -
            defaults to None
    """
    layer_name: str
    threshold: float
    new_layer_name: str | None = None


_VectorProcessorFactory.register(
    vector_processor_class=SimplifyProcessor,
    config_class=SimplifyProcessorConfig,
    package=_PACKAGE,
)

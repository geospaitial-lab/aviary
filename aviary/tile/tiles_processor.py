#  Copyright (C) 2024-2025 Marius Maryniak
#
#  This file is part of aviary.
#
#  aviary is free software: you can redistribute it and / or modify it under the terms of the
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
from aviary._functional.tile.tiles_processor import (
    copy_processor,
    normalize_processor,
    parallel_composite_processor,
    remove_buffer_processor,
    remove_processor,
    select_processor,
    sequential_composite_processor,
    standardize_processor,
    vectorize_processor,
)
from aviary.core.enums import ChannelName
from aviary.core.exceptions import AviaryUserError
from aviary.core.type_aliases import ChannelNameSet

if TYPE_CHECKING:
    from aviary.core.tiles import Tiles

_PACKAGE = 'aviary'


class TilesProcessor(Protocol):
    """Protocol for tiles processors

    Tiles processors are callables that process tiles.

    Implemented models:
        - `Adois`: Uses the adois model to detect and classify impervious surfaces

    Implemented tiles processors:
        - `CopyProcessor`: Copies a channel
        - `NormalizeProcessor`: Normalizes a channel
        - `ParallelCompositeProcessor`: Composes multiple tiles processors in parallel
        - `RemoveBufferProcessor`: Removes the buffer of channels
        - `RemoveProcessor`: Removes channels
        - `SelectProcessor`: Selects channels
        - `SequentialCompositeProcessor`: Composes multiple tiles processors in sequence
        - `StandardizeProcessor`: Standardizes a channel
        - `VectorizeProcessor`: Vectorizes a channel

    Implemented exporters:
        - `GridExporter`: Exports the grid of the tiles
        - `VectorExporter`: Exports a vector channel
    """

    def __call__(
        self,
        tiles: Tiles,
    ) -> Tiles:
        """Processes the tiles.

        Parameters:
            tiles: Tiles

        Returns:
            Tiles
        """
        ...


class TilesProcessorConfig(pydantic.BaseModel):
    """Configuration for tiles processors

    Create the configuration from a config file:
        - Use null instead of None

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'TilesProcessor'
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
        registry_entry = _TilesProcessorFactory.registry.get(key)

        if registry_entry is None:
            message = (
                'Invalid config! '
                f'The tiles processor {name} from {package} must be registered.'
            )
            raise ValueError(message)

        _, config_class = registry_entry

        if value is None:
            return config_class()

        if isinstance(value, config_class):
            return value

        return config_class(**value)


class _TilesProcessorFactory:
    """Factory for tiles processors"""
    registry: dict[tuple[str, str], tuple[type[TilesProcessor], type[pydantic.BaseModel]]] = {}  # noqa: RUF012

    @staticmethod
    def create(
        config: TilesProcessorConfig,
    ) -> TilesProcessor:
        """Creates a tiles processor from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Tiles processor

        Raises:
            AviaryUserError: Invalid `config` (the tiles processor is not registered)
        """
        key = (config.package, config.name)
        registry_entry = _TilesProcessorFactory.registry.get(key)

        if registry_entry is None:
            message = (
                'Invalid config! '
                f'The tiles processor {config.name} from {config.package} must be registered.'
            )
            raise AviaryUserError(message) from None

        tiles_processor_class, _ = registry_entry
        # noinspection PyUnresolvedReferences
        return tiles_processor_class.from_config(config=config.config)

    @staticmethod
    def register(
        tiles_processor_class: type[TilesProcessor],
        config_class: type[pydantic.BaseModel],
        package: str = _PACKAGE,
    ) -> None:
        """Registers a tiles processor.

        Parameters:
            tiles_processor_class: Tiles processor class
            config_class: Configuration class
            package: Package
        """
        key = (package, tiles_processor_class.__name__)
        _TilesProcessorFactory.registry[key] = (tiles_processor_class, config_class)


def register_tiles_processor(
    config_class: type[pydantic.BaseModel],
) -> Callable:
    """Registers a tiles processor.

    Parameters:
        config_class: Configuration class

    Returns:
        Decorator

    Raises:
        AviaryUserError: Invalid registration (the package name is equal to aviary)
    """
    def decorator(
        cls: type[TilesProcessor],
    ) -> type[TilesProcessor]:
        package = cls.__module__.split('.')[0]

        if package == _PACKAGE:
            message = (
                'Invalid registration! '
                f'The package name must be different from {_PACKAGE}.'
            )
            raise AviaryUserError(message)

        _TilesProcessorFactory.register(
            tiles_processor_class=cls,
            config_class=config_class,
            package=package,
        )
        return cls
    return decorator


class CopyProcessor:
    """Tiles processor that copies a channel

    Implements the `TilesProcessor` protocol.
    """

    def __init__(
        self,
        channel_name: ChannelName | str,
        new_channel_name: ChannelName | str | None = None,
    ) -> None:
        """
        Parameters:
            channel_name: Channel name
            new_channel_name: New channel name
        """
        self._channel_name = channel_name
        self._new_channel_name = new_channel_name

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
        tiles: Tiles,
    ) -> Tiles:
        """Copies the channel.

        Parameters:
            tiles: Tiles

        Returns:
            Tiles
        """
        return copy_processor(
            tiles=tiles,
            channel_name=self._channel_name,
            new_channel_name=self._new_channel_name,
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
          channel_name: 'my_channel'
          new_channel_name: 'my_new_channel'
        ```

    Attributes:
        channel_name: Channel name
        new_channel_name: New channel name -
            defaults to None
    """
    channel_name: ChannelName | str
    new_channel_name: ChannelName | str | None = None


_TilesProcessorFactory.register(
    tiles_processor_class=CopyProcessor,
    config_class=CopyProcessorConfig,
    package=_PACKAGE,
)


class NormalizeProcessor:
    """Tiles processor that normalizes a channel

    Notes:
        - Requires a raster channel

    Implements the `TilesProcessor` protocol.
    """

    def __init__(
        self,
        channel_name: ChannelName | str,
        min_value: float,
        max_value: float,
        new_channel_name: ChannelName | str | None = None,
        max_num_threads: int | None = None,
    ) -> None:
        """
        Parameters:
            channel_name: Channel name
            min_value: Minimum value
            max_value: Maximum value
            new_channel_name: New channel name
            max_num_threads: Maximum number of threads
        """
        self._channel_name = channel_name
        self._min_value = min_value
        self._max_value = max_value
        self._new_channel_name = new_channel_name
        self._max_num_threads = max_num_threads

    @classmethod
    def from_config(
        cls,
        config: NormalizeProcessorConfig,
    ) -> NormalizeProcessor:
        """Creates a normalize processor from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Normalize processor
        """
        config = config.model_dump()
        return cls(**config)

    def __call__(
        self,
        tiles: Tiles,
    ) -> Tiles:
        """Normalizes the channel.

        Parameters:
            tiles: Tiles

        Returns:
            Tiles
        """
        return normalize_processor(
            tiles=tiles,
            channel_name=self._channel_name,
            min_value=self._min_value,
            max_value=self._max_value,
            new_channel_name=self._new_channel_name,
            max_num_threads=self._max_num_threads,
        )


class NormalizeProcessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `NormalizeProcessor`

    Create the configuration from a config file:
        - Use null instead of None

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'NormalizeProcessor'
        config:
          channel_name: 'my_channel'
          min_value: 0.
          max_value: 255.
          new_channel_name: null
          max_num_threads: null
        ```

    Attributes:
        channel_name: Channel name
        min_value: Minimum value
        max_value: Maximum value
        new_channel_name: New channel name -
            defaults to None
        max_num_threads: Maximum number of threads -
            defaults to None
    """
    channel_name: ChannelName | str
    min_value: float
    max_value: float
    new_channel_name: ChannelName | str | None = None
    max_num_threads: int | None = None


_TilesProcessorFactory.register(
    tiles_processor_class=NormalizeProcessor,
    config_class=NormalizeProcessorConfig,
    package=_PACKAGE,
)


class ParallelCompositeProcessor:
    """Tiles processor that composes multiple tiles processors in parallel

    Notes:
        - The tiles processors are not called concurrently, but each one gets a copy of the tiles
            and the resulting tiles are combined
        - The tiles processors are composed horizontally, i.e., in parallel

    Implements the `TilesProcessor` protocol.
    """

    def __init__(
        self,
        tiles_processors: list[TilesProcessor],
    ) -> None:
        """
        Parameters:
            tiles_processors: Tiles processors
        """
        self._tiles_processors = tiles_processors

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
        tiles_processors = [
            _TilesProcessorFactory.create(config=tiles_processor_config)
            for tiles_processor_config in config.tiles_processor_configs
        ]
        return cls(
            tiles_processors=tiles_processors,
        )

    def __call__(
        self,
        tiles: Tiles,
    ) -> Tiles:
        """Processes the tiles with each tiles processor.

        Parameters:
            tiles: Tiles

        Returns:
            Tiles
        """
        return parallel_composite_processor(
            tiles=tiles,
            tiles_processors=self._tiles_processors,
        )


class ParallelCompositeProcessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `ParallelCompositeProcessor`

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'ParallelCompositeProcessor'
        config:
          tiles_processor_configs:
            - ...
            ...
        ```

    Attributes:
        tiles_processor_configs: Configurations of the tiles processors
    """
    tiles_processor_configs: list[TilesProcessorConfig]


_TilesProcessorFactory.register(
    tiles_processor_class=ParallelCompositeProcessor,
    config_class=ParallelCompositeProcessorConfig,
    package=_PACKAGE,
)


class RemoveBufferProcessor:
    """Tiles processor that removes the buffer of channels

    Implements the `TilesProcessor` protocol.
    """

    def __init__(
        self,
        channel_names:
            ChannelName | str |
            ChannelNameSet |
            bool |
            None = True,
    ) -> None:
        """
        Parameters:
            channel_names: Channel name, channel names, no channels (False or None), or all channels (True)
        """
        self._channel_names = channel_names

    @classmethod
    def from_config(
        cls,
        config: RemoveBufferProcessorConfig,
    ) -> RemoveBufferProcessor:
        """Creates a remove buffer processor from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Remove buffer processor
        """
        config = config.model_dump()
        return cls(**config)

    def __call__(
        self,
        tiles: Tiles,
    ) -> Tiles:
        """Removes the buffer of the channels.

        Parameters:
            tiles: Tiles

        Returns:
            Tiles
        """
        return remove_buffer_processor(
            tiles=tiles,
            channel_names=self._channel_names,
        )


class RemoveBufferProcessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `RemoveBufferProcessor`

    Create the configuration from a config file:
        - Use null instead of None
        - Use false or true instead of False or True

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'RemoveBufferProcessor'
        config:
          channel_names: true
        ```

    Attributes:
        channel_names: Channel name, channel names, no channels (False or None), or all channels (True) -
            defaults to True
    """
    channel_names: (
        ChannelName | str |
        ChannelNameSet |
        bool |
        None
    ) = True


_TilesProcessorFactory.register(
    tiles_processor_class=RemoveBufferProcessor,
    config_class=RemoveBufferProcessorConfig,
    package=_PACKAGE,
)


class RemoveProcessor:
    """Tiles processor that removes channels

    Implements the `TilesProcessor` protocol.
    """

    def __init__(
        self,
        channel_names:
            ChannelName | str |
            ChannelNameSet |
            bool |
            None = True,
    ) -> None:
        """
        Parameters:
            channel_names: Channel name, channel names, no channels (False or None), or all channels (True)
        """
        self._channel_names = channel_names

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
        tiles: Tiles,
    ) -> Tiles:
        """Removes the channels.

        Parameters:
            tiles: Tiles

        Returns:
            Tiles
        """
        return remove_processor(
            tiles=tiles,
            channel_names=self._channel_names,
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
          channel_names: true
        ```

    Attributes:
        channel_names: Channel name, channel names, no channels (False or None), or all channels (True) -
            defaults to True
    """
    channel_names: (
        ChannelName | str |
        ChannelNameSet |
        bool |
        None
    ) = True


_TilesProcessorFactory.register(
    tiles_processor_class=RemoveProcessor,
    config_class=RemoveProcessorConfig,
    package=_PACKAGE,
)


class SelectProcessor:
    """Tiles processor that selects channels

    Implements the `TilesProcessor` protocol.
    """

    def __init__(
        self,
        channel_names:
            ChannelName | str |
            ChannelNameSet |
            bool |
            None = True,
    ) -> None:
        """
        Parameters:
            channel_names: Channel name, channel names, no channels (False or None), or all channels (True)
        """
        self._channel_names = channel_names

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
        tiles: Tiles,
    ) -> Tiles:
        """Selects the channels.

        Parameters:
            tiles: Tiles

        Returns:
            Tiles
        """
        return select_processor(
            tiles=tiles,
            channel_names=self._channel_names,
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
          channel_names: true
        ```

    Attributes:
        channel_names: Channel name, channel names, no channels (False or None), or all channels (True) -
            defaults to True
    """
    channel_names: (
        ChannelName | str |
        ChannelNameSet |
        bool |
        None
    ) = True


_TilesProcessorFactory.register(
    tiles_processor_class=SelectProcessor,
    config_class=SelectProcessorConfig,
    package=_PACKAGE,
)


class SequentialCompositeProcessor:
    """Tiles processor that composes multiple tiles processors in sequence

    Notes:
        - The tiles processors are composed vertically, i.e., in sequence

    Implements the `TilesProcessor` protocol.
    """

    def __init__(
        self,
        tiles_processors: list[TilesProcessor],
    ) -> None:
        """
        Parameters:
            tiles_processors: Tiles processors
        """
        self._tiles_processors = tiles_processors

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
        tiles_processors = [
            _TilesProcessorFactory.create(config=tiles_processor_config)
            for tiles_processor_config in config.tiles_processor_configs
        ]
        return cls(
            tiles_processors=tiles_processors,
        )

    def __call__(
        self,
        tiles: Tiles,
    ) -> Tiles:
        """Processes the tiles with each tiles processor.

        Parameters:
            tiles: Tiles

        Returns:
            Tiles
        """
        return sequential_composite_processor(
            tiles=tiles,
            tiles_processors=self._tiles_processors,
        )


class SequentialCompositeProcessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `SequentialCompositeProcessor`

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'SequentialCompositeProcessor'
        config:
          tiles_processor_configs:
            - ...
            ...
        ```

    Attributes:
        tiles_processor_configs: Configurations of the tiles processors
    """
    tiles_processor_configs: list[TilesProcessorConfig]


_TilesProcessorFactory.register(
    tiles_processor_class=SequentialCompositeProcessor,
    config_class=SequentialCompositeProcessorConfig,
    package=_PACKAGE,
)


class StandardizeProcessor:
    """Tiles processor that standardizes a channel

    Notes:
        - Requires a raster channel

    Implements the `TilesProcessor` protocol.
    """

    def __init__(
        self,
        channel_name: ChannelName | str,
        mean_value: float,
        std_value: float,
        new_channel_name: ChannelName | str | None = None,
        max_num_threads: int | None = None,
    ) -> None:
        """
        Parameters:
            channel_name: Channel name
            mean_value: Mean value
            std_value: Standard deviation value
            new_channel_name: New channel name
            max_num_threads: Maximum number of threads
        """
        self._channel_name = channel_name
        self._mean_value = mean_value
        self._std_value = std_value
        self._new_channel_name = new_channel_name
        self._max_num_threads = max_num_threads

    @classmethod
    def from_config(
        cls,
        config: StandardizeProcessorConfig,
    ) -> StandardizeProcessor:
        """Creates a standardize processor from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Standardize processor
        """
        config = config.model_dump()
        return cls(**config)

    def __call__(
        self,
        tiles: Tiles,
    ) -> Tiles:
        """Standardizes the channel.

        Parameters:
            tiles: Tiles

        Returns:
            Tiles
        """
        return standardize_processor(
            tiles=tiles,
            channel_name=self._channel_name,
            mean_value=self._mean_value,
            std_value=self._std_value,
            new_channel_name=self._new_channel_name,
            max_num_threads=self._max_num_threads,
        )


class StandardizeProcessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `StandardizeProcessor`

    Create the configuration from a config file:
        - Use null instead of None

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'StandardizeProcessor'
        config:
          channel_name: 'my_channel'
          mean_value: .5
          std_value: .25
          new_channel_name: null
          max_num_threads: null
        ```

    Attributes:
        channel_name: Channel name
        mean_value: Mean value
        std_value: Standard deviation value
        new_channel_name: New channel name -
            defaults to None
        max_num_threads: Maximum number of threads -
            defaults to None
    """
    channel_name: ChannelName | str
    mean_value: float
    std_value: float
    new_channel_name: ChannelName | str | None = None
    max_num_threads: int | None = None


_TilesProcessorFactory.register(
    tiles_processor_class=StandardizeProcessor,
    config_class=StandardizeProcessorConfig,
    package=_PACKAGE,
)


class VectorizeProcessor:
    """Tiles processor that vectorizes a channel

    Notes:
        - Requires a raster channel

    Implements the `TilesProcessor` protocol.
    """

    def __init__(
        self,
        channel_name: ChannelName | str,
        ignore_background_class: bool = True,
        new_channel_name: ChannelName | str | None = None,
        max_num_threads: int | None = None,
    ) -> None:
        """
        Parameters:
            channel_name: Channel name
            ignore_background_class: If True, the background class (value 0) is not vectorized
            new_channel_name: New channel name
            max_num_threads: Maximum number of threads
        """
        self._channel_name = channel_name
        self._ignore_background_class = ignore_background_class
        self._new_channel_name = new_channel_name
        self._max_num_threads = max_num_threads

    @classmethod
    def from_config(
        cls,
        config: VectorizeProcessorConfig,
    ) -> VectorizeProcessor:
        """Creates a vectorize processor from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Vectorize processor
        """
        config = config.model_dump()
        return cls(**config)

    def __call__(
        self,
        tiles: Tiles,
    ) -> Tiles:
        """Vectorizes the channel.

        Parameters:
            tiles: Tiles

        Returns:
            Tiles
        """
        return vectorize_processor(
            tiles=tiles,
            channel_name=self._channel_name,
            ignore_background_class=self._ignore_background_class,
            new_channel_name=self._new_channel_name,
            max_num_threads=self._max_num_threads,
        )


class VectorizeProcessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `VectorizeProcessor`

    Create the configuration from a config file:
        - Use null instead of None
        - Use false or true instead of False or True

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'VectorizeProcessor'
        config:
          channel_name: 'my_channel'
          ignore_background_class: true
          new_channel_name: null
          max_num_threads: null
        ```

    Attributes:
        channel_name: Channel name
        ignore_background_class: If True, the background class (value 0) is not vectorized -
            defaults to True
        new_channel_name: New channel name -
            defaults to None
        max_num_threads: Maximum number of threads -
            defaults to None
    """
    channel_name: ChannelName | str
    ignore_background_class: bool = True
    new_channel_name: ChannelName | str | None = None
    max_num_threads: int | None = None


_TilesProcessorFactory.register(
    tiles_processor_class=VectorizeProcessor,
    config_class=VectorizeProcessorConfig,
    package=_PACKAGE,
)

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Protocol,
)

if TYPE_CHECKING:
    from collections.abc import Callable

import pydantic

# noinspection PyProtectedMember
from aviary._functional.inference.tiles_processor import (
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
from aviary.core.type_aliases import (
    ChannelKey,
    ChannelKeySet,
    ChannelNameKeySet,
    ChannelNameSet,
)

if TYPE_CHECKING:
    from aviary.core.tiles import Tiles


class TilesProcessor(Protocol):
    """Protocol for tiles processors

    Tiles processors are callables that process tiles.

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

    Attributes:
        name: Name
        config: Configuration
    """
    name: str
    config: (
        CopyProcessorConfig |
        NormalizeProcessorConfig |
        ParallelCompositeProcessorConfig |
        RemoveBufferProcessorConfig |
        RemoveProcessorConfig |
        SelectProcessorConfig |
        SequentialCompositeProcessorConfig |
        StandardizeProcessorConfig |
        VectorizeProcessorConfig |
        pydantic.BaseModel
    )


_registry: dict[str, tuple[type[TilesProcessor], type[pydantic.BaseModel]]] = {}


class TilesProcessorFactory:
    """Factory for tiles processors"""

    @staticmethod
    def create(
        config: TilesProcessorConfig,
    ) -> TilesProcessor:
        """Creates a tiles processor from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Tiles processor
        """
        try:
            tiles_processor_class = globals()[config.name]
            return tiles_processor_class.from_config(config=config.config)
        except KeyError:
            registry_entry = _registry.get(config.name)

            if registry_entry is None:
                message = (
                    'Invalid config! '
                    f'The tiles processor {config.name} is not registered.'
                )
                raise AviaryUserError(message) from None

            tiles_processor_class, _ = registry_entry
            # noinspection PyUnresolvedReferences
            return tiles_processor_class.from_config(config=config.config)

    @staticmethod
    def register(
        tiles_processor_class: type[TilesProcessor],
        config_class: type[pydantic.BaseModel],
    ) -> None:
        """Registers a tiles processor.

        Parameters:
            tiles_processor_class: Tiles processor class
            config_class: Configuration class
        """
        _registry[tiles_processor_class.__name__] = (tiles_processor_class, config_class)


def register_tiles_processor(config_class: type[pydantic.BaseModel]) -> Callable:
    """Registers a tiles processor.

    Parameters:
        config_class: Configuration class

    Returns:
        Decorator
    """
    def decorator(cls: type[TilesProcessor]) -> type[TilesProcessor]:
        TilesProcessorFactory.register(
            tiles_processor_class=cls,
            config_class=config_class,
        )
        return cls
    return decorator


class CopyProcessor:
    """Tiles processor that copies a channel

    Notes:
        - Copying a channel by its name assumes the time step is None

    Implements the `TilesProcessor` protocol.
    """

    def __init__(
        self,
        channel_key: ChannelName | str | ChannelKey,
        new_channel_key: ChannelName | str | ChannelKey | None = None,
    ) -> None:
        """
        Parameters:
            channel_key: Channel name or channel name and time step combination
            new_channel_key: New channel name or channel name and time step combination
        """
        self._channel_key = channel_key
        self._new_channel_key = new_channel_key

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
            channel_key=self._channel_key,
            new_channel_key=self._new_channel_key,
        )


class CopyProcessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `CopyProcessor`

    Create the configuration from a config file:
        - Use null instead of None

    Attributes:
        channel_key: Channel name or channel name and time step combination
        new_channel_key: New channel name or channel name and time step combination -
            defaults to None
    """
    channel_key: ChannelName | str | ChannelKey
    new_channel_key: ChannelName | str | ChannelKey | None = None


class NormalizeProcessor:
    """Tiles processor that normalizes a channel

    Notes:
        - Normalizing a channel by its name assumes the time step is None
        - Requires a raster channel

    Implements the `TilesProcessor` protocol.
    """

    def __init__(
        self,
        channel_key: ChannelName | str | ChannelKey,
        min_value: float,
        max_value: float,
        new_channel_key: ChannelName | str | ChannelKey | None = None,
    ) -> None:
        """
        Parameters:
            channel_key: Channel name or channel name and time step combination
            min_value: Minimum value
            max_value: Maximum value
            new_channel_key: New channel name or channel name and time step combination
        """
        self._channel_key = channel_key
        self._min_value = min_value
        self._max_value = max_value
        self._new_channel_key = new_channel_key

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
            channel_key=self._channel_key,
            min_value=self._min_value,
            max_value=self._max_value,
            new_channel_key=self._new_channel_key,
        )


class NormalizeProcessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `NormalizeProcessor`

    Create the configuration from a config file:
        - Use null instead of None

    Attributes:
        channel_key: Channel name or channel name and time step combination
        min_value: Minimum value
        max_value: Maximum value
        new_channel_key: New channel name or channel name and time step combination -
            defaults to None
    """
    channel_key: ChannelName | str | ChannelKey
    min_value: float
    max_value: float
    new_channel_key: ChannelName | str | ChannelKey | None = None


class ParallelCompositeProcessor:
    """Tiles processor that composes multiple tiles processors in parallel

    Notes:
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
            TilesProcessorFactory.create(config=tiles_processor_config)
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

    Attributes:
        tiles_processor_configs: Configurations of the tiles processors
    """
    tiles_processor_configs: list[TilesProcessorConfig]


class RemoveBufferProcessor:
    """Tiles processor that removes the buffer of channels

    Notes:
        - Removing the buffer of a channel by its name assumes the time step is None

    Implements the `TilesProcessor` protocol.
    """

    def __init__(
        self,
        channel_keys:
            ChannelName | str |
            ChannelKey |
            ChannelNameSet | ChannelKeySet | ChannelNameKeySet |
            bool |
            None = True,
    ) -> None:
        """
        Parameters:
            channel_keys: Channel name, channel name and time step combination, channel names,
                channel name and time step combinations, no channels (False or None), or all channels (True)
        """
        self._channel_keys = channel_keys

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
            channel_keys=self._channel_keys,
        )


class RemoveBufferProcessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `RemoveBufferProcessor`

    Create the configuration from a config file:
        - Use null instead of None

    Attributes:
        channel_keys: Channel name, channel name and time step combination, channel names,
            channel name and time step combinations, no channels (False or None), or all channels (True) -
            defaults to True
    """
    channel_keys: (
        ChannelName | str |
        ChannelKey |
        ChannelNameSet | ChannelKeySet | ChannelNameKeySet |
        bool |
        None
    ) = True


class RemoveProcessor:
    """Tiles processor that removes channels

    Notes:
        - Removing a channel by its name assumes the time step is None

    Implements the `TilesProcessor` protocol.
    """

    def __init__(
        self,
        channel_keys:
            ChannelName | str |
            ChannelKey |
            ChannelNameSet | ChannelKeySet | ChannelNameKeySet |
            bool |
            None = True,
    ) -> None:
        """
        Parameters:
            channel_keys: Channel name, channel name and time step combination, channel names,
                channel name and time step combinations, no channels (False or None), or all channels (True)
        """
        self._channel_keys = channel_keys

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
            channel_keys=self._channel_keys,
        )


class RemoveProcessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `RemoveProcessor`

    Create the configuration from a config file:
        - Use null instead of None

    Attributes:
        channel_keys: Channel name, channel name and time step combination, channel names,
            channel name and time step combinations, no channels (False or None), or all channels (True) -
            defaults to True
    """
    channel_keys: (
        ChannelName | str |
        ChannelKey |
        ChannelNameSet | ChannelKeySet | ChannelNameKeySet |
        bool |
        None
    ) = True


class SelectProcessor:
    """Tiles processor that selects channels

    Notes:
        - Selecting a channel by its name assumes the time step is None

    Implements the `TilesProcessor` protocol.
    """

    def __init__(
        self,
        channel_keys:
            ChannelName | str |
            ChannelKey |
            ChannelNameSet | ChannelKeySet | ChannelNameKeySet |
            bool |
            None = True,
    ) -> None:
        """
        Parameters:
            channel_keys: Channel name, channel name and time step combination, channel names,
                channel name and time step combinations, no channels (False or None), or all channels (True)
        """
        self._channel_keys = channel_keys

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
            channel_keys=self._channel_keys,
        )


class SelectProcessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `SelectProcessor`

    Create the configuration from a config file:
        - Use null instead of None

    Attributes:
        channel_keys: Channel name, channel name and time step combination, channel names,
            channel name and time step combinations, no channels (False or None), or all channels (True) -
            defaults to True
    """
    channel_keys: (
        ChannelName | str |
        ChannelKey |
        ChannelNameSet | ChannelKeySet | ChannelNameKeySet |
        bool |
        None
    ) = True


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
            TilesProcessorFactory.create(config=tiles_processor_config)
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

    Attributes:
        tiles_processor_configs: Configurations of the tiles processors
    """
    tiles_processor_configs: list[TilesProcessorConfig]


class StandardizeProcessor:
    """Tiles processor that standardizes a channel

    Notes:
        - Standardizing a channel by its name assumes the time step is None
        - Requires a raster channel

    Implements the `TilesProcessor` protocol.
    """

    def __init__(
        self,
        channel_key: ChannelName | str | ChannelKey,
        mean_value: float,
        std_value: float,
        new_channel_key: ChannelName | str | ChannelKey | None = None,
    ) -> None:
        """
        Parameters:
            channel_key: Channel name or channel name and time step combination
            mean_value: Mean value
            std_value: Standard deviation value
            new_channel_key: New channel name or channel name and time step combination
        """
        self._channel_key = channel_key
        self._mean_value = mean_value
        self._std_value = std_value
        self._new_channel_key = new_channel_key

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
            channel_key=self._channel_key,
            mean_value=self._mean_value,
            std_value=self._std_value,
            new_channel_key=self._new_channel_key,
        )


class StandardizeProcessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `StandardizeProcessor`

    Create the configuration from a config file:
        - Use null instead of None

    Attributes:
        channel_key: Channel name or channel name and time step combination
        mean_value: Mean value
        std_value: Standard deviation value
        new_channel_key: New channel name or channel name and time step combination -
            defaults to None
    """
    channel_key: ChannelName | str | ChannelKey
    mean_value: float
    std_value: float
    new_channel_key: ChannelName | str | ChannelKey | None = None


class VectorizeProcessor:
    """Tiles processor that vectorizes a channel

    Notes:
        - Vectorizing a channel by its name assumes the time step is None
        - Requires a raster channel

    Implements the `TilesProcessor` protocol.
    """

    def __init__(
        self,
        channel_key: ChannelName | str | ChannelKey,
        ignore_background_class: bool = True,
        new_channel_key: ChannelName | str | ChannelKey | None = None,
        num_workers: int = 1,
    ) -> None:
        """
        Parameters:
            channel_key: Channel name or channel name and time step combination
            ignore_background_class: If True, the background class (value 0) is not vectorized
            new_channel_key: New channel name or channel name and time step combination
            num_workers: Number of workers
        """
        self._channel_key = channel_key
        self._ignore_background_class = ignore_background_class
        self._new_channel_key = new_channel_key
        self._num_workers = num_workers

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
            channel_key=self._channel_key,
            ignore_background_class=self._ignore_background_class,
            new_channel_key=self._new_channel_key,
            num_workers=self._num_workers,
        )


class VectorizeProcessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `VectorizeProcessor`

    Create the configuration from a config file:
        - Use null instead of None

    Attributes:
        channel_key: Channel name or channel name and time step combination
        ignore_background_class: If True, the background class (value 0) is not vectorized -
            defaults to True
        new_channel_key: New channel name or channel name and time step combination -
            defaults to None
        num_workers: Number of workers -
            defaults to 1
    """
    channel_key: ChannelName | str | ChannelKey
    ignore_background_class: bool = True
    new_channel_key: ChannelName | str | ChannelKey | None = None
    num_workers: int = 1

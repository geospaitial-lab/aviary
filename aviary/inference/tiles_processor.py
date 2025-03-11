from __future__ import annotations

from types import EllipsisType
from typing import (
    TYPE_CHECKING,
    Protocol,
)

import pydantic

# noinspection PyProtectedMember
from aviary._functional.inference.tiles_processor import (
    composite_processor,
    copy_processor,
    normalize_processor,
    remove_buffer_processor,
    remove_processor,
    select_processor,
    standardize_processor,
    vectorize_processor,
)
from aviary.core.enums import ChannelName
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
        - `CompositeProcessor`: Composes multiple tiles processors
        - `CopyProcessor`: Copies a channel
        - `NormalizeProcessor`: Normalizes a channel
        - `RemoveBufferProcessor`: Removes the buffer of channels
        - `RemoveProcessor`: Removes channels
        - `SelectProcessor`: Selects channels
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
        CompositeProcessorConfig |
        CopyProcessorConfig |
        NormalizeProcessorConfig |
        RemoveBufferProcessorConfig |
        RemoveProcessorConfig |
        SelectProcessorConfig |
        StandardizeProcessorConfig |
        VectorizeProcessorConfig
    )


class CompositeProcessor:
    """Tiles processor that composes multiple tiles processors

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
        config: CompositeProcessorConfig,
    ) -> CompositeProcessor:
        """Creates a composite processor from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Composite processor
        """
        tiles_processors = []

        for tiles_processor_config in config.tiles_processor_configs:
            tiles_processor_class = globals()[tiles_processor_config.name]
            tiles_processor = tiles_processor_class.from_config(config=tiles_processor_config.config)
            tiles_processors.append(tiles_processor)

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
        return composite_processor(
            tiles=tiles,
            tiles_processors=self._tiles_processors,
        )


class CompositeProcessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `CompositeProcessor`

    Attributes:
        tiles_processor_configs: Configurations of the tiles processors
    """
    tiles_processor_configs: list[TilesProcessorConfig]


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
            EllipsisType |
            None = Ellipsis,
    ) -> None:
        """
        Parameters:
            channel_keys: Channel name, channel name and time step combination, channel names,
                channel name and time step combinations, or all channels (Ellipsis)
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
        - Use '...' instead of Ellipsis

    Attributes:
        channel_keys: Channel name, channel name and time step combination, channel names,
            channel name and time step combinations, or all channels (Ellipsis) -
            defaults to Ellipsis
    """
    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
    )

    channel_keys: (
        ChannelName | str |
        ChannelKey |
        ChannelNameSet | ChannelKeySet | ChannelNameKeySet |
        EllipsisType |
        None
    ) = Ellipsis


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
            EllipsisType |
            None = Ellipsis,
    ) -> None:
        """
        Parameters:
            channel_keys: Channel name, channel name and time step combination, channel names,
                channel name and time step combinations, or all channels (Ellipsis)
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
        - Use '...' instead of Ellipsis

    Attributes:
        channel_keys: Channel name, channel name and time step combination, channel names,
            channel name and time step combinations, or all channels (Ellipsis) -
            defaults to Ellipsis
    """
    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
    )

    channel_keys: (
        ChannelName | str |
        ChannelKey |
        ChannelNameSet | ChannelKeySet | ChannelNameKeySet |
        EllipsisType |
        None
    ) = Ellipsis


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
            EllipsisType |
            None = Ellipsis,
    ) -> None:
        """
        Parameters:
            channel_keys: Channel name, channel name and time step combination, channel names,
                channel name and time step combinations, or all channels (Ellipsis)
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
        - Use '...' instead of Ellipsis

    Attributes:
        channel_keys: Channel name, channel name and time step combination, channel names,
            channel name and time step combinations, or all channels (Ellipsis) -
            defaults to Ellipsis
    """
    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
    )

    channel_keys: (
        ChannelName | str |
        ChannelKey |
        ChannelNameSet | ChannelKeySet | ChannelNameKeySet |
        EllipsisType |
        None
    ) = Ellipsis


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

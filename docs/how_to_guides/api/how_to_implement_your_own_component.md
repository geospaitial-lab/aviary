## How to implement your own component

<span class="aviary-skill-level">Skill level: Intermediate</span>

!!! abstract "TL;DR"
    Custom components just need to implement their respective protocols.
    Optionally, a config class and a `from_config` class method can be implemented
    to create an instance from a configuration.

aviary’s components are designed to be modular and extensible.
This means that you can easily implement your own components and use them just like the built-in ones.

There are the following types of components in aviary:

- [`CoordinatesFilter`][CoordinatesFilter]
- [`TileFetcher`][TileFetcher]
- [`TilesProcessor`][TilesProcessor]

These are protocols that define the methods a component must have.
Implementing them is straightforward as they only require you to implement the `__call__` method.

  [CoordinatesFilter]: ../../api_reference/utils/coordinates_filter/coordinates_filter.md#aviary.utils.CoordinatesFilter
  [TileFetcher]: ../../api_reference/tile/tile_fetcher/tile_fetcher.md#aviary.tile.TileFetcher
  [TilesProcessor]: ../../api_reference/tile/tiles_processor/tiles_processor.md#aviary.tile.TilesProcessor

### Example

#### Implementing a custom tiles processor

Let’s implement our own tiles processor called `MyTilesProcessor`.

First, we need to have a look at the [`TilesProcessor`][TilesProcessor] protocol.
A tiles processor is a callable that takes a [`Tiles`][Tiles] object, processes it, and returns it.

So, we need to implement the `__call__` method in our class.
We can also implement the `__init__` method to initialize our tiles processor.
This is useful if you need to pass any parameters to the tiles processor.

``` python title="my_tiles_processor.py"
import aviary


class MyTilesProcessor:

    def __init__(self) -> None:
        ...  # Initialize your tiles processor

    def __call__(
        self,
        tiles: aviary.Tiles,
    ) -> aviary.Tiles:
        ...  # Process the tiles and return them
```

It’s as simple as that! Now you can use `MyTilesProcessor` like any other tiles processor in aviary.

#### Implementing a config class and a `from_config` class method

If we want to create an instance of our tiles processor from a configuration,
we need to implement a config class and a `from_config` class method.

Let’s implement the config class called `MyTilesProcessorConfig` and the `from_config` class method.
The config class is a Pydantic model that defines the configuration for our tiles processor.
This may seem complicated, but it simply mimics the parameters of the `__init__` method.
When we pass the configuration to the `from_config` class method, it should return an instance of our tiles processor.

``` python title="my_tiles_processor.py" hl_lines="1 4 7-8 15-20"
from __future__ import annotations  # (1)

import aviary
import pydantic


class MyTilesProcessorConfig(pydantic.BaseModel):
    ...  # Define the configuration for your tiles processor

class MyTilesProcessor:

    def __init__(self) -> None:
        ...  # Initialize your tiles processor

    @classmethod
    def from_config(
        cls,
        config: MyTilesProcessorConfig,
    ) -> MyTilesProcessor:
        ... # Create the tiles processor from the configuration

    def __call__(
        self,
        tiles: aviary.Tiles,
    ) -> aviary.Tiles:
        ...  # Process the tiles and return them
```

1.  This import is required for correct type hinting in the `from_config` class method.

Now you can create an instance of `MyTilesProcessor` from a configuration.

  [TilesProcessor]: ../../api_reference/tile/tiles_processor/tiles_processor.md#aviary.tile.TilesProcessor
  [Tiles]: ../../api_reference/core/tiles.md#aviary.Tiles

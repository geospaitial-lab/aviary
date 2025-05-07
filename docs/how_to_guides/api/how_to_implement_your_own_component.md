## How to implement your own component

<span class="aviary-skill-level">Skill level: Intermediate</span>

!!! abstract "TL;DR"
    Custom components just need to implement their respective protocol.

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

#### Implement a custom tiles processor

Let’s implement our own tiles processor called `MyTilesProcessor`.

First, we need to have a look at the [`TilesProcessor`][TilesProcessor] protocol.
A tiles processor is a callable that takes a [`Tiles`][Tiles] object, processes it, and returns it.

So, we need to implement the `__call__` method in our class.
We can also implement the `__init__` method to initialize our tiles processor.
This is useful if you need to pass any parameters to the tiles processor.

``` python title="my_tiles_processor.py"
import aviary


class MyTilesProcessor:

    def __init__(
        self,
        param_1: int,
        param_2: str,
    ) -> None:
        self._param_1 = param_1
        self._param_2 = param_2

    def __call__(
        self,
        tiles: aviary.Tiles,
    ) -> aviary.Tiles:
        # Process the tiles here
        return tiles
```

It’s as simple as that!
Now you can use `MyTilesProcessor` like any other tiles processor in aviary.

  [TilesProcessor]: ../../api_reference/tile/tiles_processor/tiles_processor.md#aviary.tile.TilesProcessor
  [Tiles]: ../../api_reference/core/tiles.md#aviary.Tiles

---

## Next step

Do you want to use custom components in the CLI?<br>
Have a look at the [How to register your own component] guide.

  [How to register your own component]: ../cli/how_to_register_your_own_component.md

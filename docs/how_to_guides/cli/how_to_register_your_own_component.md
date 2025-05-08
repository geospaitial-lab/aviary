## How to register your own component

<span class="aviary-skill-level">Skill level: Intermediate</span>

!!! abstract "TL;DR"
    Custom components need to implement their respective protocol, a config class, and a `from_config` class method.
    They’re registered as plugins using their respective registration decorator.

Make sure to read the [How to implement your own component] guide first.

After implementing your own component, you can register it as a plugin with its registration decorator.
This allows aviary to discover your component at runtime.

[How to implement your own component]: ../../how_to_guides/api/how_to_implement_your_own_component.md

### Example

#### Implement a config class and a `from_config` class method

If we want to create an instance of our tiles processor from a configuration,
we need to implement a config class and a `from_config` class method.

Let’s implement the config class called `MyTilesProcessorConfig` and the `from_config` class method.
The config class is a Pydantic model that defines the configuration for our tiles processor.
This may seem complicated, but in most cases it simply mimics the parameters of the `__init__` method.
When we pass the configuration to the `from_config` class method, it should return an instance of our tiles processor.

``` python title="my_tiles_processor.py" hl_lines="1 4 7-9 21-27"
from __future__ import annotations  # (1)

import aviary
import pydantic


class MyTilesProcessorConfig(pydantic.BaseModel):
    param_1: int
    param_2: str

class MyTilesProcessor:

    def __init__(
        self,
        param_1: int,
        param_2: str,
    ) -> None:
        self._param_1 = param_1
        self._param_2 = param_2

    @classmethod
    def from_config(
        cls,
        config: MyTilesProcessorConfig,
    ) -> MyTilesProcessor:
        config = config.model_dump()
        return cls(**config)

    def __call__(
        self,
        tiles: aviary.Tiles,
    ) -> aviary.Tiles:
        # Process the tiles here
        return tiles
```

1.  This import is required for correct type hinting of the `from_config` class method’s return type.

Now you can create an instance of `MyTilesProcessor` from a configuration.

---

#### Register a custom tiles processor

All we need to do is to register our own tiles processor as a plugin using the
[`register_tiles_processor`][register_tiles_processor] decorator.

``` python title="my_tiles_processor.py" hl_lines="5 12"
from __future__ import annotations  # (1)

import aviary
import pydantic
from aviary.tile import register_tiles_processor


class MyTilesProcessorConfig(pydantic.BaseModel):
    param_1: int
    param_2: str

@register_tiles_processor(config_class=MyTilesProcessorConfig)
class MyTilesProcessor:

    def __init__(
        self,
        param_1: int,
        param_2: str,
    ) -> None:
        self._param_1 = param_1
        self._param_2 = param_2

    @classmethod
    def from_config(
        cls,
        config: MyTilesProcessorConfig,
    ) -> MyTilesProcessor:
        config = config.model_dump()
        return cls(**config)

    def __call__(
        self,
        tiles: aviary.Tiles,
    ) -> aviary.Tiles:
        # Process the tiles here
        return tiles
```

1.  This import is required for correct type hinting of the `from_config` class method’s return type.

We have to specify the path to the plugins directory containing `my_tiles_processor.py`
in the config file, so that aviary knows where to look for the custom components.

``` yaml title="config.yaml"
plugins_dir_path: /path/to/our/plugins_dir

# Configure the pipeline here
```

It’s as simple as that!
Now you can use `MyTilesProcessor` like any other tiles processor in aviary.

  [register_tiles_processor]: ../../api_reference/tile/tiles_processor/tiles_processor.md#aviary.tile.register_tiles_processor

---

#### Verify the registration of a custom tiles processor

To verify that our own tiles processor was registered successfully,
we can use the [`aviary plugins`][aviary plugins] command.

```
aviary plugins --plugins-dir-path /path/to/our/plugins_dir
```

This shows the registered plugins.

  [aviary plugins]: ../../cli_reference/aviary_plugins.md

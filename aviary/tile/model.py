from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pydantic

from aviary.core.channel import RasterChannel
from aviary.core.enums import ChannelName
from aviary.core.type_aliases import (
    ChannelKey,
    _coerce_channel_key,
)
from aviary.tile.tiles_processor import _TilesProcessorFactory

if TYPE_CHECKING:
    from aviary.core.tiles import Tiles

_PACKAGE = 'aviary'


class Adois:
    """Tiles processor that uses the adois model to detect and classify impervious surfaces.

    adois is a segmentation model that is trained to detect and classify impervious surfaces
    from digital orthophotos.
    It differentiates between non-impervious surfaces (e.g., vegetation, soil or water), buildings and
    impervious surfaces (e.g., pavements, roads, sidewalks, driveways, parking lots or industrial areas).
    It is recommended to use the model with leaf-off orthophotos (i.e., without foliage on trees or shrubs),
    so canopies do not cover buildings or impervious surfaces.

    Notes:
        - Accessing a channel by its name assumes the time step is None

    Model input channels:
        - `ChannelName.R`: Red channel, raster channel, ground sampling distance of 0.2 meters,
            normalized values in range [0, 1]
        - `ChannelName.G`: Green channel, raster channel, ground sampling distance of 0.2 meters,
            normalized values in range [0, 1]
        - `ChannelName.B`: Blue channel, raster channel, ground sampling distance of 0.2 meters,
            normalized values in range [0, 1]
        - `ChannelName.NIR`: Near-infrared channel, raster channel, ground sampling distance of 0.2 meters,
            normalized values in range [0, 1]

    Model output channels:
        - 'adois': Impervious surfaces channel, raster channel, ground sampling distance of 0.2 meters,
            the classes are non-impervious surfaces (value 0), buildings (value 1), and impervious surfaces (value 2)

    Additional dependencies:
        adois requires `huggingface_hub` and `onnxruntime` as additional dependencies.

    Implements the `TilesProcessor` protocol.
    """
    _HF_HUB_MODEL_PATH = 'models/adois_v0_0.onnx'
    _HF_HUB_REPO = 'geospaitial-lab/adois'

    def __init__(
        self,
        r_channel_key: ChannelName | str | ChannelKey = ChannelName.R,
        g_channel_key: ChannelName | str | ChannelKey = ChannelName.G,
        b_channel_key: ChannelName | str | ChannelKey = ChannelName.B,
        nir_channel_key: ChannelName | str | ChannelKey = ChannelName.NIR,
        out_channel_key: ChannelName | str | ChannelKey = 'adois',
        cache_dir_path: Path = Path('cache'),
        remove_channels: bool = True,
    ) -> None:
        """
        Parameters:
            r_channel_key: Channel name or channel name and time step combination of the red channel
            g_channel_key: Channel name or channel name and time step combination of the green channel
            b_channel_key: Channel name or channel name and time step combination of the blue channel
            nir_channel_key: Channel name or channel name and time step combination of the near-infrared channel
            out_channel_key: Channel name or channel name and time step combination of the output channel
            cache_dir_path: Path to the cache directory of the model
            remove_channels: If True, the channels are removed
        """
        try:
            import onnxruntime as ort
            from huggingface_hub import hf_hub_download
        except ImportError as error:
            message = (
                'Missing dependency! '
                'To use adois, you need to install huggingface_hub and onnxruntime.'
            )
            raise ImportError(message) from error

        self._r_channel_key = r_channel_key
        self._g_channel_key = g_channel_key
        self._b_channel_key = b_channel_key
        self._nir_channel_key = nir_channel_key
        self._channel_keys = [
            self._r_channel_key,
            self._g_channel_key,
            self._b_channel_key,
            self._nir_channel_key,
        ]
        self._out_channel_key = out_channel_key
        self._cache_dir_path = cache_dir_path
        self._remove_channels = remove_channels

        self._model_path = hf_hub_download(
            repo_id=self._HF_HUB_REPO,
            filename=self._HF_HUB_MODEL_PATH,
            local_dir=self._cache_dir_path,
        )
        self._model = ort.InferenceSession(self._model_path)
        self._model_input_name = self._model.get_inputs()[0].name
        self._model_output_name = self._model.get_outputs()[0].name

    @classmethod
    def from_config(
        cls,
        config: AdoisConfig,
    ) -> Adois:
        """Creates the adois model from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Adois
        """
        config = config.model_dump()
        return cls(**config)

    def __call__(
        self,
        tiles: Tiles,
    ) -> Tiles:
        """Runs the adois model.

        Parameters:
            tiles: Tiles

        Returns:
            Tiles
        """
        inputs = tiles.to_composite_raster(channel_keys=self._channel_keys)

        preds = self._model.run(
            output_names=[self._model_output_name],
            input_feed={self._model_input_name: inputs},
        )

        preds = np.array(preds)
        preds = np.squeeze(preds, axis=0)
        preds = np.argmax(preds, axis=-1)
        preds = preds.astype(np.uint8)

        data = list(preds)
        out_channel_key = _coerce_channel_key(channel_key=self._out_channel_key)
        name, time_step = out_channel_key
        buffer_size = tiles[self._channel_keys[0]].buffer_size
        preds_channel = RasterChannel(
            data=data,
            name=name,
            buffer_size=buffer_size,
            time_step=time_step,
            copy=False,
        )

        tiles = tiles.append(
            channels=preds_channel,
            inplace=True,
        )

        if self._remove_channels:
            channel_keys = set(self._channel_keys)
            tiles = tiles.remove(
                channel_keys=channel_keys,
                inplace=True,
            )

        return tiles


class AdoisConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `Adois`

    Create the configuration from a config file:
        - Use null instead of None
        - Use false or true instead of False or True

    Example:
        ``` yaml title="config.yaml"
        r_channel_key: 'r'
        g_channel_key: 'g'
        b_channel_key: 'b'
        nir_channel_key: 'nir'
        out_channel_key: 'adois'
        cache_dir_path: 'cache'
        remove_channels: true
        ```

    Attributes:
        r_channel_key: Channel name or channel name and time step combination of the red channel -
            defaults to `ChannelName.R`
        g_channel_key: Channel name or channel name and time step combination of the green channel -
            defaults to `ChannelName.G`
        b_channel_key: Channel name or channel name and time step combination of the blue channel -
            defaults to `ChannelName.B`
        nir_channel_key: Channel name or channel name and time step combination of the near-infrared channel -
            defaults to `ChannelName.NIR`
        out_channel_key: Channel name or channel name and time step combination of the output channel -
            defaults to 'adois'
        cache_dir_path: Path to the cache directory of the model -
            defaults to 'cache'
        remove_channels: If True, the channels are removed -
            defaults to True
    """
    r_channel_key: ChannelName | str | ChannelKey = ChannelName.R
    g_channel_key: ChannelName | str | ChannelKey = ChannelName.G
    b_channel_key: ChannelName | str | ChannelKey = ChannelName.B
    nir_channel_key: ChannelName | str | ChannelKey = ChannelName.NIR
    out_channel_key: ChannelName | str | ChannelKey = 'adois'
    cache_dir_path: Path = Path('cache')
    remove_channels: bool = True


_TilesProcessorFactory.register(
    tiles_processor_class=Adois,
    config_class=AdoisConfig,
    package=_PACKAGE,
)

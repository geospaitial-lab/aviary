from aviary.core.enums import ChannelName
from aviary.core.tile import Tile
from tests.core.conftest import (
    get_tile,
    get_tile_channel_1,
    get_tile_channel_4,
    get_tile_channels,
)

data_test_tile_contains = [
    (ChannelName.R, True),
    ('r', True),
    ('custom', True),
    ((ChannelName.R, None), True),
    (('r', None), True),
    (('custom', None), True),
    ('invalid', False),
    (('invalid', None), False),
    ((ChannelName.R, 0), False),
]

data_test_tile_eq = [
    # test case 1: other is equal
    (
        get_tile(),
        True,
    ),
    # test case 2: channels is not equal
    (
        Tile(
            channels=[],
            coordinates=(0, 0),
            tile_size=128,
            copy=False,
        ),
        False,
    ),
    # test case 3: coordinates is not equal
    (
        Tile(
            channels=get_tile_channels(),
            coordinates=(128, 128),
            tile_size=128,
            copy=False,
        ),
        False,
    ),
    # test case 4: tile_size is not equal
    (
        Tile(
            channels=get_tile_channels(),
            coordinates=(0, 0),
            tile_size=256,
            copy=False,
        ),
        False,
    ),
    # test case 5: copy is not equal
    (
        Tile(
            channels=get_tile_channels(),
            coordinates=(0, 0),
            tile_size=128,
            copy=True,
        ),
        True,
    ),
    # test case 6: other is not of type Tile
    (
        'invalid',
        False,
    ),
]

data_test_tile_getattr = [
    ('r', get_tile_channel_1()),
    ('custom', get_tile_channel_4()),
]

data_test_tile_getitem = [
    (ChannelName.R, get_tile_channel_1()),
    ('r', get_tile_channel_1()),
    ('custom', get_tile_channel_4()),
    ((ChannelName.R, None), get_tile_channel_1()),
    (('r', None), get_tile_channel_1()),
    (('custom', None), get_tile_channel_4()),
]

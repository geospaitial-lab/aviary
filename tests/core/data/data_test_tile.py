from aviary.core.enums import ChannelName
from tests.core.conftest import (
    get_tile_channel_1,
    get_tile_channel_4,
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

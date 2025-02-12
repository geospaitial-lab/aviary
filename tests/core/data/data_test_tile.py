from aviary.core.enums import ChannelName

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

from aviary.core.enums import ChannelName

data_test__coerce_channel_key = [
    (ChannelName.R, (ChannelName.R, None)),
    ('r', (ChannelName.R, None)),
    ('custom', ('custom', None)),
    ((ChannelName.R, None), (ChannelName.R, None)),
    ((ChannelName.R, 0), (ChannelName.R, 0)),
    (('r', None), (ChannelName.R, None)),
    (('r', 0), (ChannelName.R, 0)),
    (('custom', None), ('custom', None)),
    (('custom', 0), ('custom', 0)),
    (None, None),
]

data_test__coerce_channel_keys = [
    (ChannelName.R, {(ChannelName.R, None)}),
    ('r', {(ChannelName.R, None)}),
    ('custom', {('custom', None)}),
    ((ChannelName.R, None), {(ChannelName.R, None)}),
    ((ChannelName.R, 0), {(ChannelName.R, 0)}),
    (('r', None), {(ChannelName.R, None)}),
    (('r', 0), {(ChannelName.R, 0)}),
    (('custom', None), {('custom', None)}),
    (('custom', 0), {('custom', 0)}),
    (
        {
            ChannelName.R,
            'g',
            'custom',
        },
        {
            (ChannelName.R, None),
            (ChannelName.G, None),
            ('custom', None),
        },
    ),
    (
        {
            (ChannelName.R, None),
            ('g', None),
            ('b', 0),
            ('custom', None),
        },
        {
            (ChannelName.R, None),
            (ChannelName.G, None),
            (ChannelName.B, 0),
            ('custom', None),
        },
    ),
    (
        {
            (ChannelName.R, None),
            ('g', None),
            ('b', 0),
            'nir',
            ('custom', None),
        },
        {
            (ChannelName.R, None),
            (ChannelName.G, None),
            (ChannelName.B, 0),
            (ChannelName.NIR, None),
            ('custom', None),
        },
    ),
    (set(), set()),
    (False, set()),
    (True, True),
    (None, set()),
]

data_test__is_channel_key = [
    ((ChannelName.R, None), True),
    ((ChannelName.R, 0), True),
    (('r', None), True),
    (('r', 0), True),
    (('custom', None), True),
    (('custom', 0), True),
    ('invalid', False),
    ((ChannelName.R, ), False),
    ((ChannelName.R, None, 'invalid'), False),
]

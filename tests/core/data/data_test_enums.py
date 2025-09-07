from aviary.core.enums import ChannelName

data_test__coerce_channel_name = [
    (ChannelName.R, ChannelName.R),
    ('r', ChannelName.R),
    ('custom', 'custom'),
]

data_test__coerce_channel_names = [
    (ChannelName.R, {ChannelName.R}),
    ('r', {ChannelName.R}),
    ('custom', {'custom'}),
    (
        {
            ChannelName.R,
            'r',
            'custom',
        },
        {
            ChannelName.R,
            'custom',
        },
    ),
    (set(), set()),
    (False, set()),
    (True, True),
    (None, set()),
]

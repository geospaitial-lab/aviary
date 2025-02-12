from aviary.core.enums import ChannelName

data_test__is_channel_key = [
    ((ChannelName.R, None), True),
    ((ChannelName.R, 0), True),
    (('r', None), True),
    (('r', 0), True),
    ('invalid', False),
    ((ChannelName.R, ), False),
    ((ChannelName.R, None, 'invalid'), False),
]

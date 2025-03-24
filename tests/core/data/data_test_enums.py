from aviary.core.enums import ChannelName

data_test__coerce_channel_name = [
    (ChannelName.R, ChannelName.R),
    ('r', ChannelName.R),
    ('custom', 'custom'),
]

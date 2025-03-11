import re

import hypothesis.strategies as st

from aviary.core.enums import ChannelName

invalid_channel_names = st.text().filter(lambda x: not re.match(r'^[A-Za-z_]+$', x))

valid_channel_names = st.one_of(
    st.sampled_from(list(ChannelName)),
    st.text(
        alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_',
        min_size=1,
    ),
    st.none(),
)

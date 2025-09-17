import re

import hypothesis.strategies as st

from aviary.core.enums import ChannelName

invalid_names = st.text().filter(lambda condition: not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', condition))

valid_names = st.one_of(
    st.sampled_from(list(ChannelName)),
    st.from_regex(r'^[A-Za-z_][A-Za-z0-9_]*$', fullmatch=True),
    st.none(),
)

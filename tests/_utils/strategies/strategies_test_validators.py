#  Copyright (C) 2024-2025 Marius Maryniak
#
#  This file is part of aviary.
#
#  aviary is free software: you can redistribute it and/or modify it under the terms of the
#  GNU General Public License as published by the Free Software Foundation,
#  either version 3 of the License, or (at your option) any later version.
#
#  aviary is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with aviary.
#  If not, see <https://www.gnu.org/licenses/>.

import re

import hypothesis.strategies as st

from aviary.core.enums import ChannelName

invalid_names = st.text().filter(lambda condition: not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', condition))

valid_names = st.one_of(
    st.sampled_from(list(ChannelName)),
    st.from_regex(r'^[A-Za-z_][A-Za-z0-9_]*$', fullmatch=True),
    st.none(),
)

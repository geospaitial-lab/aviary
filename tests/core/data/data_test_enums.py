#  Copyright (C) 2024-2025 Marius Maryniak
#
#  This file is part of aviary.
#
#  aviary is free software: you can redistribute it and / or modify it under the terms of the
#  GNU General Public License as published by the Free Software Foundation,
#  either version 3 of the License, or (at your option) any later version.
#
#  aviary is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with aviary.
#  If not, see <https://www.gnu.org/licenses/>.

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

data_test__coerce_layer_names = [
    ('custom', {'custom'}),
    ({'custom'}, {'custom'}),
    (set(), set()),
    (False, set()),
    (True, True),
    (None, set()),
]

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

import importlib
import importlib.metadata
import sys
from pathlib import Path

_ENTRY_POINT = 'aviary.plugins'


def discover_local_plugins(
    plugins_dir_path: Path,
) -> None:
    """Discover plugins from a local plugins directory.

    Parameters:
        plugins_dir_path: Path to the plugins directory
    """
    sys.path.append(str(plugins_dir_path.parent))

    try:
        importlib.import_module(plugins_dir_path.name)
    finally:
        sys.path.remove(str(plugins_dir_path.parent))


def discover_packaged_plugins() -> None:
    """Discover plugins from plugin packages."""
    entry_points = importlib.metadata.entry_points().select(group=_ENTRY_POINT)

    for entry_point in entry_points:
        entry_point.load()

import importlib
import sys
from pathlib import Path


def discover_plugins(
    plugins_dir_path: Path,
) -> None:
    """Discover plugins.

    Parameters:
        plugins_dir_path: Path to the plugins directory
    """
    sys.path.append(str(plugins_dir_path.parent))

    try:
        importlib.import_module(plugins_dir_path.name)
    finally:
        sys.path.remove(str(plugins_dir_path.parent))

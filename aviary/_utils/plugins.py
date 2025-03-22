import importlib
import sys
from pathlib import Path


def register_plugins(
    plugins_dir_path: Path = Path('plugins'),
) -> None:
    """Registers plugins.

    Parameters:
        plugins_dir_path: Path to the plugins directory
    """
    sys.path.append(str(plugins_dir_path.parent))

    try:
        for plugin_path in plugins_dir_path.iterdir():
            if plugin_path.is_file() and plugin_path.suffix == '.py':
                importlib.import_module(f'{plugins_dir_path.name}.{plugin_path.stem}')
    finally:
        sys.path.remove(str(plugins_dir_path.parent))

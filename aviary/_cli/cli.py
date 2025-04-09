from pathlib import Path

try:
    import rich.traceback
    import typer
    import yaml
except ImportError as error:
    message = (
        'Missing dependencies! '
        'To use the CLI, you need to install the cli dependency group:\n'
        'pip install geospaitial-lab-aviary[cli]'
    )
    raise ImportError(message) from error

from aviary import __version__

# noinspection PyProtectedMember
from aviary._utils.plugins import register_plugins
from aviary.pipeline.tile_pipeline import (
    TilePipelineConfig,
    TilePipelineFactory,
)

# noinspection PyProtectedMember
from aviary.tile.tile_fetcher import _registry as tile_fetcher_registry

# noinspection PyProtectedMember
from aviary.tile.tiles_processor import _registry as tiles_processor_registry

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help='Python Framework for tile-based processing of geospatial data',
)

state = {
    'verbose': False,
}


def version_callback(
    value: bool,
) -> None:
    if value:
        print(f'aviary {__version__}')
        raise typer.Exit


# noinspection PyUnusedLocal
@app.callback()
def main(
    verbose: bool = typer.Option(
        False,
        '--verbose',
        '-v',
        help='Enable verbose mode.',
    ),
    version: bool = typer.Option(
        None,
        '--version',
        callback=version_callback,
        help='Show the version of the package and exit.',
    ),
) -> None:
    if verbose:
        state['verbose'] = True
        rich.traceback.install()
    else:
        rich.traceback.install(max_frames=1)


@app.command()
def docs() -> None:
    """Open the documentation in a web browser."""
    url = 'https://geospaitial-lab.github.io/aviary'
    typer.launch(url)


@app.command()
def github() -> None:
    """Open the GitHub repository in a web browser."""
    url = 'https://github.com/geospaitial-lab/aviary'
    typer.launch(url)


@app.command()
def plugins(
    plugins_dir_path: Path = typer.Argument(
        ...,
        help='Path to the plugins directory',
    ),
) -> None:
    """List the registered plugins."""
    register_plugins(plugins_dir_path=plugins_dir_path)

    tile_fetcher_names = list(tile_fetcher_registry.keys())
    tiles_processor_names = list(tiles_processor_registry.keys())
    plugin_names = (
        tile_fetcher_names +
        tiles_processor_names
    )

    print('Registered plugins:')

    for plugin_name in plugin_names:
        print(plugin_name)


@app.command()
def tile_pipeline(
    config_path: Path = typer.Argument(
        ...,
        help='Path to the configuration file',
    ),
    set_options: list[str] | None = typer.Option(
        None,
        '--set',
        '-s',
        help='Set configuration fields using key=value format.',
    ),
) -> None:
    """Run the tile pipeline."""
    with config_path.open() as file:
        config = yaml.safe_load(file)

    if set_options is not None:
        for set_option in set_options:
            if '=' not in set_option:
                message = (
                    'Invalid set_option! '
                    'The set option must be in key=value format.'
                )
                raise typer.BadParameter(message)

            key, value = set_option.split('=', 1)
            value = yaml.safe_load(value)

            sub_config = config
            sub_keys = key.split('.')

            for sub_key in sub_keys[:-1]:
                sub_config = sub_config.setdefault(sub_key, {})

            sub_config[sub_keys[-1]] = value

    plugins_dir_path = config.get('plugins_dir_path')

    if plugins_dir_path is not None:
        plugins_dir_path = Path(plugins_dir_path)
        register_plugins(plugins_dir_path=plugins_dir_path)

    tile_pipeline_config = TilePipelineConfig(**config)
    tile_pipeline = TilePipelineFactory.create(config=tile_pipeline_config)
    tile_pipeline()


if __name__ == '__main__':
    app()

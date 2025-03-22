from pathlib import Path

try:
    import typer
    import yaml
except ImportError as error:
    message = (
        'Missing dependency! '
        'To use the CLI, you need to install pyyaml and typer.'
    )
    raise ImportError(message) from error

from aviary import __version__

# noinspection PyProtectedMember
from aviary._utils.plugins import register_plugins
from aviary.pipeline.tile_pipeline import TilePipelineFactory

# noinspection PyProtectedMember
from aviary.tile.tile_fetcher import _registry as tile_fetcher_registry

# noinspection PyProtectedMember
from aviary.tile.tiles_processor import _registry as tiles_processor_registry

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help='aviary',
)


def version_callback(
    value: bool,
) -> None:
    if value:
        print(f'aviary {__version__}')
        raise typer.Exit


# noinspection PyUnusedLocal
@app.callback()
def main(
    version: bool = typer.Option(
        None,
        '--version',
        callback=version_callback,
        help='Show the version of the package and exit.',
    ),
) -> None:
    pass


@app.command()
def docs() -> None:
    """Open the documentation in a web browser."""
    url = 'https://geospaitial-lab.github.io/aviary'
    typer.launch(url)


@app.command()
def tile_pipeline(
    config_path: str,
) -> None:
    """Run the tile pipeline.

    Parameters:
        config_path: Path to the configuration file
    """
    config_path = Path(config_path)

    with config_path.open() as file:
        config = yaml.safe_load(file)

    tile_pipeline = TilePipelineFactory.create(config=config)
    tile_pipeline()


@app.command()
def plugins(
    plugins_dir_path: str = 'plugins',
) -> None:
    """List the registered plugins.

    Parameters:
        plugins_dir_path: Path to the plugins directory
    """
    plugins_dir_path = Path(plugins_dir_path)

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


if __name__ == '__main__':
    app()

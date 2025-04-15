from collections.abc import Callable
from functools import wraps
from gettext import gettext as _
from pathlib import Path
from typing import Any

try:
    import click
    import rich.console
    import typer
    import typer.rich_utils
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
from aviary._cli.templates import registry as template_registry

# noinspection PyProtectedMember
from aviary._utils.plugins import discover_plugins
from aviary.pipeline.tile_pipeline import (
    TilePipelineConfig,
    TilePipelineFactory,
)

# noinspection PyProtectedMember
from aviary.tile.tile_fetcher import _registry as tile_fetcher_registry

# noinspection PyProtectedMember
from aviary.tile.tiles_processor import _registry as tiles_processor_registry

typer.rich_utils.DEFAULT_STRING = _('default: {}')
typer.rich_utils.REQUIRED_LONG_STRING = _('required')
typer.rich_utils.RICH_HELP = _('Try [green]{command_path} {help_option}[/] for help.')
typer.rich_utils.STYLE_COMMANDS_TABLE_FIRST_COLUMN = 'bold green'
typer.rich_utils.STYLE_METAVAR = 'dim green'
typer.rich_utils.STYLE_OPTION = 'green'
typer.rich_utils.STYLE_USAGE = 'bold green'

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help='Python Framework for tile-based processing of geospatial data',
    epilog='geosp[bold green]ai[/]tial lab',
    rich_markup_mode='rich',
    pretty_exceptions_show_locals=False,
)
tile_pipeline_app = typer.Typer(
    name='tile-pipeline',
    no_args_is_help=True,
    help='Subcommands for the tile pipeline',
)
app.add_typer(
    typer_instance=tile_pipeline_app,
    rich_help_panel='Pipeline commands',
)
console = rich.console.Console()


def version_callback(
    value: bool,
) -> None:
    if value:
        print(f'aviary {__version__}')
        raise typer.Exit(0)


# noinspection PyUnusedLocal
@app.callback()
def main(
    context: typer.Context,
    verbose_option: bool = typer.Option(
        False,  # noqa: FBT003
        '--verbose',
        '-v',
        help='Enable verbose mode.',
    ),
    version_option: bool = typer.Option(  # noqa: ARG001
        None,
        '--version',
        callback=version_callback,
        help='Show the version of the package and exit.',
    ),
) -> None:
    context.obj = {
        'verbose': verbose_option,
    }


def handle_exception(
    func: Callable,
) -> Callable:
    @wraps(func)
    def wrapper(
        *args: Any,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> Any:  # noqa: ANN401
        context = click.get_current_context()
        verbose = context.obj['verbose']

        try:
            return func(
                *args,
                **kwargs,
            )
        except click.ClickException:
            raise
        except Exception as error:
            if verbose:
                raise

            console.print(f'[bold bright_red]{type(error).__name__}:[/] {error}')
            context.exit(1)
    return wrapper


@app.command(
    rich_help_panel='General commands',
)
def docs() -> None:
    """Open the documentation in a web browser."""
    url = 'https://geospaitial-lab.github.io/aviary'
    typer.launch(url)


@app.command(
    rich_help_panel='General commands',
)
def github() -> None:
    """Open the GitHub repository in a web browser."""
    url = 'https://github.com/geospaitial-lab/aviary'
    typer.launch(url)


@app.command(
    rich_help_panel='General commands',
)
@handle_exception
def plugins(
    plugins_dir_path: Path = typer.Argument(
        ...,
        help='Path to the plugins directory',
    ),
) -> None:
    """Show the registered plugins."""
    discover_plugins(plugins_dir_path=plugins_dir_path)

    tile_fetcher_names = list(tile_fetcher_registry.keys())
    tiles_processor_names = list(tiles_processor_registry.keys())

    print('Registered plugins:')
    print('  TileFetcher:')
    for plugin_name in tile_fetcher_names:
        print(f'    - {plugin_name}')

    print('  TilesProcessor:')
    for plugin_name in tiles_processor_names:
        print(f'    - {plugin_name}')


@tile_pipeline_app.command(
    name='init',
)
@handle_exception
def tile_pipeline_init(
    config_path: Path = typer.Argument(
        ...,
        help='Path to the config file',
    ),
    template_option: str = typer.Option(
        'base',
        '--template',
        '-t',
        click_type=click.Choice(['base']),
        help='Template for the config file',
    ),
) -> None:
    """Initialize a config file."""
    pipeline = 'tile_pipeline'
    key = (pipeline, template_option)
    config = template_registry[key]

    with config_path.open('w') as file:
        file.write(config)


@tile_pipeline_app.command(
    name='run',
)
@handle_exception
def tile_pipeline_run(
    config_path: Path = typer.Argument(
        ...,
        help='Path to the config file',
    ),
    set_options: list[str] | None = typer.Option(
        None,
        '--set',
        '-s',
        help='Set configuration fields using key=value format.',
    ),
) -> None:
    """Run the tile pipeline."""
    config = parse_config(
        config_path=config_path,
        set_options=set_options,
    )

    plugins_dir_path = config.get('plugins_dir_path')

    if plugins_dir_path is not None:
        plugins_dir_path = Path(plugins_dir_path)
        discover_plugins(plugins_dir_path=plugins_dir_path)

    tile_pipeline_config = TilePipelineConfig(**config)
    tile_pipeline = TilePipelineFactory.create(config=tile_pipeline_config)
    tile_pipeline()


@tile_pipeline_app.command(
    name='validate',
)
@handle_exception
def tile_pipeline_validate(
    config_path: Path = typer.Argument(
        ...,
        help='Path to the config file',
    ),
    set_options: list[str] | None = typer.Option(
        None,
        '--set',
        '-s',
        help='Set configuration fields using key=value format.',
    ),
) -> None:
    """Validate the config file."""
    config = parse_config(
        config_path=config_path,
        set_options=set_options,
    )

    plugins_dir_path = config.get('plugins_dir_path')

    if plugins_dir_path is not None:
        plugins_dir_path = Path(plugins_dir_path)
        discover_plugins(plugins_dir_path=plugins_dir_path)

    tile_pipeline_config = TilePipelineConfig(**config)
    _ = TilePipelineFactory.create(config=tile_pipeline_config)


def parse_config(
    config_path: Path,
    set_options: list[str] | None = None,
) -> dict:
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

    return config


if __name__ == '__main__':
    app()

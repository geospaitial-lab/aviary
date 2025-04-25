from collections.abc import Callable
from enum import Enum
from functools import wraps
from gettext import gettext as _
from itertools import groupby
from pathlib import Path
from typing import Any

try:
    import click
    import pyperclip
    import rich.console
    import rich.markup
    import typer
    import typer.rich_utils
    import yaml
except ImportError as error:
    message = (
        'Missing dependencies! '
        'To use the CLI, you need to install the cli dependency group (pip install geospaitial-lab-aviary[cli]).'
    )
    raise ImportError(message) from error

from aviary import __version__

# noinspection PyProtectedMember
from aviary._cli.templates import registry as template_registry

# noinspection PyProtectedMember
from aviary._utils.plugins import discover_plugins
from aviary.pipeline.tile_pipeline import (
    TilePipelineConfig,
    _TilePipelineFactory,
)

# noinspection PyProtectedMember
from aviary.tile.tile_fetcher import _TileFetcherFactory

# noinspection PyProtectedMember
from aviary.tile.tiles_processor import _TilesProcessorFactory

_PACKAGE = 'aviary'

typer.rich_utils.DEFAULT_STRING = _('default: {}')
typer.rich_utils.ENVVAR_STRING = _('env var: {}')
typer.rich_utils.REQUIRED_LONG_STRING = _('required')
typer.rich_utils.RICH_HELP = _('Try [green]{command_path} {help_option}[/] for help.')
typer.rich_utils.STYLE_COMMANDS_TABLE_FIRST_COLUMN = 'bold green'
typer.rich_utils.STYLE_METAVAR = 'dim green'
typer.rich_utils.STYLE_OPTION = 'green'
typer.rich_utils.STYLE_OPTION_ENVVAR = 'dim green'
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
)
app.add_typer(
    typer_instance=tile_pipeline_app,
    help='Subcommands for the tile pipeline (alias: tile)',
    rich_help_panel='Pipeline commands',
)
app.add_typer(
    typer_instance=tile_pipeline_app,
    name='tile',
    help='Subcommands for the tile pipeline',
    rich_help_panel='Pipeline commands',
)
console = rich.console.Console()
error_console = rich.console.Console(
    stderr=True,
)


def version_callback(
    value: bool,
) -> None:
    if value:
        message = (
            f'[dim green]aviary [/][bold green]{__version__}'
        )
        console.print(message)
        raise typer.Exit(0)


# noinspection PyUnusedLocal
@app.callback()
def main(
    context: typer.Context,
    quiet_option: bool = typer.Option(
        False,  # noqa: FBT003
        '--quiet',
        '-q',
        help='Enable quiet mode.',
    ),
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
        'quiet': quiet_option,
        'verbose': verbose_option,
    }

    if quiet_option:
        console.quiet = True


def handle_exception(
    func: Callable,
) -> Callable:
    @wraps(func)
    def wrapper(
        *args: Any,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> Any:  # noqa: ANN401
        try:
            return func(
                *args,
                **kwargs,
            )
        except click.ClickException:
            raise
        except typer.Abort:
            raise
        except typer.Exit:
            raise
        except Exception as error:
            context = click.get_current_context()
            verbose = context.obj['verbose']

            if verbose:
                raise

            message = (
                f'[bold bright_red]{type(error).__name__}:[/] {rich.markup.escape(str(error))}'
            )
            error_console.print(message)
            context.exit(1)
    return wrapper


@app.command(
    rich_help_panel='General commands',
)
@handle_exception
def components(
    package_options: list[str] | None = typer.Option(
        None,
        '--package',
        '-p',
        help='Package of the components',
    ),
    plugins_dir_path_option: Path | None = typer.Option(
        None,
        '--plugins-dir-path',
        envvar='AVIARY_PLUGINS_DIR_PATH',
        help='Path to the plugins directory',
    ),
    type_options: list[str] | None = typer.Option(
        None,
        '--type',
        '-t',
        click_type=click.Choice(['tile_fetcher', 'tiles_processor']),  # noqa: B008
        help='Type of the components',
    ),
) -> None:
    """Show the components."""
    if package_options is not None:
        def filter_packages(package: str) -> bool:
            return package in package_options
    else:
        filter_packages = None

    if type_options is not None:
        def filter_types(type_: str) -> bool:
            return type_ in type_options
    else:
        filter_types = None

    show_components(
        title='Components:',
        plugins_dir_path=plugins_dir_path_option,
        filter_packages=filter_packages,
        filter_types=filter_types,
    )


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
    package_options: list[str] | None = typer.Option(
        None,
        '--package',
        '-p',
        help='Package of the components',
    ),
    plugins_dir_path_option: Path | None = typer.Option(
        None,
        '--plugins-dir-path',
        envvar='AVIARY_PLUGINS_DIR_PATH',
        help='Path to the plugins directory',
    ),
    type_options: list[str] | None = typer.Option(
        None,
        '--type',
        '-t',
        click_type=click.Choice(['tile_fetcher', 'tiles_processor']),  # noqa: B008
        help='Type of the components',
    ),
) -> None:
    """Show the registered plugins."""
    if package_options is not None:
        def filter_packages(package: str) -> bool:
            return package in package_options and package != _PACKAGE
    else:
        def filter_packages(package: str) -> bool:
            return package != _PACKAGE

    if type_options is not None:
        def filter_types(type_: str) -> bool:
            return type_ in type_options
    else:
        filter_types = None

    show_components(
        title='Registered plugins:',
        plugins_dir_path=plugins_dir_path_option,
        filter_packages=filter_packages,
        filter_types=filter_types,
    )


@tile_pipeline_app.command(
    name='components',
)
@handle_exception
def tile_pipeline_components(
    package_options: list[str] | None = typer.Option(
        None,
        '--package',
        '-p',
        help='Package of the components',
    ),
    plugins_dir_path_option: Path | None = typer.Option(
        None,
        '--plugins-dir-path',
        envvar='AVIARY_PLUGINS_DIR_PATH',
        help='Path to the plugins directory',
    ),
) -> None:
    """Show the components."""
    if package_options is not None:
        def filter_packages(package: str) -> bool:
            return package in package_options
    else:
        filter_packages = None

    def filter_types(type_: str) -> bool:
        return type_ in ['tile_fetcher', 'tiles_processor']

    show_components(
        title='Components:',
        plugins_dir_path=plugins_dir_path_option,
        filter_packages=filter_packages,
        filter_types=filter_types,
    )


@tile_pipeline_app.command(
    name='config',
)
@handle_exception
def tile_pipeline_config(
    component: str = typer.Argument(
        ...,
        help='Component',
    ),
    copy_option: bool = typer.Option(
        False,  # noqa: FBT003
        '--copy',
        '-c',
        help='Copy the configuration to the clipboard.',
    ),
    level_option: int = typer.Option(
        0,
        '--level',
        '-l',
        help='Indentation level',
    ),
    package_option: str = typer.Option(
        'aviary',
        '--package',
        '-p',
        help='Package of the component',
    ),
    plugins_dir_path: Path | None = typer.Option(
        None,
        '--plugins-dir-path',
        envvar='AVIARY_PLUGINS_DIR_PATH',
        help='Path to the plugins directory',
    ),
) -> None:
    """Show the configuration for a component."""
    if plugins_dir_path is not None:
        discover_plugins(plugins_dir_path=plugins_dir_path)

    registry = {
        **_TileFetcherFactory.registry,
        **_TilesProcessorFactory.registry,
    }

    key = (package_option, component)
    registry_entry = registry.get(key)

    if registry_entry is None:
        message = (
            f'The component {component} from package {package_option} must be registered.'
        )
        raise typer.BadParameter(
            message=message,
            param_hint="'COMPONENT'",
        )

    _, config_class = registry_entry
    lines: list[str] = []

    for field_key, field_info in config_class.model_fields.items():
        if field_info.is_required():
            line = f'{field_key}: '
            lines.append(line)
        else:
            default_value = field_info.get_default()

            if isinstance(default_value, Enum):
                default_value = default_value.value
            elif isinstance(default_value, Path):
                default_value = str(default_value)

            line = yaml.dump(
                data={field_key: default_value},
                default_flow_style=False,
            )
            line = line.rstrip()
            lines.append(line)

    message = (
        f'[bold green]Configuration for[/] {component}[bold green] from[/][green] {package_option}[/][bold green]:'
    )
    console.print(message)

    message = (
        f'[green]  package:[/] {package_option}'
    )
    console.print(message)
    message = (
        f'[green]  name:[/] {component}'
    )
    console.print(message)
    message = (
        '[green]  config:'
    )
    console.print(message)

    for line in lines:
        key, value = line.split(':', 1)

        if value.strip():
            message = (
                f'[green]    {key}:[/][default]{value}'
            )
            console.print(message)
        else:
            message = (
                f'[green]    {key}:'
            )
            console.print(message)

    if copy_option:
        indent = ' ' * (level_option * 2)
        component_lines = [
            f'package: {package_option}',
            f'name: {component}',
            'config:',
        ]
        lines = [f'  {line}' for line in lines]
        lines = component_lines + lines
        config = indent + ('\n' + indent).join(lines)
        pyperclip.copy(config)


@tile_pipeline_app.command(
    name='init',
)
@handle_exception
def tile_pipeline_init(
    config_path: Path = typer.Argument(
        ...,
        envvar='AVIARY_CONFIG_PATH',
        help='Path to the config file',
    ),
    force_option: bool = typer.Option(
        False,  # noqa: FBT003
        '--force',
        '-f',
        help='Force overwrite the config file if it already exists.',
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
    if config_path.exists() and not force_option:
        context = click.get_current_context()
        quiet = context.obj['quiet']

        if quiet:
            message = (
                'The config file already exists. '
                "Use '--force' to overwrite it."
            )
            raise typer.BadParameter(
                message=message,
                param_hint="'--force'",
            )

        message = (
            f'[bold yellow]The config file [/][dim yellow]at {config_path.resolve()}[/][bold yellow] already exists.'
        )
        console.print(message)
        overwrite = typer.confirm('Do you want to overwrite it?')

        if not overwrite:
            raise typer.Exit(0)

    pipeline = 'tile_pipeline'
    key = (pipeline, template_option)
    config = template_registry[key]

    with config_path.open('w') as file:
        file.write(config)

    message = (
        f'[bold green]The config file [/][dim green]at {config_path.resolve()}[/][bold green] has been initialized.'
    )
    console.print(message)


@tile_pipeline_app.command(
    name='plugins',
)
@handle_exception
def tile_pipeline_plugins(
    package_options: list[str] | None = typer.Option(
        None,
        '--package',
        '-p',
        help='Package of the components',
    ),
    plugins_dir_path_option: Path | None = typer.Option(
        None,
        '--plugins-dir-path',
        envvar='AVIARY_PLUGINS_DIR_PATH',
        help='Path to the plugins directory',
    ),
) -> None:
    """Show the registered plugins."""
    if package_options is not None:
        def filter_packages(package: str) -> bool:
            return package in package_options and package != _PACKAGE
    else:
        def filter_packages(package: str) -> bool:
            return package != _PACKAGE

    def filter_types(type_: str) -> bool:
        return type_ in ['tile_fetcher', 'tiles_processor']

    show_components(
        title='Registered plugins:',
        plugins_dir_path=plugins_dir_path_option,
        filter_packages=filter_packages,
        filter_types=filter_types,
    )


@tile_pipeline_app.command(
    name='run',
)
@handle_exception
def tile_pipeline_run(
    config_path: Path = typer.Argument(
        ...,
        envvar='AVIARY_CONFIG_PATH',
        help='Path to the config file',
    ),
    set_options: list[str] | None = typer.Option(
        None,
        '--set',
        '-s',
        help='Configuration fields using key=value format.',
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
    tile_pipeline = _TilePipelineFactory.create(config=tile_pipeline_config)
    tile_pipeline()


@tile_pipeline_app.command(
    name='validate',
)
@handle_exception
def tile_pipeline_validate(
    config_path: Path = typer.Argument(
        ...,
        envvar='AVIARY_CONFIG_PATH',
        help='Path to the config file',
    ),
    set_options: list[str] | None = typer.Option(
        None,
        '--set',
        '-s',
        help='Configuration fields using key=value format.',
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
    _ = _TilePipelineFactory.create(config=tile_pipeline_config)

    message = (
        f'[bold green]The config file [/][dim green]at {config_path.resolve()}[/][bold green] is valid.'
    )
    console.print(message)


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
                    'Must be in key=value format.'
                )
                raise typer.BadParameter(
                    message=message,
                    param_hint="'--set'",
                )

            key, value = set_option.split('=', 1)
            value = yaml.safe_load(value)

            sub_config = config
            sub_keys = key.split('.')

            for sub_key in sub_keys[:-1]:
                sub_config = sub_config.setdefault(sub_key, {})

            sub_config[sub_keys[-1]] = value

    return config


def show_components(
    title: str,
    plugins_dir_path: Path | None = None,
    filter_packages: Callable[[str], bool] | None = None,
    filter_types: Callable[[str], bool] | None = None,
) -> None:
    if plugins_dir_path is not None:
        discover_plugins(plugins_dir_path=plugins_dir_path)

    tile_fetchers = sorted(
        [
            registry_entry
            for registry_entry in _TileFetcherFactory.registry
            if filter_packages is None or filter_packages(registry_entry[0])
        ],
        key=lambda registry_entry: (registry_entry[0], registry_entry[1]),
    )
    tiles_processors = sorted(
        [
            registry_entry
            for registry_entry in _TilesProcessorFactory.registry
            if filter_packages is None or filter_packages(registry_entry[0])
        ],
        key=lambda registry_entry: (registry_entry[0], registry_entry[1]),
    )

    message = (
        f'[bold green]{title}'
    )
    console.print(message)

    show_tile_fetcher = filter_types is None or filter_types('tile_fetcher')

    if show_tile_fetcher:
        message = (
            '  [bold green]TileFetcher:'
        )
        console.print(message)

        for package, components in groupby(tile_fetchers, key=lambda registry_entry: registry_entry[0]):
            message = (
                f'    [green]{package}:'
            )
            console.print(message)

            for _, component in components:
                message = (
                    f'      - {component}'
                )
                console.print(message)

    show_tiles_processor = filter_types is None or filter_types('tiles_processor')

    if show_tiles_processor:
        message = (
            '  [bold green]TilesProcessor:'
        )
        console.print(message)

        for package, components in groupby(tiles_processors, key=lambda registry_entry: registry_entry[0]):
            message = (
                f'    [green]{package}:'
            )
            console.print(message)

            for _, component in components:
                message = (
                    f'      - {component}'
                )
                console.print(message)


if __name__ == '__main__':
    app()

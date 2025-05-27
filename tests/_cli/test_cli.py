from typing import TYPE_CHECKING

from typer.testing import CliRunner

if TYPE_CHECKING:
    from click.testing import Result

from aviary._cli.cli import app


def test_help(
    runner: CliRunner,
) -> None:
    result: Result = runner.invoke(
        app=app,
        args=['--help'],
    )

    assert result.exit_code == 0


def test_version(
    runner: CliRunner,
) -> None:
    result: Result = runner.invoke(
        app=app,
        args=['--version'],
    )

    assert result.exit_code == 0

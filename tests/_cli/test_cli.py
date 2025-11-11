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

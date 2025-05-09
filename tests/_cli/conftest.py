import pytest
from typer.testing import CliRunner


@pytest.fixture(scope='function')
def runner() -> CliRunner:
    return CliRunner()

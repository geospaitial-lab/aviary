import argparse
from datetime import datetime
from pathlib import Path

import pytz

from aviary import __version__


def bump_version(
    version: str,
    bump_type: str,
) -> str:
    """Bumps the version.

    Parameters:
        version: current version
        bump_type: type of bump ('major', 'minor' or 'patch')

    Returns:
        bumped version

    Raises:
        ValueError: Invalid bump type
    """
    major, minor, patch = version.split('.')
    major, minor, patch = int(major), int(minor), int(patch)

    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'patch':
        patch += 1
    else:
        message = 'Invalid bump type!'
        raise ValueError(message)

    return f'{major}.{minor}.{patch}'


def bump_package_version(
    bumped_version: str,
) -> None:
    """Bumps the version of the package.

    Parameters:
        bumped_version: bumped version
    """
    package_path = Path(__file__).parents[2] / 'aviary' / '__init__.py'

    with package_path.open() as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if line.startswith('__version__ = '):
            lines[i] = f"__version__ = '{bumped_version}'\n"

    with package_path.open('w') as f:
        f.write(''.join(lines))


def bump_citation_version(
    bumped_version: str,
) -> None:
    """Bumps the version in the citation file.

    Args:
        bumped_version: bumped version
    """
    berlin_tz = pytz.timezone('Europe/Berlin')
    release_date = datetime.now(berlin_tz).strftime('%Y-%m-%d')

    citation_path = Path(__file__).parents[2] / 'CITATION.cff'

    with citation_path.open() as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if line.startswith('version: '):
            lines[i] = f'version: {bumped_version}\n'
        if line.startswith('date-released: '):
            lines[i] = f'date-released: {release_date}\n'

    with citation_path.open('w') as f:
        f.write(''.join(lines))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--bump-type',
        choices=['major', 'minor', 'patch'],
        required=True,
        help='Type of bump (major, minor or patch).',
    )
    args = parser.parse_args()

    version = __version__
    bumped_version = bump_version(
        version=version,
        bump_type=args.bump_type,
    )

    bump_package_version(bumped_version)
    bump_citation_version(bumped_version)

from pathlib import Path


def get_version() -> str:
    """Returns the current version.

    Returns:
        current version

    Raises:
        ValueError: Invalid version
    """
    package_path = Path(__file__).parents[2] / 'aviary' / '__init__.py'

    with package_path.open() as file:
        lines = file.readlines()

    for line in lines:
        if line.startswith('__version__ = '):
            return line.split('=')[1].strip().strip("'")

    message = 'Invalid version!'
    raise ValueError(message)


if __name__ == '__main__':
    print(get_version())

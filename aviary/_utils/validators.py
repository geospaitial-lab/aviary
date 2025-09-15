import re

from aviary.core.enums import ChannelName
from aviary.core.exceptions import AviaryUserError

_valid_name_pattern = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def validate_name(
    name: ChannelName | str | None,
    param: str,
    description: str,
) -> None:
    """Validates `name`.

    Parameters:
        name: Name
        param: Parameter
        description: Description
    """
    if not isinstance(name, str):
        return

    if not _valid_name_pattern.match(name):
        message = (
            f'Invalid {param}! '
            f'The {description} must start with a letter or underscore '
            'and contain only letters, numbers, and underscores.'
        )
        raise AviaryUserError(message)

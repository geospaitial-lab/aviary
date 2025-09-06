import re

from aviary.core.enums import ChannelName
from aviary.core.exceptions import AviaryUserError

_valid_channel_name_pattern = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def validate_channel_name(
    channel_name: ChannelName | str | None,
    param: str = 'channel_name',
    description: str = 'channel name',
) -> None:
    """Validates `channel_name`.

    Parameters:
        channel_name: Channel name
        param: Parameter
        description: Description
    """
    if not isinstance(channel_name, str):
        return

    if not _valid_channel_name_pattern.match(channel_name):
        message = (
            f'Invalid {param}! '
            f'The {description} must start with a letter or underscore '
            'and contain only letters, numbers, and underscores.'
        )
        raise AviaryUserError(message)

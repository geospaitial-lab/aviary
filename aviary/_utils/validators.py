import re

from aviary.core.enums import ChannelName
from aviary.core.exceptions import AviaryUserError

_valid_channel_name_pattern = re.compile(r'^[A-Za-z_]+$')


def validate_channel_name(
    channel_name: ChannelName | str | None,
    param_name: str = 'channel_name',
    description: str = 'channel name',
) -> None:
    """Validates `channel_name`.

    Parameters:
        channel_name: Channel Name
        param_name: Parameter Name
        description: Description
    """
    if not isinstance(channel_name, str):
        return

    if not _valid_channel_name_pattern.match(channel_name):
        message = (
            f'Invalid {param_name}! '
            f'The {description} must contain only characters and underscores.'
        )
        raise AviaryUserError(message)

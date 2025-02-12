import pytest

# noinspection PyProtectedMember
from aviary.core.type_aliases import _is_channel_key
from tests.core.data.data_test_type_aliases import data_test__is_channel_key


@pytest.mark.parametrize(('value', 'expected'), data_test__is_channel_key)
def test__is_channel_key(
    value: object,
    expected: bool,
) -> None:
    is_channel_key = _is_channel_key(value)

    assert is_channel_key is expected

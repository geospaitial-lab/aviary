from unittest.mock import (
    MagicMock,
    patch,
)

from aviary.core.process_area import ProcessArea
from aviary.inference.tile_fetcher import TileFetcher
from aviary.inference.tile_set import TileSet


def test_init() -> None:
    process_area = MagicMock(spec=ProcessArea)
    tile_fetcher = MagicMock(spec=TileFetcher)
    tile_set = TileSet(
        process_area=process_area,
        tile_fetcher=tile_fetcher,
    )

    assert tile_set._process_area == process_area
    assert tile_set._tile_fetcher == tile_fetcher


@patch('aviary.inference.tile_set.get_item')
def test_getitem(
    mocked_get_item: MagicMock,
    tile_set: TileSet,
) -> None:
    index = 0
    expected = 'expected'
    mocked_get_item.return_value = expected
    tile = tile_set[index]

    mocked_get_item.assert_called_once_with(
        process_area=tile_set._process_area,
        index=index,
        tile_fetcher=tile_set._tile_fetcher,
    )
    assert tile == expected


@patch('aviary.inference.tile_set.get_length')
def test_len(
    mocked_get_length: MagicMock,
    tile_set: TileSet,
) -> None:
    expected = 1
    mocked_get_length.return_value = expected
    length = len(tile_set)

    mocked_get_length.assert_called_once_with(
        process_area=tile_set._process_area,
    )
    assert length == expected

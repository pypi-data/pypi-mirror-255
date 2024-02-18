"""Setup fixtures"""

import pytest

from goppai.go2048 import Tile


@pytest.fixture
def tile_test_list():
    "list of tiles"
    tile_list = [Tile() for _ in range(5)]
    tile_list[1].setvalue(2)
    tile_list[3].setvalue(2)
    return tile_list

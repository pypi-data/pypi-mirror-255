"""Test tile model"""


class Test2048GameTiles:
    """test tile"""

    def test_tile_move_to_tile(self, tile_test_list):
        """test tile movements"""

        assert [_.getvalue() for _ in tile_test_list] == [0, 2, 0, 2, 0]

        assert tile_test_list[1].move_to(tile_test_list[2]) == 0

        assert [_.getvalue() for _ in tile_test_list] == [0, 0, 2, 2, 0]

        assert tile_test_list[2].move_to(tile_test_list[3]) == 4

        assert [_.getvalue() for _ in tile_test_list] == [0, 0, 0, 4, 0]

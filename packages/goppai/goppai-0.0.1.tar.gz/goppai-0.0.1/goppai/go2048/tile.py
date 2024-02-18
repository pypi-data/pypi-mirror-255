"""Board tile module"""


class Tile:
    """board tile"""

    def __init__(self) -> None:
        self.__value = 0

    def setvalue(self, value):
        """set tile value"""
        self.__value = value

    def getvalue(self):
        """get tile value"""
        return self.__value

    def move_to(self, tile):
        """move tile value"""
        if tile.getvalue() == 0:
            tile.setvalue(self.__value)
            self.__value = 0
            return self.__value
        elif tile.getvalue() == self.__value:
            tile.setvalue(self.__value + tile.getvalue())
            self.__value = 0
            return tile.getvalue()
        return -1


tile_list = [Tile() for _ in range(4)]
tile_list[1].setvalue(4)
tile_list[0].setvalue(2)

print([_.getvalue() for _ in tile_list])

lennn = len(tile_list)

for i in range(lennn):
    lennn -= 1
    tile_list[lennn - 1].move_to(tile_list[lennn])


print([_.getvalue() for _ in tile_list])

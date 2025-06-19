class Player:

    def __init__(self, id, wind):
        self.id = id
        self.hand = []
        self.melds = []
        self.discards = []
        self.seat_wind = wind

    def print_hand(self, sort_hand=False):
        if sort_hand:
            print(", ".join(str(tile) for tile in sorted(self.hand)))
        else:
            print(", ".join(str(tile) for tile in self.hand))

    def discard_tile(self, idx, sorted_hand=False):
        if sorted_hand:
            idx = self.hand.index(sorted(self.hand)[idx])
        return self.hand.pop(idx)

    def meld(self, tiles):
        for tile in tiles:
            self.hand.remove(tile)
        self.melds.append(tiles)

    def __str__(self):
        return str(self.id)

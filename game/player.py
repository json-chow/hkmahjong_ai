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

    def print_melds(self):
        print(self.melds)

    def discard_tile(self, idx, sorted_hand=False):
        if sorted_hand:
            idx = self.hand.index(sorted(self.hand)[idx])
        return self.hand.pop(idx)

    def query_meld(self, type, options):
        print(f"Player {self.id}, you have a potential {type}")
        print("0: Skip")
        for i in range(1, len(options)+1):
            print(f"{i}: {options[i-1]}")
        return input("Choice: ")

    def perform_meld(self, to_meld):
        if isinstance(to_meld[0], list):
            # Perform win
            for meld in to_meld:
                for tile in meld:
                    self.hand.remove(tile)
                self.melds.append(meld)
        else:
            # Kongs, chows, pungs
            for tile in to_meld:
                self.hand.remove(tile)
            self.melds.append(to_meld)

    def __str__(self):
        return str(self.id)

from Card import Card

HAND_SIZE = 5


def id_from(cards: [Card], id: int):
    return [e for e in cards if e.id == id][0]


class Deck:
    @staticmethod
    def generete_dummy(n):
        return [Card(2, 2, 1, False) for _ in range(n)]
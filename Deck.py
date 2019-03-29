from Card import Card

HAND_SIZE = 5
TABLE_SIZE = 7


def id_from(cards: [Card], id: int):
    return [e for e in cards if e.id == id][0]


class Deck:
    @staticmethod
    def generete_dummy(n):
        return [Card(2, 2, 1, False) for _ in range(n)]

    @staticmethod
    def group(deck: [Card]) -> [[Card]]:
        grouped = []
        for card in deck:
            def add_to_group():
                for group in grouped:
                    for card_in_group in group:
                        if card.is_equal_type(card_in_group):
                            group.append(card)
                            return
                else:
                    grouped.append([card])
            add_to_group()
        return grouped

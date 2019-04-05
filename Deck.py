from Card import Card
import numpy as np

HAND_SIZE = 5
TABLE_SIZE = 5

def calc_att_plus_hp_for_cards(cards):
    return np.array([[c.hp, c.att] for c in cards]).sum()

def id_from(cards: [Card], id: int):
    return [e for e in cards if e.id == id][0]


class Deck:
    @staticmethod
    def equals(a: [Card], b: [Card]):
        return len(a) == len(b) and \
            all(a.count(i) == b.count(i) for i in a)

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


    @staticmethod
    def generete_deck(n):
        lst = [Card(2, 1, 1, False),
               Card(2, 1, 1, False),
               Card(3, 2, 2, False),
               Card(3, 2, 2, False),
               Card(2, 3, 2, False),
               Card(2, 3, 2, False),
               Card(5, 1, 3, False),
               Card(5, 1, 3, False),
               Card(2, 7, 4, False),
               Card(2, 7, 4, False),
               Card(4, 5, 4, False),
               Card(4, 5, 4, False),
               Card(5, 4, 4, False),
               Card(5, 4, 4, False),
               Card(5, 6, 5, False),
               Card(5, 6, 5, False),
               Card(6, 7, 6, False),
               Card(6, 7, 6, False),
               Card(7, 8, 7, False),
               Card(7, 8, 7, False),
               ]
        return lst

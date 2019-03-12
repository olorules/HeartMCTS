
class Card:
    next_id = 0

    @staticmethod
    def get_next_id():
        Card.next_id += 1
        return Card.next_id

    def __init__(self, att, hp):
        self.id = Card.get_next_id()
        self.att = att
        self.hp = hp

    def __str__(self):
        return "({:2}: {}, {})".format(self.id, self.att, self.hp)


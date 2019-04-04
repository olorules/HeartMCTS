
class CardType:
    def __init__(self, att, cost, max_hp):
        self.att = att
        self.max_hp = max_hp
        self.cost = cost

    def __eq__(self, other):
        return self.att == other.att and self.cost == other.cost and self.max_hp == other.max_hp

    def __str__(self):
        return "(att:{}, hp:{}, cost:{})".format(self.att, self.max_hp, self.cost)

class Card:
    next_id = 0

    @staticmethod
    def get_next_id():
        Card.next_id += 1
        return Card.next_id

    def is_equal_id(self, other):
        return self.id == other.id

    def is_equal_type(self, other):
        # att and cost and max_hp are the same
        return self.get_type() == other.get_type()

    def get_type(self) -> CardType:
        return CardType(self.att, self.cost, self.max_hp)

    def copy(self):
        return Card(self.att, self.hp, self.cost, self.can_att, self.id, self.max_hp)

    def __init__(self, att, hp, cost, can_att, id=None, max_hp=None):
        self.id = Card.get_next_id() if id is None else id
        self.att = att
        self.hp = hp
        self.max_hp = hp if max_hp is None else max_hp
        self.cost = cost
        self.can_att = can_att

    def __str__(self):
        return "({:2}{} att:{}, hp:{}/{}, cost:{})".format(self.id, '!' if self.can_att else ':', self.att, self.hp, self.max_hp, self.cost)


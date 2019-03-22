
class Card:
    next_id = 0

    @staticmethod
    def get_next_id():
        Card.next_id += 1
        return Card.next_id

    def __init__(self, att, hp, cost, can_att):
        self.id = Card.get_next_id()
        self.att = att
        self.hp = hp
        self.cost = cost
        self.can_att = can_att

    def __str__(self):
        return "({:2}{} att:{}, hp:{}, cost:{})".format(self.id, '!' if self.can_att else ':', self.att, self.hp, self.cost)


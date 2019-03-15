
class Card:
    next_id = 0

    @staticmethod
    def get_next_id():
        Card.next_id += 1
        return Card.next_id

    def __init__(self, att, hp, cost, fresh):
        self.id = Card.get_next_id()
        self.att = att
        self.hp = hp
        self.cost = cost
        self.fresh = fresh

    def __str__(self):
        return "({:2}{} att:{}, hp:{}, cost:{})".format(self.id, '!' if self.fresh else ':', self.att, self.hp, self.cost)


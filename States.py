from Deck import HAND_SIZE, id_from


class HalfState:
    def __init__(self, deck):
        self.deck = list(deck)
        self.hand = []
        self.on_table = []
        self.trash = []
        self.hp = 20
        self.mana = 0
        self.times_taken_dmg = 0

    def take_card(self):
        if len(self.deck) > 0 and len(self.hand) < HAND_SIZE:
            self.hand.append(self.deck[0])
            self.deck = self.deck[1:]
        elif len(self.deck) == 0:
            self.times_taken_dmg += 1
            self.hp -= self.times_taken_dmg
        elif len(self.hand) >= HAND_SIZE:
            self.trash.append(self.deck[0])
            self.deck = self.deck[1:]

    def add_mana(self, num):
        #TODO: limit max mana?
        self.mana = min(self.mana+num, 10)

    def play_card(self, id):
        card = id_from(self.hand, id)
        if self.mana >= card.cost:
            self.hand.remove(card)
            self.on_table.append(card)
            self.mana -= card.cost


class GameState:
    def __init__(self, half1, half2, player_turn, turn_index):
        self.player_states = [half1, half2]
        self.player_turn = player_turn
        self.turn_index = turn_index

    def get_curr_player_id(self):
        return -1 if self.player_turn else -2

    def curr_player(self) -> HalfState:
        return self.player_states[self.player_turn]

    def other_player(self) -> HalfState:
        return self.player_states[(self.player_turn + 1) % 2]

    def take_card(self, player=None):
        if player is None:
            player = self.player_turn
        self.player_states[player].take_card()

    @staticmethod
    def generate_starting_state(deck1, deck2):
        game_state = GameState(HalfState(deck1), HalfState(deck2), 0, 0)
        return game_state

    def add_mana(self, player=None):
        if player is None:
            player = self.player_turn
        self.player_states[player].add_mana(min(self.turn_index // 2 + 1, 10))

    def turn_start(self):
        self.take_card()
        self.add_mana()

    def turn_stop(self):
        self.player_turn = (self.player_turn + 1) % 2
        self.turn_index += 1

    def make_action(self, action_id, id1=None, id2=None):
        if action_id == 0:
            #play card
            self.curr_player().play_card(id1)
        elif action_id == 1:
            #att card on card
            card = id_from(self.curr_player().on_table, id1)
            target = id_from(self.other_player().on_table, id2)
            card.hp -= target.att
            target.hp -= card.att
            if card.hp <= 0:
                self.curr_player().on_table.remove(card)
            if target.hp <= 0:
                self.other_player().on_table.remove(target)
        elif action_id == 2:
            #att card on hero
            card = id_from(self.curr_player().on_table, id1)
            self.other_player().hp -= card.att
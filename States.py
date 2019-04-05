from Deck import HAND_SIZE, id_from, Deck
from Card import Card, CardType
import itertools
TABLE_SIZE = 5


class HalfState: # player state
    def __init__(self, deck, hand=None, on_table=None, trash=None, hp=20, mana=0, times_taken_dmg=0):
        self.deck: [Card] = [card.copy() for card in deck]
        self.hand: [Card] = [] if hand is None else hand
        self.on_table: [Card] = [] if on_table is None else on_table
        self.trash: [Card] = [] if trash is None else trash
        self.hp = hp
        self.mana = mana
        self.times_taken_dmg = times_taken_dmg

    def copy(self):
        return HalfState(self.deck,
                         [card.copy() for card in self.hand],
                         [card.copy() for card in self.on_table],
                         [card.copy() for card in self.trash],
                         self.hp, self.mana, self.times_taken_dmg
                         )

    def take_card(self):
        if len(self.deck) > 0 and len(self.hand) < HAND_SIZE:
            #Draw a card
            self.hand.append(self.deck[0])
            self.deck = self.deck[1:]
        elif len(self.deck) == 0:
            # exhaustion
            self.times_taken_dmg += 1
            self.hp -= self.times_taken_dmg
        elif len(self.hand) >= HAND_SIZE:
            #Hand is full
            self.trash.append(self.deck[0])
            self.deck = self.deck[1:]

    def take_card_of_type(self, type: CardType):
        card = None
        for c in self.deck:
            if type == c.get_type():
                card = c
                break
        if card is None:
            raise Exception('Nie ma karty o danym typie.')

        if len(self.deck) > 0 and len(self.hand) < HAND_SIZE:
            #Draw a card
            self.hand.append(card)
            self.deck.remove(card)
        elif len(self.deck) == 0:
            # exhaustion
            self.times_taken_dmg += 1
            self.hp -= self.times_taken_dmg
        elif len(self.hand) >= HAND_SIZE:
            #Hand is full
            self.trash.append(card)
            self.deck.remove(card)

    def add_mana(self, turn_index):
        #TODO: limit max mana?
        self.mana = min(turn_index, 10)

    def play_card(self, id):
        card = id_from(self.hand, id)
        if self.mana >= card.cost:
            self.hand.remove(card)
            self.on_table.append(card)
            self.mana -= card.cost
        else:
            raise Exception('Nie możesz wykonać tego ruchu.')

    def __eq__(self, other):
        return self.times_taken_dmg == other.times_taken_dmg and \
            self.mana == other.mana and \
            self.hp == other.hp and \
            len(self.on_table) == len(other.on_table) and \
            len(self.hand) == len(other.hand) and \
            len(self.deck) == len(other.deck) and \
            Deck.equals(self.on_table, other.on_table) and \
            Deck.equals(self.hand, other.hand) and \
            Deck.equals(self.deck, other.deck)


class GameState:
    def __init__(self, half1, half2, player_turn, turn_index):
        self.player_states = [half1, half2]
        self.player_turn = player_turn
        self.turn_index = turn_index

    def copy(self):
        return GameState(self.player_states[0].copy(), self.player_states[1].copy(), self.player_turn, self.turn_index)

    def is_done(self):
        return self.player_states[0].hp <= 0 or self.player_states[1].hp <= 0

    def curr_player(self) -> HalfState:
        return self.player_states[self.player_turn]

    def other_player(self) -> HalfState:
        return self.player_states[(self.player_turn + 1) % 2]

    def take_card(self, player=None, draw_card_type: CardType=None):
        if player is None:
            player = self.player_turn
        if draw_card_type is None:
            self.player_states[player].take_card()
        else:
            self.player_states[player].take_card_of_type(draw_card_type)

    @staticmethod
    def generate_starting_state(deck1, deck2):
        game_state = GameState(HalfState(deck1), HalfState(deck2), 0, 0)
        for elem in range(2):
            for elem2 in range(2):
                game_state.take_card(elem)
        game_state.take_card(1)
        return game_state

    def add_mana(self, player=None):
        if player is None:
            player = self.player_turn
        self.player_states[player].add_mana(min(self.turn_index // 2 + 1, 10))

    def turn_start(self, draw_card_type: CardType=None):
        for ps in self.player_states:
            for card in ps.on_table:
                card.can_att = True
        self.take_card(draw_card_type=draw_card_type)
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
            card.can_att = False
        elif action_id == 2:
            #att card on hero
            card = id_from(self.curr_player().on_table, id1)
            self.other_player().hp -= card.att
            card.can_att = False
        elif action_id == 3: # check possible attacks
            #print(list(self.possible_plays()))
            print(self.rate_board())

    def possible_plays(self):
        res = []
        for card in self.curr_player().on_table:
            poss_attacks = [[2, card.id]]
            for target in self.other_player().on_table:
                poss_attacks.append([1,card.id, target.id])
            res.append(poss_attacks)
        #return res
        return itertools.product(*res)

    def rate_board(self):
        res = 0
        res += self.curr_player().hp * 0 - self.other_player().hp *(-0.1)
        for card in self.curr_player().on_table:
            res = res + card.att * 1.2 + card.hp
        for card in self.other_player().on_table:
            res -= card.att * 1.2 + card.hp
        return res

    def __eq__(self, other):
        return self.player_turn == other.player_turn and \
            self.turn_index == other.turn_index and \
            self.player_states[0] == other.player_states[0] and \
            self.player_states[1] == other.player_states[1]
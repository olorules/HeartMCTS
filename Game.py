from os import system
from Card import Card

HAND_SIZE = 5

class UIPlayer:
    def __init__(self):
        self.name = 'UIPlayer'

    def move(self, state):
        pass

class BotPlayer:
    def __init__(self):
        self.name = 'BotPlayer'

    def move(self, state):
        pass

class Deck:
    @staticmethod
    def generete_dummy(n):
        return [Card(2, 2) for _ in range(n)]

class HalfState:
    def __init__(self, deck):
        self.deck = list(deck)
        self.hand = []
        self.on_table = []
        self.trash = []
        self.hp = 20
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



class GameState:
    def __init__(self, half1, half2, turn):
        self.player_states = [half1, half2]
        self.player_turn = turn

    def take_card(self, player=None):
        if player is None:
            player = self.player_turn
        self.player_states[player].take_card()

    @staticmethod
    def generate_starting_state(deck1, deck2):
        game_state = GameState(HalfState(deck1), HalfState(deck2), 0)
        return game_state


class Game:

    def __init__(self):
        self.players = [BotPlayer(), UIPlayer()]
        self.state = GameState.generate_starting_state(Deck.generete_dummy(20), Deck.generete_dummy(20))

    def move(self):
        self.state.take_card(self.state.player_turn)
        self.players[self.state.player_turn].move(self.state)
        self.state.player_turn = (self.state.player_turn + 1) % 2


    def play(self):
        self.draw()
        while self.state.player_states[0].hp > 0 and self.state.player_states[1].hp > 0:
            self.move()
            self.draw()
            input('click enter...')

    def draw(self):
        #system('cls')
        print('||||||||||||||||||||||||||||||||||||||||||||||||||||||||')
        for i in range(len(self.players)):
            print("{}{}: {} {}".format(self.players[i].name, i, self.state.player_states[i].hp, 'turn' if self.state.player_turn == i else ''))
            print("Deck left: {}".format(len(self.state.player_states[i].deck)))
            print("Hand: {}".format([str(e) for e in self.state.player_states[i].hand]))
            print("Table: {}".format([str(e) for e in self.state.player_states[i].on_table]))
            print('----------------')



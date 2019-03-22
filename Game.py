from Deck import Deck
from Players import HeroAttPlayer, UIPlayer
from States import GameState


class Game:
    def __init__(self):
        self.players = [HeroAttPlayer(), UIPlayer()]
        self.state = GameState.generate_starting_state(Deck.generete_dummy(20), Deck.generete_dummy(20))

    def move(self):
        self.state.turn_start()
        self.draw()
        done = False
        while not done:
            action = self.players[self.state.player_turn].move(self.state)
            print(action)
            if 0 < len(action) <= 3:
                self.state.make_action(*action)
                self.draw()
            else:
                done = True
        self.state.turn_stop()

    def play(self):
        self.draw()
        while self.state.player_states[0].hp > 0 and self.state.player_states[1].hp > 0:
            self.move()
            # input('click enter...')
        print('winner chicken dinner: {}'.format(self.players[0].name if self.state.player_states[0].hp > 0 else self.players[1].name))

    def draw(self):
        print('||||||||||||||||||||||||||||||||||||||||||||||||||||||||')
        strings_to_print = [
            ("{}{}: HP:{} MANA:{} {}", lambda i: [self.players[i].name, i, self.state.player_states[i].hp, self.state.player_states[i].mana, 'turn' if self.state.player_turn == i else '']),
            ("Deck left: {}", lambda i: [len(self.state.player_states[i].deck)]),
            ("Hand: {}", lambda i: [[str(e) for e in self.state.player_states[i].hand]]),
            ("Table: {}", lambda i: [[str(e) for e in self.state.player_states[i].on_table]])
        ]
        for i in range(len(self.players)):
            for s, args in strings_to_print if i % 2 == 0 else strings_to_print[::-1]:
                print(s.format(*args(i)))
            print('--------')



from Deck import Deck
from States import GameState


class Game:
    def __init__(self, players, state=None, can_print=True):
        # self.players = [HeroAttPlayer(), UIPlayer()]
        self.players = players
        self.state = GameState.generate_starting_state(Deck.generete_deck(20), Deck.generete_deck(20)) if state is None else state
        self.can_print = can_print

    def move(self):
        self.state.turn_start()
        self.draw()
        done = False
        while not done:
            if self.players[self.state.player_turn].name == 'MTCSPlayer' or self.players[self.state.player_turn].name == 'RandomPlayer':
                actions = self.players[self.state.player_turn].move(self.state)
                for action in actions:
                    print(action) if self.can_print else None
                    if(len(action) >2):
                        if set([action[2],action[1]]) not in self.state.curr_player().on_table + self.state.other_player().on_table:
                            continue


                    self.state.make_action(*action)
                    self.draw()
                done = True
            else:
                action = self.players[self.state.player_turn].move(self.state)
                print(action) if self.can_print else None
                if 0 < len(action) <= 3:
                    self.state.make_action(*action)
                    self.draw()
                else:
                    done = True
        self.state.turn_stop()

    def winner_id(self):
        return 0 if self.state.player_states[0].hp > 0 else 1

    def curr_player_id(self):
        return self.state.player_turn

    def play(self):
        self.draw()
        while not self.state.is_done():
            self.move()
            # input('click enter...')
        winner_id = self.winner_id()
        print('winner chicken dinner: {}{}'.format(self.players[winner_id].name, winner_id)) if self.can_print else None

    def draw(self):
        if not self.can_print:
            return
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



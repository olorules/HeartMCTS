from Deck import Deck
from States import GameState
from Action import Action
import itertools

class Game:
    def __init__(self, players, state=None, can_print=False, gather_metadata=False):
        self.players = players
        self.state = GameState.generate_starting_state(Deck.generete_deck(20), Deck.generete_deck(20)) if state is None else state
        self.can_print = can_print

    def move(self):
        self.state.turn_start()
        self.draw()
        move = []
        mtcs_size = None
        done = False
        while not done:
            if self.players[self.state.player_turn].name == 'MTCSPlayer' or self.players[self.state.player_turn].name == 'RandomPlayer':
                actions = self.players[self.state.player_turn].move(self.state)
                for action in actions:
                    print(action) if self.can_print else None
                    if len(action) > 1 and action[0] == Action.PlayCard:
                        if action[1] not in [c.id for c in self.state.curr_player().hand]:
                            continue
                    if len(action) > 1 and action[0] == Action.AttackHero:
                        if action[1] not in [c.id for c in self.state.curr_player().on_table]:
                            continue
                    if len(action) > 2:
                        if action[2] not in [c.id for c in self.state.other_player().on_table]:
                            continue

                    move.append(action)
                    self.state.make_action(*action)
                    self.draw()
                done = True

                if self.players[self.state.player_turn].name == 'MTCSPlayer':
                    mtcs_size = self.players[self.state.player_turn].tree.num_nodes()
            else:
                action = self.players[self.state.player_turn].move(self.state)
                print(action) if self.can_print else None
                if 0 < len(action) <= 3:
                    move.append(action)
                    self.state.make_action(*action)
                    self.draw()
                else:
                    done = True
        self.state.turn_stop()

        return move, mtcs_size

    def winner_id(self):
        if self.state.player_states[0].hp > 0 and self.state.player_states[1].hp > 0:
            raise Exception('game not finished')
        return 0 if self.state.player_states[0].hp > 0 else 1

    def curr_player_id(self):
        return self.state.player_turn

    def play(self):
        self.draw()
        moves = []
        sizes = []
        while not self.state.is_done():
            m, mtcs_size = self.move()
            moves.append(m)
            if mtcs_size is not None:
                sizes.append(mtcs_size)
            # input('click enter...')
        winner_id = self.winner_id()
        print('winner chicken dinner: {}{}'.format(self.players[winner_id].name, winner_id)) if self.can_print else None
        return winner_id, list(itertools.chain.from_iterable([[e[0] for e in m] for m in moves if len(m) > 0])), self.state.turn_index // 2 + 1, sizes

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



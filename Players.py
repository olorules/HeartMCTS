import time
import numpy as np
import itertools
from random import sample

from States import GameState
from Action import Action
from Tree import Tree
from Deck import Deck, TABLE_SIZE, HAND_SIZE, id_from
from Game import Game
import pandas as pd

def list_of_combs(arr, max_len):
    combs = []
    for i in range(0, max_len+1):
        listing = [list(x) for x in itertools.combinations(arr, i)]
        combs.extend(listing)
    return combs

def list_of_possible_card_plays(curr_hand, spots_on_table, mana):
    plays = list_of_combs(curr_hand, spots_on_table)
    return [[[Action.PlayCard, card.id] for card in play] for play in plays if
                        np.sum([card.cost for card in play]) <= mana]


class RandomPlayer:
    def __init__(self):
        self.name = 'RandomPlayer'

    def move(self, state: GameState):

        curr_hand = state.curr_player().hand
        curr_table = state.curr_player().on_table
        other_table = state.other_player().on_table
        spots_on_table = TABLE_SIZE - len(curr_table)

        lst_of_plays = list_of_possible_card_plays(curr_hand, spots_on_table, state.curr_player().mana)
        all_posible_plays = [a + b for a, b in list(itertools.product(lst_of_plays,
                                                                     [list(e) for e in state.possible_plays()]))]

        smpl = sample(all_posible_plays, k=1)
        return smpl[0]


class HeroAttPlayer:
    def __init__(self):
        self.name = 'HeroAttPlayer'

    def move(self, state: GameState):
        for card in state.curr_player().on_table:
            if card.can_att:
                return [Action.AttackHero, card.id]
        if len(state.curr_player().on_table) < TABLE_SIZE:
            for card in state.curr_player().hand:
                if card.cost <= state.curr_player().mana:
                    return [Action.PlayCard, card.id]

        return []



class PlayCardPlayer:
    def __init__(self):
        self.name = 'PlayCardPlayer'

    def move(self, state: GameState):
        if len(state.curr_player().on_table) < TABLE_SIZE:
            for card in state.curr_player().hand:
                if card.cost <= state.curr_player().mana:
                    return [Action.PlayCard, card.id]

        return []

def calc_att_plus_hp_for_cards(cards):
    return np.array([[c.hp, c.att] for c in cards]).sum()

class MTCSPlayer:
    class MTCSNode(Tree):
        def __init__(self, game_state: GameState=None, actions_from_parent=None, node_type=None, card_type=None, prob=None):
            super().__init__()
            self.n = 0
            self.q = 0
            self.prob = 1 if prob is None else prob
            self.game_state: GameState = game_state
            self.actions_from_parent = actions_from_parent
            self.card_type = card_type
            self.fresh = True
            self.node_type = node_type

        def num_nodes(self):
            return 1 + np.sum([c.num_nodes() for c in self.children])

        def calc_score(self,  c):
            return (self.q / self.n) + c * np.sqrt((2 * np.log(self.parent.n)) / self.n) if self.n > 0 else -99999999

        def apply_backprop(self, delta, n):
            if self.num_children() == 0:
                self.n += 1
                self.q += delta
                return delta
            elif self.node_type == 'move':
                self.n += 1
                self.q += delta
                return delta
            elif self.node_type == 'random':
                self.n += 1  # n
                self.q += delta  # delta*n
                return 0 if delta == 1 else 0

        def gen_all_child_states(self, expand_type):
            if self.node_type == 'random':
                curr_deck = self.game_state.curr_player().deck
                other_deck = self.game_state.other_player().deck
                grouped = Deck.group(other_deck)
                types = [group[0].get_type() for group in grouped]
                probs = [len(group)/len(grouped) for group in grouped]
                probs /= np.sum(probs)
                new_children = []
                for t, p in zip(types, probs):
                    new_state = self.game_state.copy()
                    new_state.turn_stop()
                    new_state.turn_start(t)
                    new_children.append(MTCSPlayer.MTCSNode(new_state, node_type='move', card_type=t, prob=p))
                self.add_children(new_children)
            elif self.node_type == 'move':
                if expand_type == 'Full':
                    curr_hand = self.game_state.curr_player().hand
                    curr_table = self.game_state.curr_player().on_table
                    spots_on_table = TABLE_SIZE - len(curr_table)
                    legal_play_cards = list_of_possible_card_plays(curr_hand, spots_on_table, self.game_state.curr_player().mana)
                    all_posible_plays = [a + b for a, b in list(itertools.product(legal_play_cards, [list(e) for e in self.game_state.possible_plays()]))]
                    new_children = []
                    for nsa in all_posible_plays:
                        try:
                            new_state = self.game_state.copy()
                            for a in nsa:
                                new_state.make_action(*a)
                            new_children.append(MTCSPlayer.MTCSNode(new_state, node_type='random', actions_from_parent=nsa))
                        except:
                            pass
                    self.add_children(new_children)
                elif expand_type == 'PlayCardNum' or expand_type == 'PlayCardScr':
                    curr_hand = self.game_state.curr_player().hand
                    curr_table = self.game_state.curr_player().on_table
                    spots_on_table = TABLE_SIZE - len(curr_table)
                    legal_play_cards = list_of_possible_card_plays(curr_hand, spots_on_table, self.game_state.curr_player().mana)
                    k = 2 if len(legal_play_cards) < 5 else 4
                    scores = [len(e) for e in legal_play_cards] if expand_type == 'PlayCardNum' else \
                        [calc_att_plus_hp_for_cards(cards) for cards in [[id_from(self.game_state.curr_player().hand, play[1]) for play in plays] for plays in legal_play_cards]]
                    best_inds = np.argpartition(scores, -k)[-k:]
                    all_posible_plays = [a + b for a, b in list(itertools.product([legal_play_cards[i] for i in best_inds], [list(e) for e in self.game_state.possible_plays()]))]
                    new_children = []
                    for nsa in all_posible_plays:
                        try:
                            new_state = self.game_state.copy()
                            for a in nsa:
                                new_state.make_action(*a)
                            new_children.append(MTCSPlayer.MTCSNode(new_state, node_type='random', actions_from_parent=nsa))
                        except:
                            pass
                    self.add_children(new_children)
                else:
                    raise Exception('bad expand_type value')

        def __str__(self):
            return "p: {:0=.6f}, q: {:0=4d}, n: {:0=4d}, sc: {:0=4f} | ".format(self.prob, self.q, self.n, self.q / self.n if self.n != 0 else 0) + \
                   (str(self.actions_from_parent) if self.actions_from_parent is not None else str(self.card_type))

    def __init__(self, cp_base, time_per_move, expand_type, playout_type):
        self.name = 'MTCSPlayer'
        self.tree: MTCSPlayer.MTCSNode = None
        self.time_per_move = time_per_move
        self.cp_base = cp_base
        self.expand_type = expand_type
        self.playout_type = playout_type

    def move(self, state: GameState):
        if self.tree is None:
            # create tree
            self.tree = MTCSPlayer.MTCSNode(state, node_type='move')
        else:
            try:
                nodes = list(itertools.chain.from_iterable(
                    itertools.chain.from_iterable(
                        itertools.chain.from_iterable(
                            [[[o.children for o in m.children] for m in n.children] for n in self.tree.children]
                        )
                    )
                ))
                ind = [e.game_state for e in nodes].index(state)
                self.tree = nodes[ind]
            except:
                # searched node was never created
                self.tree = MTCSPlayer.MTCSNode(state, node_type='move')

        start_time = time.process_time()
        while time.process_time() - start_time < self.time_per_move:
        # for i in range(600):
            v1 = self.tree_policy(self.tree)
            delta = self.default_policy(v1)
            self.backup(v1, delta)

        # return action from best child of root node
        return self.best_child(self.tree, 0).actions_from_parent

    def tree_policy(self, node: MTCSNode):
        if node.num_children() == 0:
            node.gen_all_child_states(self.expand_type)
            if node.num_children() == 0:
                # terminal state
                return node

        for child in node.get_children():
            if child.fresh:
                child.fresh = False
                return child

        return self.tree_policy(self.best_child(node, self.cp_base))

    def best_child(self, node: MTCSNode, cp):
        if node.node_type == 'move':
            scores = np.array([child.calc_score(cp) for child in node.get_children()])
            # if cp == 0:
            #     print(scores)
            best_ind = np.argmax(scores)
            return node.get_children()[best_ind]
        else:
            probs = np.array([c.prob for c in node.get_children()])
            probs /= np.sum(probs)
            chosen = np.argmax(np.random.multinomial(1, probs))
            return node.get_children()[chosen]

    def default_policy(self, node: MTCSNode):
        mtcs_won = None
        if self.playout_type == 'Random':
            players = [RandomPlayer(), RandomPlayer()]
            new_state = node.game_state.copy()
            game = Game(players, new_state, False)
            starter_player_id = game.curr_player_id()
            game.play()
            winner_id = game.winner_id()
            mtcs_won = 1 if winner_id == starter_player_id else 0
        elif self.playout_type == 'Heur':
            curr_table = node.game_state.curr_player().on_table
            other_table = node.game_state.other_player().on_table
            curr_hp = node.game_state.curr_player().hp
            other_hp = node.game_state.other_player().hp
            mtcs_won = 1 if calc_att_plus_hp_for_cards(curr_table) + curr_hp > calc_att_plus_hp_for_cards(other_table) + other_hp else 0
        elif self.playout_type == 'HeurAgent':
            #  todo:
            raise Exception('not implemented playout')
        else:
            raise Exception('bad playout value')

        return mtcs_won

    def backup(self, node: MTCSNode, delta):
        last_node = node
        while node is not None:
            delta = node.apply_backprop(delta, last_node.prob)
            last_node = node
            node = node.get_parent()


class UIPlayer:
    def __init__(self):
        self.name = 'UIPlayer'

    def move(self, state: GameState):
        string = input('Podaj akcje ([0,2] [id]? [id]?):')
        if string == '' or string == 'n':
            return []
        command = string.split(' ')
        return [int(e) for e in command]
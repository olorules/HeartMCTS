import time
import numpy as np
import itertools
from random import sample

from States import GameState
from Action import Action
from Tree import Tree
from Deck import Deck, TABLE_SIZE, HAND_SIZE
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

        def gen_all_child_states(self):
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
                # TODO: make it better, attacks are a subset
                curr_hand = self.game_state.curr_player().hand
                curr_table = self.game_state.curr_player().on_table
                other_table = self.game_state.other_player().on_table
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

        def __str__(self):
            return "p: {:0=.6f}, q: {:0=4d}, n: {:0=4d} | ".format(self.prob, self.q, self.n) + \
                   (str(self.actions_from_parent) if self.actions_from_parent is not None else str(self.card_type))

    def __init__(self, cp_base, time_per_move):
        self.name = 'MTCSPlayer'
        self.tree: MTCSPlayer.MTCSNode = None
        self.time_per_move = time_per_move
        self.cp_base = cp_base

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
                self.tree = MTCSPlayer.MTCSNode(nodes[ind], node_type='move')
            except:
                # TODO: select sub tree from root node's children, not create new
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
            node.gen_all_child_states()
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
        # players = [HeroAttPlayer(), HeroAttPlayer()]
        players = [RandomPlayer(), RandomPlayer()]
        new_state = node.game_state.copy()
        game = Game(players, new_state, False)
        starter_player_id = game.curr_player_id()
        game.play()
        winner_id = game.winner_id()
        return 1 if winner_id == starter_player_id else 0

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
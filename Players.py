from States import GameState


class HeroAttPlayer:
    def __init__(self):
        self.name = 'HeroAttPlayer'

    def move(self, state: GameState):
        for card in state.curr_player().on_table:
            if card.can_att:
                return [Action.AttackHero, card.id]
        if len(state.curr_player().on_table) < HAND_SIZE:
            for card in state.curr_player().hand:
                if card.cost <= state.curr_player().mana:
                    return [Action.PlayCard, card.id]

        return []
        return []


class UIPlayer:
    def __init__(self):
        self.name = 'UIPlayer'

    def move(self, state: GameState):
        string = input('Podaj akcje ([0,2] [id]? [id]?):')
        if string == '':
            return []
        command = string.split(' ')
        return [int(e) for e in command]
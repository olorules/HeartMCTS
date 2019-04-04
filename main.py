from Game import Game
from Players import HeroAttPlayer, UIPlayer, MTCSPlayer, PlayCardPlayer, RandomPlayer
import numpy as np
import pandas as pd
import datetime
import itertools

def test_for(param_dict, worker, keys=None, params=None):
    outcomes = []
    if keys is None:
        keys = list(param_dict.keys())
    if params is None:
        params = {}
    if len(keys) > 0:
        key = keys[0]
        for param in param_dict[key]:
            new_params: dict = params.copy()
            new_params[key] = param
            outputs = test_for(param_dict, worker, keys[1:], new_params)
            outcomes.extend(outputs)
    else:
        # try:
        output = worker(params)
        outcomes.append(output)
        # except:
        #     pass

    return outcomes

def main():
    np.random.seed(986465)
    timestamp = datetime.datetime.now()
    # g = Game([MTCSPlayer(), UIPlayer()])
    # g = Game([MTCSPlayer(), PlayCardPlayer()])
    # g = Game((HeroAttPlayer(),UIPlayer()))
    # g = Game([RandomPlayer(), PlayCardPlayer()])
    # g = Game([RandomPlayer(), MTCSPlayer()])
    # g = Game([HeroAttPlayer(), MTCSPlayer()])
    # g.play()

    params_space = {
        'seed': [
            43534534,
            34253425,
            78675423,
            65856324,
        ],
        'cp': [0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.85, 1.0],
        'time': [10]
    }
    name = str(timestamp).replace(' ', '_').replace('-', '.').replace(':', '.')
    with open(name + '.txt', 'w') as file:
        keys = list(params_space.keys())
        vals = list(params_space.values())
        liness = [[str(k) + '\n'] + [' ' + str(v) + '\n' for v in vs] for k, vs in params_space.items()]
        file.writelines(list(itertools.chain.from_iterable(liness)))

    def runner(params):
        np.random.seed(params['seed'])
        g = Game([UIPlayer(), MTCSPlayer(params['cp'], params['time'])])
        score = g.play()
        ret = params.copy()
        ret.update({'wid': score})
        return ret
    log = pd.DataFrame(test_for(params_space, runner))
    log.to_excel(name + '.xlsx')
    print('Avg win ratio for MTCS: {}'.format(np.mean(log['wid'])))
    print(log.groupby(['cp']).mean())
    a = 0

if __name__ == "__main__":
    main()

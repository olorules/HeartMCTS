from Game import Game
from Players import HeroAttPlayer, UIPlayer, MTCSPlayer, PlayCardPlayer, RandomPlayer
import numpy as np
import pandas as pd
import datetime
import itertools
from multiprocessing import Pool
import functools
import time

def runner(params):
    np.random.seed(params['seed'])
    g = Game([MTCSPlayer(params['cp'], params['time']), RandomPlayer()])
    score = g.play()
    ret = params.copy()
    ret.update({'wid': score})
    return ret

def test_for(param_dict, keys=None, params=None):
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
            outputs = test_for(param_dict, keys[1:], new_params)
            outcomes.extend(outputs)
    else:
        # try:
        output = runner(params)
        outcomes.append(output)
        # except:
        #     pass

    return outcomes

def main():
    np.random.seed(986465)
    timestamp = datetime.datetime.now()
    seeds = [
        642406694, 614399897, 192497555, 172242113, 864437623, 430577642,
        572867839, 561357409, 573605626, 813832390, 293706663, 100232327,
        559894643, 401000648, 882843946, 828894178, 607068174, 984542426,
        173241323, 332135694,  49130241, 587887565, 301918570, 754024093,
        647203557,  68376355, 265216917, 316672848, 885174579, 167027641,
        581140635, 380653971, 834072854, 361120898, 424521210, 647126284,
        595525438, 253823747, 747099495, 194156830, 783747068, 441283594,
        570437402, 939545249, 483485403, 874809671, 342805290,  22453175,
        984587518, 623303278,  77088379, 519099333,   2470081, 893640279,
        882546828, 965127427, 556482657, 217053156, 373308154, 353759006,
        782992762,  14787852, 839767898, 504966386
    ][:8]
    params_space = {
        'cp': [0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.85, 1.0],
        'time': [0.1, 1, 5, 10]
    }
    name = str(timestamp).replace(' ', '_').replace('-', '.').replace(':', '.')
    with open(name + '.txt', 'w') as file:
        liness = [[str(k) + '\n'] + [' ' + str(v) + '\n' for v in vs] for k, vs in dict(params_space, **{'seed': seeds}).items()]
        file.writelines(list(itertools.chain.from_iterable(liness)))

    num_threads = 7
    time_start = time.time()
    real_num_threads = min(num_threads, len(seeds))
    params_subspaces = [dict(params_space, **{'seed': subseeds}) for subseeds in np.array_split(seeds, min(real_num_threads*2, len(seeds)))]
    pool = Pool(real_num_threads)
    logs = pool.map(test_for, params_subspaces)
    time_stop = time.time()
    print('took: {}s'.format(time_stop - time_start))

    log = pd.DataFrame(itertools.chain.from_iterable(logs))
    log.to_excel(name + '.xlsx')
    print('Avg win ratio for MTCS: {}'.format(log['wid'].mean()))
    print(log.groupby(['cp']).mean())
    a = 0

if __name__ == "__main__":
    main()

from Game import Game
from Players import HeroAttPlayer, UIPlayer, MTCSPlayer, PlayCardPlayer, RandomPlayer
import numpy as np
import pandas as pd
import datetime
import itertools
from multiprocessing import Pool
import time
import pickle as pkl


def runner(params):
    try:
        np.random.seed(params['seed'])
        oponent = RandomPlayer() if params['op'] == 'Random' else (HeroAttPlayer() if params['op'] == 'HeroAtt' else None)
        players = [MTCSPlayer(params['cp'], params['time'], params['expand'], params['playout']), oponent]
        g = Game(players if params['first'] == 'mtcs' else players[::-1], can_print=False, gather_metadata=True)
        wid, moves, num_turns, mtcs_sizes, mtcs_num_ppls, other_num_ppls, mtcs_table_scores, other_table_scores = g.play()
        unique, counts = np.unique(moves, return_counts=True)
        counts = counts / num_turns
        ret = params.copy()
        ret.update({
            'won': wid if params['first'] != 'mtcs' else (1-wid),
            'moves': moves,
            'num_turns': num_turns,
            'mtcs_sizes': mtcs_sizes,
            'num_play_card': np.sum(counts[unique == 0]),
            'num_att_card': np.sum(counts[unique == 1]),
            'num_att_hero': np.sum(counts[unique == 2]),
            'avg_mtcs_size': np.mean(mtcs_sizes),
            'mtcs_num_ppl': mtcs_num_ppls,
            'other_num_ppl': other_num_ppls,
            'mtcs_table_scores': mtcs_table_scores,
            'other_table_scores': other_table_scores,
            'avg_mtcs_num_ppl': np.mean(mtcs_num_ppls),
            'avg_other_num_ppl': np.mean(other_num_ppls),
            'avg_mtcs_table_scores': np.mean(mtcs_table_scores),
            'avg_other_table_scores': np.mean(other_table_scores),
        })
        return ret
    except:
        return None


def expand_space(param_dict, keys=None, params=None):
    if keys is None:
        keys = list(param_dict.keys())
    if params is None:
        params = {}
    if len(keys) > 0:
        key = keys[0]
        for param in param_dict[key]:
            new_params: dict = params.copy()
            new_params[key] = param
            yield from expand_space(param_dict, keys[1:], new_params)
    else:
        yield params


def main():
    np.random.seed(986465)
    timestamp = datetime.datetime.now()
    params_space = {
        'cp': [0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.85, 1.0],
        'time': [0.1, 1, 5],
        'expand': [
            'Full',
            'PlayCardNum',
            'PlayCardScr',
        ],
        'playout': [
            'Random',
            'Heur',
            'HeurAgent',
        ][1:2],
        'first': [
            'mtcs',
            'op'
        ],
        'op': [
            'Random',
            'HeroAtt',
            'Board',
        ][0:2],
        'seed': [
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
            782992762,  14787852, 839767898, 504966386,
        ],
    }
    params_space_size = np.prod([len(v) for v in params_space.values()])
    name = str(timestamp).replace(' ', '_').replace('-', '.').replace(':', '.')
    with open(name + '.txt', 'w') as file:
        liness = [[str(k) + '\n'] + [' ' + str(v) + '\n' for v in vs] for k, vs in params_space.items()]
        file.writelines(list(itertools.chain.from_iterable(liness)))

    num_threads = 7
    time_start = time.time()
    pool = Pool(num_threads)
    log = pd.DataFrame()
    cache = []
    cache_size = 30
    for i, v in enumerate(pool.imap(runner, expand_space(params_space), chunksize=5)):
        if v is not None:
            cache.append(v)
            print('{:4d}/{:4d}, {:3.3f}s'.format(i, params_space_size, time.time() - time_start))
            if len(cache) >= cache_size:
                log = log.append(cache, ignore_index=True)
                cache.clear()
                log.to_hdf(name + '_{:04d}of{:04d}.hdf'.format(i, params_space_size), key='key')
                print('flushed')
    if len(cache) > 0:
        log = log.append(cache, ignore_index=True)
        cache.clear()
        log.to_hdf(name + '.hdf', key='key')
        print('flushed2')

    # TODO serialize match history
    # full flush
    log.to_excel(name + '.xlsx')
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    print('Avg win ratio for MTCS: {}'.format(log['won'].mean()))
    print(log.groupby(['cp', 'expand']).mean())
    #print([np.unique(e, return_counts=True) for e in log['moves']])
    #print([[v[4] for v in l] for l in list([log.values[e.values] for e in log.groupby(['cp']).groups.values()])])  # 'mtces_sizes'
    a = 0

if __name__ == "__main__":
    main()

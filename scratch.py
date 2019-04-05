import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import itertools
import seaborn as sns

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
log = pd.read_hdf('common.hdf', 'key')
print('Avg win ratio for MTCS: {}'.format(log['won'].mean()))
print(log.groupby(['cp', 'op', 'expand', 'time']).mean())

# print([np.unique(e, return_counts=True) for e in log['moves']])
# print([[v[4] for v in l] for l in list([log.values[e.values] for e in log.groupby(['cp']).groups.values()])])  # 'mtces_sizes'

def plot_to_file(plott, title, txt_file_name, mode = 'a'):
  plott.savefig(title+'.png')
  with open(txt_file_name, mode) as file:
      file.write("""
\\begin{figure}[H]
\centering
\includegraphics[scale=1.0]{""" + title + """.png}
\caption{""" + title + """}
\label{fig:my_label}
\end{figure}

                """)

def do_action_hist(g_labels):
    grouped = log.groupby(g_labels)
    vals = [np.unique(list(itertools.chain.from_iterable(log.iloc[g_v]['moves'].values)), return_counts=True) for g_k, g_v in grouped.groups.items()]
    print(vals)
    # df = pd.DataFrame([{**{'k': k}, **e} for k,e in zip(grouped.groups.keys(), [dict(zip(*v)) for v in vals])])
    # sns.barplot(x="k", hue="kind", y="data", data=df)
    for data, key in zip(vals, list(grouped.groups.keys())):
        plt.bar(data[0], data[1], label=str(key))
        t = str(g_labels) + ', ' + str('moves') + ', ' + str(key)
        plt.title(t)
        plt.legend()
        plt.show()
        plot_to_file(plt, t, 'figures.txt')

def do_grouping_lists(g_labels, common_label):
    s_label = 'mtcs_' + common_label
    so_label = 'other_' + common_label
    grouped = log.groupby(g_labels)
    vals = \
        np.array([np.mean([[np.mean(c) for c in np.array_split(v, 8)] for v in log.iloc[g_v][s_label].values], axis=0) for g_k, g_v in grouped.groups.items()]) - \
        np.array([np.mean([[np.mean(c) for c in np.array_split(v, 8)] for v in log.iloc[g_v][so_label].values], axis=0) for g_k, g_v in grouped.groups.items()])
    print(vals)
    for data, key in zip(vals, list(grouped.groups.keys())):
        plt.plot(list(range(len(data))), data, label=str(key))
    t = str(g_labels) + ', ' + str(common_label)
    plt.title(t)
    plt.legend()
    plt.show()
    plot_to_file(plt, t, 'figures.txt')


do_grouping_lists(['won', 'time'], 'table_scores')
do_grouping_lists(['won', 'playout'], 'table_scores')
do_grouping_lists(['won', 'expand'], 'table_scores')
do_grouping_lists(['won', 'cp'], 'table_scores')
do_grouping_lists(['won', 'op'], 'table_scores')
do_action_hist(['won', 'cp'])
do_action_hist(['won', 'expand'])


a = 0

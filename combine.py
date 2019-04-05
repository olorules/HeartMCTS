import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import itertools
import seaborn as sns

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
log1 = pd.read_hdf('2019.04.05_05.05.01.946200_9998of20736.hdf', 'key')
log2 = pd.read_hdf('2019.04.05_12.34.58.898200_3872of20736.hdf', 'key')

size = min(len(log1), len(log2))
log = pd.concat([log1, log2])

log.to_hdf('common.hdf', 'key')
log.to_excel('common.xlsx')
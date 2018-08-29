# Akhil Dalal

import csv
import pandas as pd
import numpy as np
import pprint

df = pd.read_csv('libraries.csv')
df = df.sort_values(by=['Library'])

apps =  df['Application'].drop_duplicates().tolist()

df_apps = []

for a in apps:
    df_apps.append(df[df['Application'] == a].sort_values(by='Library').reset_index(drop=True))


oses = df['OS'].drop_duplicates().tolist()

res = {}

for app in df_apps:
    if app['Application'][0] not in res:
        res[app['Application'][0]] = {}
    for os1 in oses:
        for os2 in oses:
            merged = app[app['OS'] == os1].merge(app[app['OS'] == os2], how='left', on=['Library'], indicator=True)
            common = merged[merged['_merge'] == 'both'].count()['Library']
            if os1 not in res[app['Application'][0]]:
                res[app['Application'][0]][os1] = {}
            if os2 not in res[app['Application'][0]][os1]:
                res[app['Application'][0]][os1][os2] = -1
            res[app['Application'][0]][os1][os2] = common

for app in apps:
    print(app, "\n")
    data = pd.DataFrame(res[app]).T
    data = data.reindex(sorted(data.columns), axis=1).sort_index()
    mask = np.zeros_like(data, dtype=bool)
    mask[np.tril_indices_from(mask, k=-1)] = True 
    data = data.mask(mask, other = '-')
    print(data)
    print(list(data.index))
    print("\n\n")


print(df[['Application', 'OS', 'Library']].groupby(['Application', 'OS']).agg(['count']))

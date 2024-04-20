import pandas as pd

data = pd.read_csv('/Users/narendragoddu/Downloads/act-mooc/mooc_actions.tsv', sep='\t')
features_data = pd.read_csv('/Users/narendragoddu/Downloads/act-mooc/mooc_action_features.tsv', sep='\t')
labels_data = pd.read_csv('/Users/narendragoddu/Downloads/act-mooc/mooc_action_labels.tsv', sep='\t')

data = data.join(features_data, on="ACTIONID", how='left', rsuffix="_y")
data = data.join(labels_data, on="ACTIONID", how='left', rsuffix="_y")
data = data.drop('ACTIONID_y', axis=1)
data = data.sort_values(by='LABEL')
data = data.drop_duplicates(subset=['ACTIONID', 'TIMESTAMP'], keep='last').dropna(axis=0)

zeros = data.loc[data['LABEL'] == 0]
ones = data.loc[data['LABEL'] == 1]
users = data['USERID'].drop_duplicates()
targets = data['TARGETID'].drop_duplicates()

users.to_csv('./users.csv', index=False)
targets.to_csv('./targets.csv', index=False)
zeros.reset_index(drop=True).to_csv('./zeros.csv', index=False)
ones.reset_index(drop=True).to_csv('./ones.csv', index=False)


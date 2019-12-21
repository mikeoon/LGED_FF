import numpy as np
import pandas as pd

def _clean_team_name(name_series):
	name_series = name_series.str.strip('Team(')
	name_series = name_series.str.strip(')')
	return name_series

def load_matchup_data(start, end):
	result = {}
	for w in range(start, (end+1)):
		matchup_df = pd.read_csv(f'../data/2019/{w}wk_matchups.csv')
		for i in ['team', 'opp']:
			matchup_df[i] = _clean_team_name(matchup_df[i])
		result[f'wk{w}'] = matchup_df
	return result

def create_allmatchups_df(data):
	count = 0
	for k, v in data.items():
		if count == 0:
			all_matchups = v.copy()
			count+=1
		else:
			all_matchups = pd.concat((all_matchups, v), axis=0, sort=False)
	return all_matchups.reset_index().drop(['index','QB1'], axis=1)


def fix_team_names(data):
	matt_name = lambda x: 'Post Mahomes' if x == 'Seattle Post Mahomes' else x
	danny_name = lambda x: '2 Girls 1 Kupp' if x == 'urf Munchers' else x
	data['team'] = data['team'].map(matt_name)
	data['team'] = data['team'].map(danny_name)
	return data

def add_gm_names(data):
	gms = ['junghwan', 'charlie', 'matt', 'mike', 'anil', 'kyle', 'sunjin',
			 'eugene','connor', 'zach', 'kai', 'danny']
	gms_teams = {gm:team for gm, team in zip(gms,all_match['team'].unique())}
	teams_gms = {v:k for k,v in gms_teams.items()}
	data['team_gm'] = data['team'].map(lambda x: teams_gms[x])

	return data


























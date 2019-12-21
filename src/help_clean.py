import numpy as np
import pandas as pd

def _clean_team_name(name_series):
	name_series = name_series.str.strip('Team(')
	name_series = name_series.str.strip(')')
	return name_series

def load_matchup_data(start, end):
	result = {}
	for w in range(start, (end+1)):
		matchup_df = pd.read_csv(f'/Users/youngjungyoon/LGED/LGED_FF/data/2019/{w}wk_matchups.csv')
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
	return all_matchups.reset_index().drop('index', axis=1)




























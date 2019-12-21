import numpy as np
import pandas as pd


'''
Script to create a Pandas dataframe that has all the FF ESPN matchups
The script pulls data from csv files that were collected via FF ESPN api
If these csv files don't exist, then no dataframe

CURRENTLY
Must call load_matchup_data to read the csv
Then using the dictionary crated from load_matchup_data, call create_allmatchups_df

'''

def _clean_team_name(name_series):
	'''
	Cleans the names pulled from the FF ESPN api

	Parameters: team name series from all_m df
	Return: Series with the clean names
	'''
	
	name_series = name_series.str.strip('Team(')
	name_series = name_series.str.strip(')')
	return name_series

def load_matchup_data(start, end):
	'''
	Reads in the FF ESPN api matchups by week.
	Data must in csv files pulled by the FF ESPN api

	Parameters: start - num of week, end - num of week
	Return: Dict with all data for each week

	'''

	result = {}
	for w in range(start, (end+1)):
		matchup_df = pd.read_csv(f'data/2019/{w}wk_matchups.csv')
		for i in ['team', 'opp']:
			matchup_df[i] = _clean_team_name(matchup_df[i])
		result[f'wk{w}'] = matchup_df
	return result

def create_allmatchups_df(data):
	'''
	Creates a pandas dataframe of the data read in via csv from the FF ESPN api

	Parameters: data - dict of read in csv values of matchups
	Returns: all_matchups - pandas dataframe with all matchup data from csv
	'''

	count = 0
	for k, v in data.items():
		if count == 0:
			all_matchups = v.copy()
			count+=1
		else:
			all_matchups = pd.concat((all_matchups, v), axis=0, sort=False)
	all_matchups = all_matchups.reset_index().drop('index', axis=1)
	all_matchups = _fix_team_names(all_matchups)
	all_matchups = _add_gm_names(all_matchups)

	return all_matchups


def _fix_team_names(all_m):

	'''
	Fixes the team names since people change their FF team name
	Should be only number of team names per gm
	CURRENTLY HARDCODED, SHOULD AUTOMATE THIS PROCESS MORE

	Parameters: all_m - all_matchups dataframe from create_allmatchups_df
	Returns: all_m - df with correct team names
	'''

	matt_name = lambda x: 'Post Mahomes' if x == 'Seattle Post Mahomes' else x
	danny_name = lambda x: '2 Girls 1 Kupp' if x == 'urf Munchers' else x
	all_m['team'] = all_m['team'].map(matt_name)
	all_m['team'] = all_m['team'].map(danny_name)
	return all_m

def _add_gm_names(all_m):
	'''
	Add's the team_gm column to the all_matchups df
	ALSO CURRENTLY HARDCODED, SHOULD FIND A WAY TO FIX THIS	

	Parameters: all_m - all_matchups dataframe from create_allmatchups_df
	Returns: all_m - df with team_gm column
	
	'''

	gms = ['junghwan', 'charlie', 'matt', 'mike', 'anil', 'kyle', 'sunjin',
			 'eugene','connor', 'zach', 'kai', 'danny']
	gms_teams = {gm:team for gm, team in zip(gms,all_m['team'].unique())}
	teams_gms = {v:k for k,v in gms_teams.items()}
	all_m['team_gm'] = all_m['team'].map(lambda x: teams_gms[x])

	return all_m
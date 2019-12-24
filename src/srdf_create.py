import pandas as pd
import numpy as np

import src.help_clean as hc

from sportsreference.nfl.schedule import Schedule
from sportsreference.nfl.boxscore import Boxscore, Boxscores
from sportsreference.nfl.teams import Teams
from sportsreference.nfl.roster import Roster



def create_boxscore_dfs(season, start, end):
	b_games=[]
	player_dict = dict()
	player_stats=[]
	box_id = []
	box_keys ={}
	box_games = Boxscores(start, season, end).games
	for k,v in box_games.items():
	    for box in v:
	        box_keys[box['boxscore']] = k.split('-')[0]
	        box_id.append(box['boxscore'])
	#box_id = [ids['boxscore'] for v in box_games.values() for ids in v]
	for ids in box_id:
	    box = Boxscore(ids)
	    for p in box.home_players:
	        if p not in player_dict.keys():
	            player_dict[p.name]=p.player_id
	        temp_hplayer_df = p.dataframe
	        temp_hplayer_df['box_id'] = ids
	        temp_hplayer_df['team'] = box.home_abbreviation
	        temp_hplayer_df['name'] = p.name
	        player_stats.append(temp_hplayer_df)
	    for p in box.away_players:
	        if p not in player_dict.keys():
	            player_dict[p.name]=p.player_id
	        temp_aplayer_df = p.dataframe
	        temp_aplayer_df['box_id'] = ids
	        temp_aplayer_df['team'] = box.away_abbreviation
	        temp_aplayer_df['name'] = p.name
	        player_stats.append(temp_aplayer_df)
	    b_games.append(box.dataframe)
	boxscore_stats_df = pd.concat(player_stats)
	box_df = pd.concat(b_games)
	# Temp cut out to try and work it into the first nested loop
	#box_keys ={}
	#for k,v in box_games.items():
	#    for box in v:
	#        box_keys[box['boxscore']] = k.split('-')[0]
	
	# creates in the boxscore_stats_df a column for what week the game was played
	boxscore_stats_df['week'] = boxscore_stats_df['box_id'].map(lambda x: box_keys[x])

	# Creates a column for the week the game was played
	box_df = box_df.reset_index().rename(columns={'index':'box_id'})
	box_df['week'] = box_df['box_id'].map(lambda x: box_keys[x])
	box_df = box_df.set_index('box_id')

	return boxscore_stats_df, box_df, player_dict

# Code to fix the DJ to D.J. for the espn names to SR names
def dot_name(name):
    if type(name) != float:
        name_split=name.split()
        if len(name_split[0]) == 2 and name_split[0].isupper() and name_split[1] != 'Chark':
            dot_name = ''
            for i in name_split[0]:
                dot_name+=(i+'.')
            
            return dot_name + ' ' +' '.join(name_split[1:])
        else:
            return name
    return name

# Make code for 3 word names like Jr., II, V, etc.
def three_names(name):
    if type(name) != float:
        name_split=name.split()
        if len(name_split)==3:
            if name_split[2] == 'Jr.' or name_split[2] == 'Sr.':
                new_name=' '.join(name_split[:2])
            elif name_split[2] in ['II', 'III', 'IV', 'V']:
                new_name=' '.join(name_split[:2])
            else:
                new_name=name
            return new_name
        else:
            return name
    return name

# Function to fix names
# Hard coded names that are far from the data base and the espn names
def broken_name(name):
    b_names = {'Jonathan Hilliman': 'Jon Hilliman', 'Mike Badgley':'Michael Badgley'}
    if name in b_names.keys():
        return b_names[name]
    return name


def create_ff_players_df(player_dict, week):
	combine_player_pos=[pd.read_csv(f'data/2019/{i+1}wk_players.csv')for i in range(0, week)]
	player_pos_df = pd.concat(combine_player_pos)
	player_pos_df.rename(columns={'0':'name', '1':'pos'}, inplace=True)
	p_unique=[]
	for p in player_pos_df['name'].unique():
	    if 'D/ST' not in p:
	        p_unique.append(p)

	player_pos_df.rename(columns={'name':'espn_name'}, inplace=True)
	player_pos_df['sr_name'] = player_pos_df['espn_name'].map(lambda p: broken_name(three_names(dot_name(p))))
	unique_players = set()
	for idx,player in player_pos_df.iterrows():
	    a,b,c = player.values
	    unique_players.add((a,b,c))
	u_player_pos_df = pd.DataFrame(unique_players).rename(columns={0:'espn_name', 1:'pos', 2:'sr_name'})
	u_player_pos_df['player_id'] = u_player_pos_df['sr_name'].map(lambda x: player_dict[x] if 'D/ST' not in x and x not in ['A.J. Green','Rob Gronkowski'] else np.nan)

	return u_player_pos_df


def clean_teams(boxscore_stats, player_pos):
    # Players that are a bit strange... see notes above
    spec_clean={'Justin Jackson':'sdg', 'Kenyan Drake':'crd', 'Jonathan Williams':'clt'}
    fix_teams = {}
    
    # Finds all unique names in the player_pos dataframe
    # Renames the ESPN API data to fit the sportsreference names
    p_unique=[broken_name(three_names(dot_name(p))) for p in player_pos['name'].unique() if 'D/ST' not in p]

    # Identifies where the teams need to be fixed
    # Currently hard coded to any player with more than 2 designated teams are flagged
    for player in p_unique:
        teams = {_ for _ in boxscore_stats[boxscore_stats['name']==player]['team'].values.flatten()}
        if len(teams)>3:
            fix_teams[player] = teams
    
    # Identifies the team with the most number of entries, that being the players actual team        
    fix_teams = {k:(boxscore_stats[boxscore_stats['name'] == k].team.value_counts().max(), 
                    boxscore_stats[boxscore_stats['name'] == k].team.value_counts().index[0]) for k in fix_teams.keys()}
    
    # Updates the table with the correct teams for the players
    # Players that are somewhat broken, are found in the spec_clean, and must be handled specifically
    for k,v in fix_teams.items():
        if k not in spec_clean.keys():
            player_loc=boxscore_stats[boxscore_stats['name'] == k].index[0]
            boxscore_stats.loc[player_loc,'team'] = boxscore_stats.loc[player_loc,'team'].map(lambda x: v[1] if x != v[1] else x)
    
    # Clean up specific players 
    for k,v in spec_clean.items():
        player_loc=boxscore_stats[boxscore_stats['name'] == k].index[0]
        if k == 'Kenyan Drake':
            boxscore_stats.loc[player_loc,'team'] = boxscore_stats.loc[player_loc,'team'].map(lambda x: v if x != 'mia' else x)
        else:
            boxscore_stats.loc[player_loc,'team'] = boxscore_stats.loc[player_loc,'team'].map(lambda x: v if x != v else x)
    
    return boxscore_stats
















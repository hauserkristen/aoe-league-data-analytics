from typing import List
from mgz.fast import Action
from mgz.model import Inputs

def parse_action(action: Inputs):
    # Check for actions
    if action.type == 'Research':
        if action.payload['technology_id'] in [101, 102, 103]:
            return action.param, action.timestamp

    return None, None
 
def get_age_up_times(actions: List[Inputs], player_name):
    age_up_times = {}
    for action in actions:
        # Check for player name match
        if action.player is not None:
            if action.player.name == player_name:
                age, time = parse_action(action)
                if age is not None:
                    age_up_times[age] = time
    return age_up_times
from typing import List
from mgz.fast import Action
from mgz.model import Inputs

def get_consecutive_count(values):
    ret = []
    current = None
    count = 0
    for v in values:
        if current != v:
            if count > 0:
                ret.append((current, count))
            current = v
            count = 1
        else:
            count += 1
    return ret

def parse_action(action: Inputs):
    # Check for actions
    if action.type == 'Queue':
        return action.param
    elif action.type == 'Build':
        return action.param
    elif action.type == 'Research':
        return action.param

    return None

def get_build_order(actions: List[Inputs], player_name):
    bo = []
    for action in actions:
        # Check for player name match
        if action.player is not None:
            if action.player.name == player_name:
                action_result = parse_action(action)
                if action_result is not None:
                    bo.append(action_result)
            
    # Get reduced BO
    reduced_bo = get_consecutive_count(bo)

    # TODO: Estimate BO and return name
    return 'Scouts -> Knights'
from typing import List
from mgz.fast import Action
from mgz.model import Inputs
from datetime import timedelta

TC_TECHS = [
    101, # Feudal Age
    102, # Castle Age
    103, # Imperial Age
    22,  # Loom
    213, # Wheelbarrow
    249, # Hand Cart
    8,   # Town Watch
    280  # Town Patrol
]

# TODO: Accomodate civ bonuses like Persians?
TC_RESEARCH_TIME = {
    'Villager': 25, 
    'Feudal Age': 130,
    'Castle Age': 160,
    'Loom': 25,
    'Wheelbarrow': 75,
    'Town Watch': 25
}

def get_tc_actions(action: Inputs):
    # Check for actions
    if action.type == 'Research':
        if action.payload['technology_id'] in TC_TECHS:
            return action
    elif action.type == 'Queue' and action.param == 'Villager':
        return action

    return None
 
def calculate_idle_time(action: Inputs, current_age: str, queue_expiration: timedelta):
    tc_time = TC_RESEARCH_TIME[action.param]

    # Calculate if idle time is occured
    idle_time = timedelta()
    remaining_que = timedelta()
    if queue_expiration < action.timestamp:
        idle_time = action.timestamp - queue_expiration
    else:
        remaining_que = queue_expiration - action.timestamp

    # Calculate time that the queue will be busy for tc
    new_current_age = current_age
    if action.type == 'Research':
        queue_time = timedelta(seconds=tc_time)
        if action.payload['technology_id'] in [101, 102, 103]:
            new_current_age = action.param
    else:
        vill_count = action.payload['amount']
        queue_time = timedelta(seconds=(vill_count * tc_time))

    # Calculate new expiration
    total_queue = queue_time + remaining_que
    new_queue_expiration = action.timestamp + total_queue

    print('Current Time {:<15}  Queue Exp {:<15}  Step Idle Time {:<15}  Queue {:<15} New Queue Exp {:<15}'.format(str(action.timestamp), str(queue_expiration), str(idle_time), str(total_queue), str(new_queue_expiration)))

    return idle_time, new_current_age, new_queue_expiration


def get_idle_tc_time(actions: List[Inputs], player_name):
    # DEBUG
    print('Queue History for {}'.format(player_name))

    # Get all tc actions
    tc_actions = []
    for action in actions:
        # Check for player name match
        if action.player is not None:
            if action.player.name == player_name:
                tc_action = get_tc_actions(action)
                if tc_action is not None:
                    tc_actions.append(tc_action)

    # Calculate idle tc time
    idle_tc = {
        'Dark Age': timedelta(),
        'Feudal Age': timedelta()
    }
    current_age = 'Dark Age'
    queue_expiration = timedelta()
    for action in tc_actions:
        idle_time, new_current_age, queue_expiration = calculate_idle_time(action, current_age, queue_expiration)

        # Add idle time
        idle_tc[current_age] += idle_time

        # Update age
        current_age = new_current_age

        # Break if new age is castle
        if current_age == 'Castle Age':
            break 

    return idle_tc
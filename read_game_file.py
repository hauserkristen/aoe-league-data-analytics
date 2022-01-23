from datetime import timedelta
import json
from game_analysis.age_up_times import get_age_up_times
from game_analysis.idle_tc_time import get_idle_tc_time
from mgz.model import parse_match

from game_analysis import get_build_order

def main():
    test_file = 'game_files/Stealth_R_Us_1200.aoe2record'

    with open(test_file, 'rb') as h:
        match = parse_match(h)

        # Print general match up
        match_summary = ''
        for i, player_1 in enumerate(match.teams[0]):
            # Add comma seperation per team
            if i > 1:
                match_summary += ', '
            match_summary += '{} ({})'.format(player_1.name, player_1.civilization)

        match_summary += ' vs '
        for i, player_2 in enumerate(match.teams[1]):
            # Add comma seperation per team
            if i > 1:
                match_summary += ', '
            match_summary += '{} ({})'.format(player_2.name, player_2.civilization)
        
        estimated_bo = {}
        age_up_times = {}
        idle_times = {}
        for player in match.players:
            # Get estimate BO
            estimated_bo[player.name] = get_build_order(match.inputs, player.name)

            # Get age up times
            age_up_times[player.name] = get_age_up_times(match.inputs, player.name)
            
            # Get idle time
            idle_times[player.name] = get_idle_tc_time(match.inputs, player.name)

        # Display results in table
        print(match_summary)
        print ("{:<15} {:<30} {:<25} {:<20} {:<25} {:<20} {:<20}".format('Player', 'Estimated BO', 'Dark Age TC Idle Time', 'Feudal Time', 'Feudal Age TC Idle Time', 'Castle Time', 'Imperial Time'))
        for player in match.players:
            # Default game times
            if 'Castle Age' not in age_up_times[player.name].keys():
                castle_time = str(timedelta())
            else:
                castle_time = str(age_up_times[player.name]['Castle Age'])
            if 'Imperial Age' not in age_up_times[player.name].keys():
                imp_time = str(timedelta())
            else:
                imp_time = str(age_up_times[player.name]['Imperial Age'])

            print ("{:<15} {:<30} {:<25} {:<20} {:<25} {:<20} {:<20}".format(
                player.name,
                estimated_bo[player.name],
                str(idle_times[player.name]['Dark Age']),
                str(age_up_times[player.name]['Feudal Age']),
                str(idle_times[player.name]['Feudal Age']),
                castle_time,
                imp_time
            ))

        # Actual answers
        # Stealth idle - Dark : 0:20 - Feudal : 0:31
        # @00:04 - 0:01 idle
        # @02:07 - 0:01 idle
        # @02:59 - 0:02 idle
            # @06:07 - two vills queued
            # @06:18 - one vill un-queued
        # @07:35 - 0:16 idle
        # Feudal Age
        # @14:11 - 0:10 idle
        # @16:06 - 0:01 idle
        # Gilboy idle  - Dark : 0:43 - Feudal : 2:14
        # @00:04 - 0:01 idle
        # @03:48 - 0:01 idle
        # @04:13 - 0:06 idle
        # @04:43 - 0:30 idle
        # @08:33 - 0:05 idle
        # Feudal Age
        # @11:38 - 0:16 idle
        # @12:19 - 0:14 idle
            

if __name__ == '__main__':
    main()
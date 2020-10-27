from penguin_game import *

"""
My name is TGbot. I'm still a little dumb, but I'm working on it
"""

# All groups to specific destination
def groups_to_dest(grouplist, dest):
    return [ gp for gp in grouplist if gp.destination == dest]


# Check if I have more iceberg than the enemy
def have_more_icebergs(game):
    return True if len(game.get_my_icebergs()) > len(game.get_enemy_icebergs()) else False


# Send Penguins 
def send_group(source, destination, group):
    print(source, "sends", group, "penguins to", destination)
    source.send_penguins(destination, group)


#Upgrade iceberg
def upgrade(iceberg, penguins):
    if penguins >= iceberg.upgrade_cost and iceberg.upgrade_level_limit > iceberg.level:
        iceberg.upgrade()
        return True
    return False
    
    
# Return the closest destination to specific iceberg
def closet_destination(game, iceberg):
    return sorted(game.get_all_icebergs(), key = lambda x: iceberg.get_turns_till_arrival(x))[1]
            

# claculate futur state of an iceberg in x turns
def iceberg_state_in_X_turns(game, iceberg, turns):
    enemy_groups = [gp for gp in groups_to_dest(game.get_my_penguin_groups(), iceberg) if
                    gp.turns_till_arrival <= turns]
    my_groups = [gp for gp in groups_to_dest(game.get_enemy_penguin_groups(), iceberg) if
                    gp.turns_till_arrival <= turns]
    all_groups = sorted(enemy_groups + my_groups, key=lambda gp: gp.turns_till_arrival)  # gp[3] : turns_till_arrival
    
    print("all groups to this iceberg")
    print(all_groups)
    
    owner = iceberg.owner
    penguins = iceberg.penguin_amount
    print("penguins now on this iceberg " + str(penguins))
    for gp in all_groups:
        if owner != game.get_neutral():
            penguins += (gp.turns_till_arrival * iceberg.level)
        if gp.owner == owner:
            penguins += gp.penguin_amount
        else:
            penguins -= gp.penguin_amount
            if penguins < 0:
                owner = gp.owner
                penguins *= -1
            elif penguins == 0:
                owner = game.get_neutral()
    if owner != game.get_neutral():
        if all_groups:
            turns -= all_groups[len(all_groups) - 1].turns_till_arrival
        penguins += (turns * iceberg.level)
    
    print("iceberg " + str(iceberg.id) + " state")
    print([owner, penguins])
    return {"owner":owner, "penguins":penguins}


# The best icebergs according to the distance and the amount I sent (sent/did not send)
def best_iceberg(game, icebergs, my_iceberg, available):
    destinations = []
    
    # Sort destinations by strategy. The strategy (for now) is the shortest distance 
    icebergList = sorted(icebergs, key=lambda x: my_iceberg.get_turns_till_arrival(x))
    
    #  # Go through all the destinations 
    for iceberg in icebergList:
        
        # Calculate the owner of the iceberg and the number of penguins that will be on it 
        # if we send a group in the current queue
        future_state = iceberg_state_in_X_turns(game, iceberg, my_iceberg.get_turns_till_arrival(iceberg))
        
        # If I do not own the iceberg but can conquer it, add it to the destinations list and reduce the number of penguins available
        if future_state["owner"] != game.get_myself() and available > future_state["penguins"]:
            destinations.append([iceberg, future_state["penguins"] + 1])  # [destintion & amount of peguins to send]
            available -= (future_state["penguins"] + 1)
        else:
            # If you can not conquer the near destinations, do not go further (?) 
            return destinations
    
    return destinations


# The main function
def do_turn(game):

    """
    :param game: the current game state
    :type game: Game
    """
    
    print("turn num: " + str(game.turn))

    initial_iceberg = game.get_my_icebergs()[0]
    
    # Wait for the other to attack or for the game to come to an end before attacking
    if not game.get_enemy_penguin_groups() and game.turn + closet_destination(game, initial_iceberg).get_turns_till_arrival(initial_iceberg)<game.max_turns:
        upgrade(initial_iceberg, initial_iceberg.penguin_amount)
        return
   
    # Go through all the icebergs
    for my_iceberg in game.get_my_icebergs():

        percentage = 1
        available = int(my_iceberg.penguin_amount * percentage) 
        
        # Check if there is a group that can conquer me or leave me with too few penguins
        # Allows conquest / upgrade only if not
        if not [gp for gp in groups_to_dest(game.get_enemy_penguin_groups(), my_iceberg)
                if iceberg_state_in_X_turns(game, my_iceberg, gp.turns_till_arrival+1)["owner"] == game.get_enemy
                or iceberg_state_in_X_turns(game, my_iceberg, gp.turns_till_arrival+1)["penguins"]-gp.penguin_amount<my_iceberg.upgrade_cost ]:
            
            # Look for the best destination for an attack
            destinations = best_iceberg(game, game.get_neutral_icebergs() + game.get_enemy_icebergs(),
                                        my_iceberg, available)
            for destination in destinations:
                send_group(my_iceberg, destination[0], destination[1])
            
            # Try to upgrade if no good destination is found
            if not destinations:
                upgrade(my_iceberg, available)

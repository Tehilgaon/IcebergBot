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
    if (penguins >= iceberg.upgrade_cost) and (iceberg.upgrade_level_limit > iceberg.level):
        iceberg.upgrade()
        return True
    return False
 


# Return all the icebergs except a specific one
def other_icebergs(game, iceberg):
    return [x for x in game.get_all_icebergs() if x != iceberg]



# return list of destinations sorted by their distance from a specific iceberg
def closest_strategy(game, iceberg, destinations):
    return sorted(destinations, key = lambda x: iceberg.get_turns_till_arrival(x))[0]



# return list of destinations sorted by their level of centrality
def central_strategy(game, destinations):  
    most_central_dest = {}  # dict {iceberg: sum_distances}
    for dest in destinations:
        sum_distance = 0
        for oth_dest in destinations:
            sum_distance += dest.get_turns_till_arrival(oth_dest)
        most_central_dest[dest] = sum_distance
    return list(most_central_dest.keys())



# claculate futur state of an iceberg in x turns
def iceberg_state_in_X_turns(game, iceberg, turns):
    print("iceberg " + str(iceberg.id) + ": ")
    enemy_groups = [gp for gp in groups_to_dest(game.get_my_penguin_groups(), iceberg) if
                    gp.turns_till_arrival <= turns]
    my_groups = [gp for gp in groups_to_dest(game.get_enemy_penguin_groups(), iceberg) if
                    gp.turns_till_arrival <= turns]
    all_groups = sorted(enemy_groups + my_groups, key=lambda gp: gp.turns_till_arrival)  # gp[3] : turns_till_arrival
    
    print("all groups to this iceberg")
    print(all_groups)
    
    # The owner and penguins amount on the iceberg in this turn
    owner = iceberg.owner 
    penguins = iceberg.penguin_amount
    print("penguins now on this iceberg " + str(penguins))
    
    # Calculate the iceberg changes in turns until arrival time
    for gp in all_groups:
        if owner != game.get_neutral():
            penguins += (gp.turns_till_arrival * iceberg.level)
        
        # Add the number of penguins if they belong to the same group
        # Subtract if they are from the opposite group
        if gp.owner == owner:
            penguins += gp.penguin_amount
        else:
            penguins -= gp.penguin_amount
            
            # Change owner
            if penguins < 0:
                owner = gp.owner
                penguins *= -1
            elif penguins == 0:
                owner = game.get_neutral()
    
    # Adds the natural multiplicity of penguins, if they are not neutral penguins
    if owner != game.get_neutral():
        if all_groups:
            turns -= all_groups[len(all_groups) - 1].turns_till_arrival
        penguins += (turns * iceberg.level)
    
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
        if  future_state["owner"] == game.get_myself(): continue
        elif available > future_state["penguins"]:
            destinations.append([iceberg, future_state["penguins"] + 1])  # [destintion & amount of peguins to send]
            available -= (future_state["penguins"] + 1)
        else:
            # If you can not conquer the near destinations, do not go further (?) 
            return destinations
    
    return destinations


# Calculates the average number of turns of several icebergs from the destination
def turns_avg(game, destination, sources):
    sum_distance = sum([s.get_turns_till_arrival(destination) for s in sources])
    return sum_distance // len(sources)



def ambush(game, destination, sources):
    sources_sending = {}
    sources.sort(key = lambda x: x.penguin_amount, reverse = True)
    future_state = iceberg_state_in_X_turns(game, destination, turns_avg(game, destination, sources))
    if future_state["owner"] == game.get_myself(): return sources_sending
    for source in sources:  
        if source.penguin_amount > future_state["penguins"]:
            sources_sending[source] = future_state["penguins"] + 1  # [source : amount of peguins to send]
            return sources_sending
        else:
            sources_sending[source] = source.penguin_amount * 0.5
            future_state["penguins"] -= source.penguin_amount * 0.5   
    return sources_sending



# The main function
def do_turn(game):

    print("turn num: " + str(game.turn))

    initial_iceberg = game.get_my_icebergs()[0]
    # Wait for the other to attack or for the game to come to an end before attacking
    if not game.get_enemy_penguin_groups() and initial_iceberg.level < initial_iceberg.upgrade_level_limit:  
        upgrade(initial_iceberg, initial_iceberg.penguin_amount)
        return
    
    # Check if there is a group that can conquer me or leave me with too few penguins
        # Allows conquest / upgrade only if not
    available_icebregs = [iceberg for iceberg in game.get_my_icebergs() if iceberg not in [gp.destination for gp in groups_to_dest(game.get_enemy_penguin_groups(), iceberg)
        if iceberg_state_in_X_turns(game, iceberg, gp.turns_till_arrival+1)["owner"] == game.get_enemy 
        or iceberg_state_in_X_turns(game, iceberg, gp.turns_till_arrival+1)["penguins"] - gp.penguin_amount < iceberg.upgrade_cost]]
    
    
    enemy_groups = game.get_enemy_penguin_groups() 
    if available_icebregs and enemy_groups:
        # Go through all the enemy's groups  
        for group in enemy_groups:
            destination = group.destination
            sources = ambush(game, destination, available_icebregs)   
            for source, amount in sources.items():
                send_group(source, destination, amount)
    
    else:
        # Go through all the icebergs
        for my_iceberg in available_icebregs:

            percentage = 1
            available = int(my_iceberg.penguin_amount * percentage) 
                
            # Look for the best destination for an attack
            destinations = best_iceberg(game, game.get_neutral_icebergs() + game.get_enemy_icebergs(),
                                            my_iceberg, available)
            for destination in destinations:
                send_group(my_iceberg, destination[0], destination[1])
                
                # Try to upgrade if no good destination is found
            if not destinations:
                upgrade(my_iceberg, available)
        
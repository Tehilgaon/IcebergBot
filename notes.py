"""
This is an example for a bot.
"""
from penguin_game import *


def do_turn(game):
    """
    Makes the bot run a single turn.

    :param game: the current game state.
    :type game: Game
    """
    
    listhelp=[]
    
    # Go over all of my icebergs.
    for my_iceberg in game.get_my_icebergs():
        flag=False
        distance1=300
        # The amount of penguins in my iceberg.
        if my_iceberg.level<2:
            my_iceberg.upgrade()
        
        else:
            my_penguin_amount = my_iceberg.penguin_amount  # type: int
            
            # If there are any neutral icebergs.
            if game.get_neutral_icebergs():
                # Target a neutral iceberg.
                for iceberg in game.get_neutral_icebergs():
                    d=iceberg
                    distance=my_iceberg.get_turns_till_arrival(iceberg)
                    if len(game.get_my_icebergs())<3:
                        if game.get_my_penguin_groups():
                            for t in game.get_my_penguin_groups():
                                if t.source.equals(my_iceberg) and t.destination not in game.get_my_icebergs():
                                    d=t.destination
                                    break
                            #s=not(game.get_my_penguin_groups()[0].source.equals(my_iceberg))
                        else:
                            d=my_iceberg
                        if distance < distance1 and not (d.equals(iceberg)):
                            distance1=distance
                            destination=iceberg
                            flag=True
                            destination_penguin_amount = destination.penguin_amount  # type: int
                    else:
                        flag=True
                        for iceberg in game.get_neutral_icebergs():
                            distance=my_iceberg.get_turns_till_arrival(iceberg)
                            #Will attack the icebergs we can conquer the fastest, according to the distance and amount of penguins on the icebergs.
                            if distance + iceberg.penguin_amount < distance1:
                                distance1=distance
                                destination=iceberg
                        #The number of penguins in the destination also depends on the growth rate of the penguins and the amount of turns until we reach the destination.
                        destination_penguin_amount = destination.penguin_amount
            else:
                s=True
                # Target an enemy iceberg.
                for iceberg in game.get_enemy_icebergs():
                    distance=my_iceberg.get_turns_till_arrival(iceberg)
                    #Will attack the icebergs we can conquer the fastest, according to the distance and amount of penguins on the icebergs.
                    if distance < distance1:
                        distance1=distance
                        destination=iceberg
                #The number of penguins in the destination also depends on the growth rate of the penguins and the amount of turns until we reach the destination.
                destination_penguin_amount = destination.penguin_amount+ destination.get_turns_till_arrival(my_iceberg)*destination.penguins_per_turn  # type: int
                flag=True

            # The amount of penguins the target has.
           
            # Send penguins to the ta:
            if flag:
                print(my_iceberg + "sends" + (destination_penguin_amount + 1) + "penguins to" + destination)
                my_iceberg.send_penguins(destination, destination_penguin_amount + 1)
            #listhelp.append(destination)




-------------------------------------------------------------------------------------------------------
for ice in protectSorted:
            d_owner, d_amount = IceState(game, destination, my_iceberg.get_turns_till_arrival(ice))
            amount = d_amount
            while amount >= my_iceberg.penguins_per_turn:
                _owner, m_amount = IceState(game, my_iceberg, my_iceberg.get_turns_till_arrival(ice), amount)
                if m_owner == game.get_myself(): 
                    break
                amount -= 1
            print(my_iceberg, "sends", (amount), "penguins to", destination)
            my_iceberg.send_penguins(ice, amount)
            
def enemyTerritory(game, my_ice):
    ices = sorted(game.get_all_icebergs(), key = lambda x: my_ice.get_turns_till_arrival(x))
    ices = ices[1:len(ices)//4]
    for ice in ices:
        if ice.owner != game.get_enemy():
            return False
    if sum(ice.penguin_amount for ice in ices) < my_ice.penguin_amount:
        return False
    return True

def closetEnemy(game, my_ice):
    dest = None
    for ice in game.get_enemy_icebergs():
        if not dest or my_ice.get_turns_till_arrival(ice) < my_ice.get_turns_till_arrival(dest):
            dest = ice
    return dest


def have_more_icebergs(game):
    return True if len(game.get_my_icebergs()) >= len(game.get_enemy_icebergs()) else False

# return list of destinations sorted by their level of centrality
def central_strategy(game, destinations):  
    most_central_dest = {}  # dict {iceberg: sum_distances}
    for dest in destinations:
        sum_distance = 0
        for oth_dest in destinations:
            sum_distance += dest.get_turns_till_arrival(oth_dest)
        most_central_dest[dest] = sum_distance
    return list(most_central_dest.keys())
    
# All groups to specific destination
def groups_to_dest(grouplist, dest):
    return [ gp for gp in grouplist if gp.destination == dest]

def iceToAttack(ices):
    dest = None
    for ice in ices:
        if not dest or ice.penguin_amount < dest.penguin_amount:
            dest = ice
    return ice

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
 

# claculate futur state of an iceberg in x turns
def ice_state(game, iceberg, turns):   
    groups = [x for x in game.get_my_penguin_groups()+game.get_enemy_penguin_groups() if x.turns_till_arrival <= turns and x.destination == iceberg]
    groups.sorted(key=lambda gp: gp.turns_till_arrival)  # gp[3] : turns_till_arrival
      
    # The owner and penguins amount on the iceberg in this turn
    owner = iceberg.owner 
    penguins = iceberg.penguin_amount
    # Calculate the iceberg changes in turns until arrival time
    for x in groups:
        if owner != game.get_neutral():
            penguins += (x.turns_till_arrival * iceberg.level)
        
        # Add the number of penguins if they belong to the same group
        # Subtract if they are from the opposite group
        if x.owner == owner:
            penguins += x.penguin_amount
        else:
            penguins -= x.penguin_amount     
            # Change owner
            if penguins < 0:
                owner = x.owner
                penguins *= -1
            elif penguins == 0:
                owner = game.get_neutral()  
    # Adds the natural multiplicity of penguins, if they are not neutral penguins
    if owner != game.get_neutral():  
        penguins += ((Time-curTime) * iceberg.level)
    return  penguins



# The best icebergs according to the distance and the amount I sent (sent/did not send)
def best_iceberg(game, icebergs, my_iceberg, available):
   
    destinations = {}
    icebergList = sorted(icebergs, key=lambda x: my_iceberg.get_turns_till_arrival(x)) if len(game.get_my_icebergs()) <= 3 else central_strategy(game, icebergs)
    
    #for gp in game.get_enemy_penguin_groups():
        #if not gp.turns_till_arrival and gp.destination != my_iceberg: icebergList.insert(gp.destination, 0)
    
    #  # Go through all the destinations 
    for ice in icebergList: 
        # Calculate the owner of the iceberg and the number of penguins that will be on it 
        # if we send a group in the current queue
        future_state = iceberg_state_in_X_turns(game, ice, my_iceberg.get_turns_till_arrival(ice))
        
        # If I do not own the iceberg but can conquer it, add it to the destinations list and reduce the number of penguins available
        if  future_state["owner"] == game.get_myself(): continue
        elif available > int(future_state["penguins"]):
            print("here?")
            destinations[ice] = (future_state["penguins"] + 1)  # [destintion & amount of peguins to send]
            available -= (future_state["penguins"] + 1)
        else:
            # If you can not conquer the near destinations, do not go further (?) 
            return destinations    
    return destinations


def groupSizePercentage(game):
    p = 0
    for gp in game.get_enemy_penguin_groups():
        p += (gp.penguin_amount / (iceberg_state_in_X_turns(game, gp.destination, gp.turns_till_arrival)["penguins"] + 1))
    return p / len(game.get_enemy_penguin_groups())   
        

# The main function
def do_turn(game):

    print("turn num: " + str(game.turn))

    ice1 = game.get_my_icebergs()[0]
    # Wait for the other to attack or until reaching the highest level
    if not game.get_enemy_penguin_groups() and ice1.level < ice1.upgrade_level_limit:  
        upgrade(ice1, ice1.penguin_amount)
        return
 
    # Go through all the icebergs
    for my_iceberg in game.get_my_icebergs():
        
        # Check if there is a group that can conquer me or leave me with too few penguins
        # Allows conquest / upgrade only if not
        if not [gp for gp in groups_to_dest(game.get_enemy_penguin_groups(), my_iceberg)]:
                #if iceberg_state_in_X_turns(game, my_iceberg, gp.turns_till_arrival+1)["owner"] == game.get_enemy
                #or iceberg_state_in_X_turns(game, my_iceberg, gp.turns_till_arrival+1)["penguins"]-gp.penguin_amount<my_iceberg.upgrade_cost ]:
        
            available = int(my_iceberg.penguin_amount)  
            destinations = {}
            
            # Look for the best destination for an attack
            destinations.update(best_iceberg(game, game.get_neutral_icebergs() + game.get_enemy_icebergs(),
                                        my_iceberg, available))
            
            for dest, amount in destinations.items():
                send_group(my_iceberg, dest, amount)
            
            # Defending
            destinations.clear()
            for gp in game.get_enemy_penguin_groups():
                if gp.destination in game.get_my_icebergs():
                    future_state = iceberg_state_in_X_turns(game, gp.destination, gp.turns_till_arrival)
                    # if future_state["owner"] == game.get_enemy() and gp.turns_till_arrival <= my_iceberg.get_turns_till_arrival(gp.destination) and available > future_state["penguins"]:
                    if available > gp.penguin_amount:
                        destinations[gp.destination] = (gp.penguin_amount + 1)
                        available -= (gp.penguin_amount + 1)
        
            for dest, amount in destinations.items():
                send_group(my_iceberg, dest, amount)
            
            # Try to upgrade if no good destination is found
            if not destinations:
                upgrade(my_iceberg, available)
 
            
    # log(game)




def log(game):
    print("turn num: " + str(game.turn))
    print("enemys iceberges")
    print(game.get_enemy_icebergs())
    print("enemys groups")
    print([(x.penguin_amount, x.destination) for x in game.get_enemy_penguin_groups()])
    print("enemyScore " + str(game.get_enemy().score))
    print("my iceberges")
    print(game.get_my_icebergs())
    print("my groups")
    print([(x.penguin_amount, x.destination) for x in game.get_my_penguin_groups()])    
    print("myScore " + str(game.get_myself().score))
    



    ------------------------------------------------------------------------------------------------------------------------------

 """
This is an example for a bot.
"""
from penguin_game import *

def groupsize(groups):
    sum = 0
    for x in groups:
        sum += x.penguin_amount
    return sum // len(groups)

def groups(ice,group):
    count=0
    for x in group:
        if x.destination==ice:
            count+=x.penguin_amount
    return count


#check if the iceberg will stay netural or not.
def willStayNeutral(game , iceberg , my_iceberg):
    turn_till_arrivial = my_iceberg.get_turns_till_arrival(iceberg)
    for ei in game.get_enemy_icebergs():
        ei_amount = ei.penguin_amount + (turn_till_arrivial * iceberg.penguins_per_turn)
        if ei_amount >= (ei.get_turns_till_arrival(iceberg) * iceberg.penguins_per_turn):
            return False
    return True
    
    

def do_turn(game):
    """
    Makes the bot run a single turn.

    :param game: the current game state.
    :type game: Game
    """
    # Go over all of my icebergs.

    for my_iceberg in game.get_my_icebergs():
        my_penguin_amount = my_iceberg.penguin_amount  # type: int
        neturalSorted = sorted(game.get_neutral_icebergs(), key=lambda x: my_iceberg.get_turns_till_arrival(x))
        enemySorted = sorted(game.get_enemy_icebergs(), key=lambda x:my_iceberg.get_turns_till_arrival(x))
        y = 1
        if game.get_enemy_penguin_groups():
            g = groupsize(game.get_enemy_penguin_groups())
            y = my_iceberg.penguin_amount // g if 5 < g < my_iceberg.penguin_amount else 1
            
        if game.get_neutral_icebergs():
           neutral = neturalSorted[0]
        if game.get_enemy_icebergs():
            enemy = enemySorted[0]
       
        if game.get_neutral_icebergs() and game.get_enemy_icebergs() and my_iceberg.get_turns_till_arrival(neutral) < my_iceberg.get_turns_till_arrival(enemy):
            if groups(neutral, game.get_my_penguin_groups()) and game.turn < 25 :
                neutral = neturalSorted[1]
               
            destination = neutral
            # The amount of penguins the target will have.
              
            if game.turn < 25 or game.turn % 5 == 0:
                destination_penguin_amount = destination.penguin_amount
            else:
                 destination_penguin_amount = destination.penguin_amount//y
     
        elif game.get_enemy_icebergs() and game.turn % 10 != 0 :
            destination = enemySorted[0]
            destination_penguin_amount = destination.penguin_amount//y-1  # type: int
        elif game.get_neutral_icebergs():
            destination = neturalSorted[0]
            destination_penguin_amount = destination.penguin_amount//y
        else:
            destination = enemySorted[0]
            destination_penguin_amount = destination.penguin_amount//y-1  # type: int
        
        
        if groups(my_iceberg,game.get_enemy_penguin_groups()) > my_iceberg.penguin_amount - destination_penguin_amount:
            s=True
        elif my_iceberg.level < 2 and my_iceberg.can_upgrade():  # if it safe, upgrade.
            print my_iceberg, "upgrade to level ", my_iceberg.level
            my_iceberg.upgrade() 

        # If my iceberg has more penguins than the target iceberg.
        else:
    
            print my_iceberg, "sends", (destination_penguin_amount + 1), "penguins to", destination
            my_iceberg.send_penguins(destination, destination_penguin_amount + 1)
            
        elif game.turn % 15!=0 and ( game.get_neutral_bonus_iceberg() and game.turn>= 60 ) or (
        groups(game.get_bonus_iceberg(),game.get_enemy_penguin_groups())>=game.get_bonus_iceberg().penguin_amount) and my_iceberg in bonusSorted[: len(bonusSorted)//2]:
            if groups(game.get_bonus_iceberg(),game.get_my_penguin_groups())<11:
                my_iceberg.send_penguins(game.get_bonus_iceberg(),destination_penguin_amount )

        elif my_iceberg.can_create_bridge(destination) and destination.owner == game.enemy game.turn%10==0 and my_iceberg.penguin_amount - game.iceberg_bridge_cost > groups(my_iceberg, game.get_enemy_penguin_groups()) and my_iceberg.get_turns_till_arrival(destination) > 20:
            my_iceberg.create_bridge(destination)   
"""
This is an example for a bot.
"""


# All the destinations my penguins' group are on their way to
def enemy_destinations(game):
    return [[gp.id, gp.destination, gp.penguin_amount, gp.turns_till_arrival, gp.owner]
            for gp in game.get_enemy_penguin_groups()]


def my_destinations(game):
    return [[gp.id, gp.destination, gp.penguin_amount, gp.turns_till_arrival, gp.owner]
            for gp in game.get_my_penguin_groups()]


def has_more_icebergs(game):
    return 1 if len(game.get_my_icebergs()) > len(game.get_enemy_icebergs()) else 0


def send_group(source, destination, group):
    print(source, "sends", group, "penguins to", destination)
    source.send_penguins(destination, group)


def penguins_on_iceberg_in_X_turns(game, iceberg, turns):
    # gp[0] : id
    # gp[1] : destination
    # gp[2] : amount
    # gp[3] : turns_till_arrival
    # gp[4] : Owner
    enemy_groups = [gp for gp in enemy_destinations(game) if
                    gp[1] == iceberg and gp[3] <= turns]
    my_groups = [gp for gp in my_destinations(game) if gp[1] == iceberg and gp[3] <= turns]
    all_groups = sorted(enemy_groups + my_groups, key=lambda gp: gp[3])  # gp[3] : turns_till_arrival
    print("all group to this iceberg")
    print(all_groups)
    owner = iceberg.owner
    num = iceberg.penguin_amount
    print("penguins now on this iceberg " + str(num))
    for gp in all_groups:
        if owner != game.get_neutral():
            num += (gp[3] * iceberg.level)
        if gp[4] == owner:
            num += gp[2]
        else:
            num -= gp[2]
            if num < 0:
                owner = gp[4]
                num *= -1
            if num == 0:
                owner = game.get_neutral()

    if all_groups and owner != game.get_neutral():
        turns -= all_groups[len(all_groups) - 1][3]
        num += (turns * iceberg.level)
    print("iceberg " + str(iceberg.id) + " state")
    print([owner, num])
    return [owner, num]


# The best icebergs according to the distance and the amount I sent (sent/did not send)
def best_iceberg(game, icebergs, my_iceberg, available):
    destinations = []
    icebergList = sorted(icebergs, key=lambda x: my_iceberg.get_turns_till_arrival(x))
    for iceberg in icebergList:
        future_state = penguins_on_iceberg_in_X_turns(game, iceberg, my_iceberg.get_turns_till_arrival(iceberg))
        # future_state[0]: owner   # future_state[1]: penguins_amount

        if future_state[0] != game.get_myself() and available > future_state[1]:
            destinations.append([iceberg, future_state[1] + 1])  # iceberg, amount to send
            available -= (future_state[1] + 1)

    return destinations


# The main function
def do_turn(game):
    print("turn num: " + str(game.turn))

    if game.get_my_icebergs()[0].level < 2:
        game.get_my_icebergs()[0].upgrade()
        return

    for my_iceberg in game.get_my_icebergs():

        percentage = 1
        available = int(my_iceberg.penguin_amount * percentage)

        '''
        # Check the Id of enemy's group that come to attack me
        groups = [g[0] for g in enemy_destinations(game) if g[1] == my_iceberg]
        if groups:
            # --- 
          #  if are there available penguins on the iceberg
        if available:
            if has_more_icebergs(game):
                # defend other'''

        destinations = best_iceberg(game, game.get_neutral_icebergs() + game.get_enemy_icebergs(),
                                    my_iceberg, available)
        for destination in destinations:
            send_group(my_iceberg, destination[0], destination[1])
        if not destinations:
            if available >= my_iceberg.upgrade_cost and my_iceberg.upgrade_level_limit > my_iceberg.level:
                my_iceberg.upgrade()

import random


# Creates a list of lists filled with the characters' color in each room (index 0 is room 0, ... up to room 9)
# needs the game_state variable
def get_current_positions(game_state):
    current_map = [[], [], [], [], [], [], [], [], [], []]
    for char in game_state["characters"]:
        if char["suspect"]:
            current_map[char["position"]].append(char["color"])
    return current_map


# Crates a list with the number of characters inside the rooms with a specific character, the indexes of these numbers correspond to the indexes of the possible choices sent by the server
# needs the possible answers of the server and the current map (with get_current_positions)
def get_number_characters(characters_data, current_map):
    nb_characters = [0] * len(characters_data)
    for i in range(len(characters_data)):
        for case in current_map:
            if characters_data[i]["color"] in case:
                nb_characters[i] = len(case)
    return nb_characters


# Creates a list containing the indexes of the get_number_characters of the biggest number of characters within a room
# needs the number_of_characters in the desired rooms (from get_number_characters)
def get_least_isolated_char(nb_characters):
    maximum_char = max(nb_characters)
    maximum_indexes = []
    for i in range(len(nb_characters)):
        if nb_characters[i] == maximum_char:
            maximum_indexes.append(i)
    return maximum_indexes


# Creates a list with the indexes of the possible moves corresponding to the rooms with the smallest number of players in them
# need the possible moves from the server and the current map (from get_current_positions)
def get_smallest_rooms(possible_moves, current_map):
    smallest_rooms_index = []
    least_full_room = 10
    for i in range(len(possible_moves)):
        if len(current_map[possible_moves[i]]) < least_full_room:
            least_full_room = len(current_map[possible_moves[i]])
    for i in range(len(possible_moves)):
        if len(current_map[possible_moves[i]]) == least_full_room:
            smallest_rooms_index.append(i)
    return smallest_rooms_index


# the ghost must select characters who are with more other in a room in order to isolate them
def select_character(fantom_logger, data, current_map, game_state):
    i = 0
    for char in data:
        if char["color"] == "red":
            return i
        i += 1
    nb_characters = get_number_characters(data, current_map)
    maximum_indexes = get_least_isolated_char(nb_characters)
    fantom_logger.debug(f"nb_characters ------- {nb_characters}")
    fantom_logger.debug(f"minimum_indexes ----- {maximum_indexes}")
    response_index = random.choice(maximum_indexes)
    return response_index


# the position selected is the room with the least number of persons in it
def select_position(fantom_logger, data, current_map, game_state):
    small_rooms = get_smallest_rooms(data, current_map)
    fantom_logger.debug(f"big_rooms ------- {small_rooms}")
    response_index = random.choice(small_rooms)
    return response_index


# Creates the behaviour of the grey character
# in order to help the ghost, the grey character must switch off the lights of the room with the biggest number of characters
def grey_character_power(fantom_logger, data, current_map, game_state):
    biggest_room_population = 0
    indexes = []
    for i in range(len(data)):
        if biggest_room_population < len(current_map[data[i]]):
            biggest_room_population = len(current_map[data[i]])
    for j in range(len(data)):
        if len(current_map[data[j]]) == biggest_room_population:
            indexes.append(j)
    response_index = random.choice(indexes)
    return response_index


# since the brown power makes another character comes with him, we decided to always says "NO" in order to leave him alone
def activate_brown_power(fantom_logger, data, current_map, game_state):
    return 0


def brown_character_power(fantom_logger, data, current_map, game_state):
    return 0


# we try to lock the loneliest characters
def blue_character_power_room(fantom_logger, data, current_map, game_state):
    top_locks = get_smallest_rooms(data, current_map)
    fantom_logger.debug(f"top_locks ------- {top_locks}")
    response_index = random.choice(top_locks)
    return response_index


def blue_character_power_exit(fantom_logger, data, current_map, game_state):
    power_exit = random.randint(0, len(data) -1)
    fantom_logger.debug(f"power_exit ------- {power_exit}")
    response_index = power_exit
    return response_index


#the black power brings everyone close to her so we never activate it
def activate_black_power(fantom_logger, data, current_map, game_state):
    return 0


# the white power is activated only if the white is suspect so he stays alone
def activate_white_power(fantom_logger, data, current_map, game_state):
    for char in game_state["characters"]:
        if char["color"] == "white":
            if char["suspect"]:
                return 1
            else:
                return 0

# we move the characters first to the rooms where there is no one, then the rooms with more than 1 person and finally the others
def white_power(fantom_logger, data, current_map, game_state):
    i = 0
    the_rest = []
    no = []
    for room_number in data:
        if len(current_map[room_number]) == 0:
            return i
        elif len(current_map[room_number]) == 1:
            no.append(i)
        else:
            the_rest.append(i)
        i += 1
    if len(the_rest) > 0:
        return random.choice(the_rest)
    return random.choice(no)


# he just switches places with another character so it's not necessary in our method
def activate_purple_power(fantom_logger, data, current, game_state):
    return 0

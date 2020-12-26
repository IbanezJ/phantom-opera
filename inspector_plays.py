import random


# Creates a list of lists filled with the characters' color in each room (index 0 is room 0, ... up to room 9)
# needs the game_state variable
def get_current_positions(game_state):
    current_map = [[], [], [], [], [], [], [], [], [], []]
    for char in game_state["characters"]:
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


# Creates a list containing the indexes of the get_number_characters of the smallest number of characters within a room
# needs the number_of_characters in the desired rooms (from get_number_characters)
def get_most_isolated_char(nb_characters):
    minimum_char = min(nb_characters)
    minimum_indexes = []
    for i in range(len(nb_characters)):
        if nb_characters[i] == minimum_char:
            minimum_indexes.append(i)
    return minimum_indexes


# Creates a list with the indexes of the possible moves corresponding to the rooms with the biggest number of players in them
# need the possible moves from the server and the current map (from get_current_positions)
def get_biggest_rooms(possible_moves, current_map):
    biggest_rooms_index = []
    most_full_room = 0
    for i in range(len(possible_moves)):
        if len(current_map[possible_moves[i]]) > most_full_room:
            most_full_room = len(current_map[possible_moves[i]])
    for i in range(len(possible_moves)):
        if len(current_map[possible_moves[i]]) == most_full_room:
            biggest_rooms_index.append(i)
    return biggest_rooms_index


def select_character(inspector_logger, data, current_map):
    nb_characters = get_number_characters(data, current_map)
    minimum_indexes = get_most_isolated_char(nb_characters)
    inspector_logger.debug(f"nb_characters ------- {nb_characters}")
    inspector_logger.debug(f"minimum_indexes ----- {minimum_indexes}")
    response_index = random.randint(0, len(minimum_indexes) - 1)
    return response_index


def select_position(inspector_logger, data, current_map):
    big_rooms = get_biggest_rooms(data, current_map)
    inspector_logger.debug(f"big_rooms ------- {big_rooms}")
    response_index = random.randint(0, len(big_rooms) - 1)
    return response_index
import json
import logging
import os
import random
import socket
from logging.handlers import RotatingFileHandler

import protocol

host = "localhost"
port = 12000
# HEADERSIZE = 10

"""
set up inspector logging
"""
inspector_logger = logging.getLogger()
inspector_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s :: %(levelname)s :: %(message)s", "%H:%M:%S")
# file
if os.path.exists("./logs/inspector.log"):
    os.remove("./logs/inspector.log")
file_handler = RotatingFileHandler('./logs/inspector.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
inspector_logger.addHandler(file_handler)
# stream
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
inspector_logger.addHandler(stream_handler)


class Player():

    def __init__(self):

        self.end = False
        # self.old_question = ""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def connect(self):
        self.socket.connect((host, port))

    def reset(self):
        self.socket.close()

    def get_current_positions(self, game_state):
        current_map = [[], [], [], [], [], [], [], [], [], []]
        for char in game_state["characters"]:
            current_map[char["position"]].append(char["color"])
        return current_map

    def get_people_from_point(self, characters_data, current_map):
        nb_characters = [0] * len(characters_data)
        for i in range(len(characters_data)):
            for case in current_map:
                if characters_data[i]["color"] in case:
                    nb_characters[i] = len(case)
        return nb_characters

    def get_most_isolated_char(self, nb_characters):
        minimum_char = min(nb_characters)
        minimum_indexes = []
        for i in range(len(nb_characters)):
            if nb_characters[i] == minimum_char:
                minimum_indexes.append(i)
        return minimum_indexes

    def get_biggest_room(self, possible_moves, current_map):
        biggest_rooms_index = []
        most_full_room = 0
        for i in range(len(possible_moves)):
            if len(current_map[possible_moves[i]]) > most_full_room:
                most_full_room = len(current_map[possible_moves[i]])
        for i in range(len(possible_moves)):
            if len(current_map[possible_moves[i]]) == most_full_room:
                biggest_rooms_index.append(i)
        return biggest_rooms_index

    def answer(self, question):
        # work
        data = question["data"]
        game_state = question["game state"]
        current_map = self.get_current_positions(game_state)
        inspector_logger.debug("|\n|")
        inspector_logger.debug(f"current-map ------- {current_map}")
        if question["question type"] == "select character":
            nb_characters = self.get_people_from_point(data, current_map)
            minimum_indexes = self.get_most_isolated_char(nb_characters)
            inspector_logger.debug(f"nb_characters ------- {nb_characters}")
            inspector_logger.debug(f"minimum_indexes ----- {minimum_indexes}")
            response_index = random.randint(0, len(minimum_indexes)-1)
        elif question["question type"] == "select position":
            big_rooms = self.get_biggest_room(data, current_map)
            inspector_logger.debug(f"big_rooms ------- {big_rooms}")
            response_index = random.randint(0, len(big_rooms)-1)
        else:
            response_index = random.randint(0, len(data)-1)
        # log
        inspector_logger.debug("inspector answers")
        inspector_logger.debug(f"question type ----- {question['question type']}")
        inspector_logger.debug(f"data -------------- {data}")
        inspector_logger.debug(f"response index ---- {response_index}")
        inspector_logger.debug(f"response ---------- {data[response_index]}")
        return response_index

    def handle_json(self, data):
        data = json.loads(data)
        response = self.answer(data)
        # send back to server
        bytes_data = json.dumps(response).encode("utf-8")
        protocol.send_json(self.socket, bytes_data)

    def run(self):

        self.connect()

        while self.end is not True:
            received_message = protocol.receive_json(self.socket)
            if received_message:
                self.handle_json(received_message)
            else:
                print("no message, finished learning")
                self.end = True


p = Player()

p.run()

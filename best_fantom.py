import json
import logging
import os
import random
import socket
from logging.handlers import RotatingFileHandler

import protocol
from fantom_plays import select_character, select_position, blue_character_power_room, blue_character_power_exit, \
    activate_black_power, activate_white_power, grey_character_power, activate_purple_power, activate_brown_power, \
    brown_character_power, get_current_positions, white_power

host = "localhost"
port = 12000
# HEADERSIZE = 10

"""
set up fantom logging
"""
fantom_logger = logging.getLogger()
fantom_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s :: %(levelname)s :: %(message)s", "%H:%M:%S")
# file
if os.path.exists("./logs/fantom.log"):
    os.remove("./logs/fantom.log")
file_handler = RotatingFileHandler('./logs/fantom.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
fantom_logger.addHandler(file_handler)
# stream
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
fantom_logger.addHandler(stream_handler)


class Player():

    def __init__(self):

        self.end = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.moves = {"select character": select_character, "select position": select_position,
                      "blue character power room": blue_character_power_room,
                      "blue character power exit": blue_character_power_exit,
                      "activate black power": activate_black_power, "activate white power": activate_white_power,
                      "activate purple power": activate_purple_power, "grey character power": grey_character_power,
                      "activate brown power": activate_brown_power, "brown character power": brown_character_power,
                      "white character power move": white_power}

    def connect(self):
        self.socket.connect((host, port))

    def reset(self):
        self.socket.close()

    def answer(self, question):
        # work
        data = question["data"]
        game_state = question["game state"]
        current_map = get_current_positions(game_state)
        fantom_logger.debug("|\n|")
        fantom_logger.debug(f"current-map ------- {current_map}")
        fantom_logger.debug("inspector answers")
        fantom_logger.debug(f"question type ----- {question['question type']}")
        if question["question type"] in self.moves:
            print(question["question type"])
            response_index = self.moves[question["question type"]](fantom_logger, data, current_map, game_state)
        elif "white character power move" in question["question type"]:
            print(question["question type"])
            response_index = self.moves["white character power move"](fantom_logger, data, current_map, game_state)
        else:
            print("random")
            response_index = random.randint(0, len(data) - 1)
        # log
        fantom_logger.debug(f"data -------------- {data}")
        fantom_logger.debug(f"response index ---- {response_index}")
        fantom_logger.debug(f"response ---------- {data[response_index]}")
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

import json
import logging
import os
import random
import socket
from logging.handlers import RotatingFileHandler
from inspector_plays import get_current_positions, select_character,\
    select_position, blue_character_power_room,\
    blue_character_power_exit, activate_black_power, activate_white_power, activate_purple_power, grey_character_power, activate_brown_power, brown_character_power

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
        self.moves = {"select character": select_character, "select position": select_position,
                      "blue character power room": blue_character_power_room,
                      "blue character power exit": blue_character_power_exit,
                      "activate black power": activate_black_power, "activate white power": activate_white_power,
                      "activate purple power": activate_purple_power, "grey character power": grey_character_power, 
                      "activate brown power": activate_brown_power, "brown character power": brown_character_power}

    def connect(self):
        self.socket.connect((host, port))

    def reset(self):
        self.socket.close()

    def answer(self, question):
        # work
        data = question["data"]
        game_state = question["game state"]
        current_map = get_current_positions(game_state)
        inspector_logger.debug("|\n|")
        inspector_logger.debug(f"current-map ------- {current_map}")
        inspector_logger.debug("inspector answers")
        inspector_logger.debug(f"question type ----- {question['question type']}")
        if question["question type"] in self.moves:
            print(question["question type"])
            response_index = self.moves[question["question type"]](inspector_logger, data, current_map)
        else:
            response_index = random.randint(0, len(data)-1)
        # log
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

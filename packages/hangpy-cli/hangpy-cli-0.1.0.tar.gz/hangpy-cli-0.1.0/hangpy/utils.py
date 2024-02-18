from configparser import ConfigParser
from hangpy import hangpy_dir

def gen_config(config: list = False):
    if not config:
        config_file = ConfigParser()
        config_file["Game"] = {
                "lang": "es",
                "word_lang": "es",
                "default_player": "",
            }

        config_file["Player_1"] = {
                "name": "Player 1",
                "points": "0",
            }
        config_file["Player_2"] = {
                "name": "Player 2",
                "points": "0",
            }
        config_file["Player_3"] = {
                "name": "Player 3",
                "points": "0",
            }
        config_file["Player_4"] = {
                "name": "Player 4",
                "points": "0",
            }
        config_file["Player_5"] = {
                "name": "Player 5",
                "points": "0",
            }
    with open(f'{hangpy_dir}/data/config.ini', 'w') as file_object:
        config_file.write(file_object)


def clear():
    from os import system, name
    if name == "nt":
        system("cls")
    else:
        system("clear")

CONFIG = ConfigParser()
CONFIG.read(f"{hangpy_dir}/data/config.ini")
if not CONFIG.sections():
    gen_config()
    CONFIG.read(f"{hangpy_dir}/data/config.ini")

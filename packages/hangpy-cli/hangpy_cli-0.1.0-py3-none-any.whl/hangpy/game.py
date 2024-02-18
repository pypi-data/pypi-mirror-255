from hangpy.ascii_status import *
from hangpy.utils import clear, gen_config, CONFIG
from hangpy.translations import gm
from hangpy import hangpy_dir
from random import choice


def print_lives(lives):
  if 8 > lives > 0:
    print(gm[CONFIG["Game"]["lang"]]["show_lives"], lives)


def get_name():
  while True:
    try:
      name = input(gm[CONFIG["Game"]["lang"]]["ask_name"]).strip()
      
      if len(name) == 0:
        raise ValueError(gm[CONFIG["Game"]["lang"]]["ask_name_er1"])
      
      if len(name) > 15:
        raise ValueError(gm[CONFIG["Game"]["lang"]]["ask_name_er2"])
      
      break

    except ValueError as ve:
      print(ve)
      input(gm[CONFIG["Game"]["lang"]]["enter_continue"])

  return name


def get_guess(chars: list = False):
  while True:
    try:
      c = input(gm[CONFIG["Game"]["lang"]]["get_guess"]).strip()
      if c.isdigit() or not c.isalpha():
        raise ValueError(gm[CONFIG["Game"]["lang"]]["get_guess_er1"])
      if len(c) > 1:
        raise ValueError(gm[CONFIG["Game"]["lang"]]["get_guess_er2"])
      if c.upper() in chars["right"] or c.upper() in chars["wrong"]:
        raise ValueError(gm[CONFIG["Game"]["lang"]]["get_guess_er3"])
      break
    except ValueError as ve:
      print(ve)
  return c.upper()


def print_game_stats(stats):
  print(gm[CONFIG["Game"]["lang"]]["game_stats_1"], end="")
  for char in stats["right"]:
    print(char, end=" ")
  print()
  print(gm[CONFIG["Game"]["lang"]]["game_stats_2"], end="")
  for char in stats["wrong"]:
    print(char, end=" ")
  print('\n')


def save_points(player: str, points: int):
  position = ask_for_top(points)
  if position > 0:
    CONFIG[f'Player_{position}'] = {
      "name": player,
      "score": points
      }
    with open(f'{hangpy_dir}/data/config.ini', 'w') as file_object:
      CONFIG.write(file_object)


def yes_no_qt(msg):
  again = str(input(f"\033[93m\n{msg}\033[0m")).strip().upper()
  awrs = ["S", "Y", "SI", "YES"]
  if again in awrs or len(again) == 0:
    return True
  return False


def ask_for_top(points, print_info = True):
  print('\033[92m', end="")
  try:
    for i in range(1, 6):
      if not CONFIG[f'Player_{i}'] or int(CONFIG[f'Player_{i}']['score']) < points:
        position = i
        break
      else:
        position = 0
    if print_info:
      if position > 0:
        print(gm[CONFIG["Game"]["lang"]]["ask_for_top_1"], position)
      else:
        print(gm[CONFIG["Game"]["lang"]]["ask_for_top_2"])
    return position
  except ValueError:
    print(gm[CONFIG["Game"]["lang"]]["ask_for_top_er_1"])
    print(gm[CONFIG["Game"]["lang"]]["ask_for_top_er_2"])
    gen_config()
    exit(1)


def show_top():
  print('\033[92m')
  print("Top 5 jugadores")
  for i in range(1, 6):
    try:
      print(f"{i}. {CONFIG[f'Player_{i}']['name']} - {CONFIG[f'Player_{i}']['score']}")
    except KeyError:
      print(f"{i}. Vacio")


def get_words(lang):
  try:
    with open(f"{hangpy_dir}/data/dics/{lang}.txt", "r") as f:
      words = f.readlines()
    if words == []:
      print(gm[CONFIG["Game"]["lang"]]["get_words_err_1"], lang)
      exit(1)
    return words
  except FileNotFoundError:
    print(gm[CONFIG["Game"]["lang"]]["get_words_err_2"], lang)
    exit(1)


def print_char_board(word: str, right_chars: list):
  print('\033[94m', end="")
  for char in word:
    if char in right_chars:
      print(char, end=" ")
    else:
      print("_", end=" ")
  print()
        
def main_game(player: str):
  word_dict =  get_words(CONFIG['Game']['word_lang'])
  game_total = {
    "points": 0,
    "guessed_words": 0,
    "word_dict": word_dict,
  }
  is_new_game = True

  # Main game loop
  while True:
    if is_new_game:
      current_game = {
        "lives": 8,
        "word": choice(game_total["word_dict"]).strip().upper(),
        "chars_len": 0,
        "guessed": False,
        "chars": {
            "right": [],
            "wrong": []
        }
      }
      current_game["chars_len"] = len(set(current_game["word"]))
      is_new_game = False


    if 0 < current_game["lives"] <= 8 and not current_game["guessed"]:
      clear()
      print_ascii_state(current_game["lives"])
      print_lives(current_game["lives"])
      print_char_board(current_game["word"], current_game["chars"]["right"])
      print_game_stats(current_game["chars"])
      c = get_guess(current_game["chars"])

      if c in current_game["word"]:
        current_game["chars"]["right"].append(c)

      else:
        current_game["chars"]["wrong"].append(c)
        current_game["lives"] -= 1

      current_game["guessed"] = current_game["chars_len"] == len(current_game["chars"]["right"])


    elif current_game["guessed"]:
        game_total["points"] += current_game["lives"] + 20
        clear()
        print_ascii_state(current_game["lives"], True)
        print(f"\033[92m{player} {gm[CONFIG["Game"]["lang"]]["main_game_1"]} {current_game["word"]}\033[0m")
        print(f"{gm[CONFIG["Game"]["lang"]]["main_game_2"]} {game_total["points"]}\n")
        ask_for_top(game_total["points"])

        if yes_no_qt(gm[CONFIG["Game"]["lang"]["main_game_3"]]):
            is_new_game = True
        
        clear()
    else:
        break
  # End of main game loop

  if current_game["lives"] == 0:
    print_ascii_state(current_game["lives"])
    print(f"\033[95m{gm[CONFIG["Game"]["lang"]]["main_game_4"]} {current_game["word"]}\033[0m")
    print(f"{gm[CONFIG["Game"]["lang"]]["main_game_2"]} {game_total["points"]}\n")  
  save_points(player, game_total["points"])
  input(gm[CONFIG["Game"]["lang"]]["enter_continue"])

  clear()
  print_game_over()


def start_game():
  clear()
  print_title()
  print(gm[CONFIG["Game"]["lang"]]["hangpy"])
  name = ""
  if CONFIG["Game"]["default_player"]:
    if yes_no_qt(f"{gm[CONFIG['Game']['lang']]['start_game']} {CONFIG['Game']['default_player']} ? "):
      name = CONFIG["Game"]["default_player"]
  if not name:
    name = get_name()
    CONFIG["Game"]["default_player"] = name
    with open(f'{hangpy_dir}/data/config.ini', 'w') as file_object:
      CONFIG.write(file_object)
  clear()
  main_game(name)


def get_desire_lang():
  try:
    lang = input(gm[CONFIG["Game"]["lang"]]["get_desired_lang"]).strip()
    if not lang.isalpha() or lang.upper() not in ["ES", "EN"]:
      raise ValueError(gm[CONFIG["Game"]["lang"]]["get_desired_lang_er"])
    return lang.lower()
  except ValueError as ve:
    print(ve)
    exit(1)


def configure_game():
  print(gm[CONFIG["Game"]["lang"]]["configure_game_1"])
  print(f"{gm[CONFIG['Game']['lang']]['configure_game_2']} {CONFIG['Game']['lang']}")
  print(f"{gm[CONFIG['Game']['lang']]['configure_game_3']} {CONFIG['Game']['word_lang']}")
  choice = input("\033[94m\n[1/2] \033[0m")
  if choice == "1":
    lang = get_desire_lang()
    CONFIG["Game"]["lang"] = lang
    with open(f'{hangpy_dir}/data/config.ini', 'w') as file_object:
      CONFIG.write(file_object)
    print(gm[CONFIG["Game"]["lang"]]["configure_game_4"])
  elif choice == "2":
    lang = get_desire_lang()
    CONFIG["Game"]["word_lang"] = lang
    with open(f'{hangpy_dir}/data/config.ini', 'w') as file_object:
      CONFIG.write(file_object)
    print(gm[CONFIG["Game"]["lang"]]["configure_game_4"])
  else:
    print(gm[CONFIG["Game"]["lang"]]["configure_game_5"])
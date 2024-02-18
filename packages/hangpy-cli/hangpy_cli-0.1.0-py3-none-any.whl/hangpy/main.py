from hangpy.game import start_game, show_top, configure_game
from hangpy.utils import clear
import argparse

def run():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("-c", "--config", help="Configure game settings", action="store_true")
        parser.add_argument("-t", "--top", help="Show top 5 players", action="store_true")
        args = parser.parse_args()
        if args.config:
            configure_game()
        elif args.top:
            show_top()
        else:
            start_game()

    except KeyboardInterrupt:
        clear()
        print("\033[91mBye!\033[0m")


if __name__ == '__main__':
    run()

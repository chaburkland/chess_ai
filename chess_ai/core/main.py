import argparse

from chess_ai.core.Game.game import Game
from chess_ai.core.Game.board import Board
from chess_ai.core.Utils.pgn_parser import Parser
from chess_ai.test import get_input


def main():
    game = Game()

    parser = Parser.from_pgn(get_input.get('length8848.5.pgn'))

    try:
        game.start_game(parser)
    except EOFError:
        print('Game forcefully quit!')
    finally:
        del game


if __name__ == '__main__':
    main()

import argparse

from chess_ai.core.Game.game import Game
from chess_ai.core.Game.board import Board


def main():
    game = Game()

    initial_moves = None#[
    #         ('F2', 'F3'),
    #         ('E7', 'E5'),
    #         ('G2', 'G4'),
    #         ('D8', 'H4'),
    # ]

    try:
        game.start_game(initial_moves)
    except EOFError:
        print('Game forcefully quit!')
    finally:
        del game


if __name__ == '__main__':
    main()

import os
from pytest import main, mark

from chess_ai.core.Game.game import Game
from chess_ai.core.Mechanics.status import Status
from chess_ai.core.Utils.pgn_parser import Parser
from chess_ai.test import get_input


from pyinstrument import Profiler


def test_fools_game_direct_moves():
    game = Game()

    initial_moves = [
            ('F2', 'F3'),
            ('E7', 'E5'),
            ('G2', 'G4'),
            ('D8', 'H4'),
    ]

    game_status, competitive_ending = game.start_game(initial_moves)

    assert game_status == Status.Checkmate
    assert competitive_ending.value is None


def test_fools_game_parser():
    game = Game()
    parser = Parser.from_fools_mate()

    game_status, competitive_ending = game.start_game(parser)

    assert game_status == Status.Checkmate
    assert competitive_ending.value is None


def test_game_from_parser_a():
    game = Game()
    parser = Parser.from_sample_games('one')

    game_status, competitive_ending = game.start_game(parser)

    assert game_status == Status.Checkmate
    assert competitive_ending.value is None

def test_game_from_parser_b():
    game = Game()
    parser = Parser.from_pgn(get_input.get('raphael_hiaves_2006.pgn'))

    game_status, competitive_ending = game.start_game(parser)

    assert game_status == Status.Checkmate
    assert competitive_ending.value is None


if __name__ == '__main__':
    #main()

    test_game_from_parser_b()
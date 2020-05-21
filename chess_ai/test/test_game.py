from pytest import main

from chess_ai.core.Game.game import Game
from chess_ai.core.Mechanics.status import Status

def test_fools_game():
    game = Game()

    initial_moves = [
            ('F2', 'F3'),
            ('E7', 'E5'),
            ('G2', 'G4'),
            ('D8', 'H4'),
    ]

    game_status, competitive_ending = game.start_game(initial_moves)

    assert game_status == Status.Checkmate
    assert competitive_ending is None


if __name__ == '__main__':
    main()
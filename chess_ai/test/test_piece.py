from pytest import main

from chess_ai.core.Utils.reference import Ref
from chess_ai.core.Game.board import Board
from chess_ai.core.Pieces.piece import Piece, Empty, King, Queen, Rook, Knight, Bishop, Pawn
from chess_ai.core.Mechanics.color import Color

class BoardTester(Board):
    def __init__(self):
        self.move_exposes_king_result = False

    def move_exposes_king(self, piece, move, color):
        return self.move_exposes_king_result


class PieceTester(Piece):
    def __init__(self, color, board, pos):
        super.__init__(color, board, pos)
        self.can_attack_result = False

    def can_attack(self, p):
        return self.can_attack_result

    def get_all_valid_moves(self):
        return []


def test_constructor():
    p = PieceTester(Color.White, None, Point())
    assert p.is_first_move

def perform_move():
    piece = PieceTester(Color.White, None, Point(1, 1))
    en_passant =  Ref(Point(1, 1))
    piece.perform_move(Point(3, 4), en_passant)

    assert not piece.is_first_move
    assert p.pos == Point(3, 4)
    assert en_passant() == Point()

def test_is_valid_move():
    b = BoardTester()
    p = PieceTester(Color.White, b, Point())

    # If piece cannot attack is always an invalid move
    p.can_attack_result = False
    assert not p.is_valid_move(Point())

    # If piece can attack the result is the negation of the board's call to move_exposes_king
    p.can_attack_result = True
    b.move_exposes_king_result = True
    assert p.is_valid_move(Point()) != b.move_exposes_king(p, Point(), p.color)

    b.move_exposes_king_result = False
    assert p.is_valid_move(Point()) != b.move_exposes_king(p, Point(), p.color)

def test_can_move_horizontally_to_empty_space():
    b = BoardTester()
    p = PieceTester(Color.White, b, Point(4, 4))

    assert p._can_move_horizontally_to(0)

    for i in range(1, 8):
        if i == 4:
            continue
        assert p._can_move_horizontally_to(i)

def test_can_move_horizontally_to_enemy_piece():
    b = Board()
    p = PieceTester(Color.White, b, Point(4, 4))

    b.perform_move(b[6, 2], Point(4, 2))
    assert p._can_move_horizontally_to(2)

    b.perform_move(b[7, 7], Point(4, 7))
    assert p._can_move_horizontally_to(7)

def test_can_not_move_horizontally_to_invalid_space():
    b = BoardTester()
    p = PieceTester(Color.White, b, Point(4, 4))

    assert not p._can_move_horizontally_to(-1)
    assert not p._can_move_horizontally_to(8)

def test_can_not_move_horizontally_to_team_piece():
    b = Board()
    p = PieceTester(Color.White, b, Point(4, 4))

    b.perform_move(b[1, 1], Point(4, 1))
    assert not p._can_move_horizontally_to(1)

    b.perform_move(b[1, 7], Point(4, 7))
    assert not p._can_move_horizontally_to(7)

def can_move_vertically_to_empty_space():
    b = Board()
    p = PieceTester(Color.White, b, Point(4, 4))
    b.remove_piece((0, 4))
    b.remove_piece((1, 4))
    b.remove_piece((6, 4))
    b.remove_piece((7, 4))

    assert p._can_move_vertically_to(0)
    for i in range(1, 8):
        if i == 4:
            continue

        assert p._can_move_vertically_to(i)

def test_can_move_vertically_to_enemy_piece():
    b = Board()
    p = PieceTester(Color.White, b, Point(4, 4))

    assert p._can_move_vertically_to(6)
    b.perform_move(b[7, 7], Point(2, 4))
    assert p._can_move_vertically_to(2))

def test_can_not_move_vertically_to_invalid_space():
    b = Board()
    p = PieceTester(Color.White, b, Point(4, 4))

    assert not p._can_move_vertically_to(-1)
    assert not p._can_move_vertically_to(8)

def test_can_not_move_vertically_to_team_piece():
    b = Board()
    p = PieceTester(Color.White, b, Point(4, 4))

    assert not p._can_move_vertically_to(1)
    b.perform_move(b[0, 0], Point(5, 4))
    assert not p._can_move_vertically_to(5)


if __name__ == '__main__':
    main()
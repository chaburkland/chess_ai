import typing as tp
from collections import namedtuple
from itertools import product

from chess_ai.core.Pieces.piece import Piece, Pawn, PieceType
from chess_ai.core.Mechanics.color import Color
from chess_ai.core.Mechanics.point import Point


MovePair = namedtuple('MovePair', ('start', 'end'))
TeamMovePair = namedtuple('TeamMovePair', ('move_pair', 'color'))


class Screenshot:
    '''
    A lightweight class containing minimal information about the state of a chessboard
    '''
    @classmethod
    def from_board(cls, board: 'Board') -> 'Screenshot':

        moves: tp.List[TeamMovePair] = []
        total_pieces = 0
        pawn_locations: tp.List[Point] = []

        for row, col in product(range(8), range(8)):
            piece: Piece = board[row, col]

            if piece is not None:

                valid_moves = piece.get_all_valid_moves()

                for move in valid_moves:
                    moves.append(TeamMovePair(MovePair(Point(row, col), move), piece.color))

                total_pieces += 1

                if piece.piece_type == PieceType.Pawn:
                    pawn_locations.append(piece.pos)

        return cls(moves, board.white_score, board.black_score, pawn_locations, total_pieces)

    def __init__(self,
            moves: tp.List[TeamMovePair],
            white_score: float,
            black_score: float,
            pawn_locations: tp.List[Point],
            total_pieces: int
        ):
        self.moves: tp.List[TeamMovePair] = moves
        self.white_score: float = white_score
        self.black_score: float = black_score
        self.pawn_locations: tp.List[Point] = pawn_locations
        self.total_pieces: int = total_pieces

    def compare_available_moves(self, other: 'Screenshot') -> bool:
        '''
        Checks equivelancy between two screenshots. Every possible move between the two must be the same for them to be considered equal.
        '''

        if len(self.moves) != len(other.moves):
            return False

        for i in range(len(self.moves)):
            if ((other.moves[i].move_pair.start != self.moves[i].move_pair.start) or
                    (other.moves[i].move_pair.end != self.moves[i].move_pair.end)):
                return False

        return True

    def compare_pawn_locations(self, other: 'Screenshot') -> bool:
        '''
        Compares the location of the pawns between two screenshots
        '''
        if len(other.pawn_locations) != len(self.pawn_locations):
            return False

        for i in range(len(self.pawn_locations)):
            if other.pawn_locations[i] != self.pawn_locations[i]:
                return False

        return True

    def compare_piece_count(self, other: 'Screenshot') -> bool:
        '''
        Compares the location of the pawns between two screenshots
        '''
        return self.total_pieces == other.total_pieces

    def get_score(self, color: Color) -> float:
        '''
        Gets the score of the current board for a given team
        '''
        if color == Color.White:
            return self.white_score
        return self.black_score

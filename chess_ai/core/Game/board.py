import static_frame as sf
import numpy as np
from itertools import product
import typing as tp

from chess_ai.core.Pieces.piece import Queen, King, Pawn, Rook, Knight, Bishop, Empty, Piece
from chess_ai.core.Mechanics.color import Color, get_opposite_color
from chess_ai.core.Mechanics.point import Point, check_bounds
from chess_ai.core.Mechanics.status import Status
from chess_ai.core.Utils.reference import Ref
from chess_ai.core.Game.screenshot import Screenshot

from colorama import init as colorama_init
from colorama import Back, Fore, Style
from termcolor import colored
colorama_init(autoreset=True)


BOARD_STR = '''
     A  |  B  |  C  |  D  |  E  |  F  |  G  |  H  |
  -------------------------------------------------
1 |     |     |     |     |     |     |     |     |
  -------------------------------------------------
2 |     |     |     |     |     |     |     |     |
  -------------------------------------------------
3 |     |     |     |     |     |     |     |     |
  -------------------------------------------------
4 |     |     |     |     |     |     |     |     |
  -------------------------------------------------
5 |     |     |     |     |     |     |     |     |
  -------------------------------------------------
6 |     |     |     |     |     |     |     |     |
  -------------------------------------------------
7 |     |     |     |     |     |     |     |     |
  -------------------------------------------------
8 |     |     |     |     |     |     |     |     |
  -------------------------------------------------
'''



class Board:
    COL_MAP = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H'}

    def _gen_board(self):
        _board = np.full((8, 8), fill_value=Empty)
        for row, col in product(range(8), range(8)):
            color = Color.White if row <= 1 else Color.Black

            piece = Empty
            king = None

            if row == 0 or row == 7:
                if col == 0 or col == 7:
                    piece = Rook(color, self, Point(row, col))
                elif col == 1 or col == 6:
                    piece = Knight(color ,self, Point(row, col))
                elif col == 2 or col == 5:
                    piece = Bishop(color, self, Point(row, col))
                elif col == 3:
                    piece= Queen(color, self, Point(row, col))
                else:
                    piece = King(color, self, Point(row, col))
                    king = piece
            elif row == 1 or row == 6:
                piece = Pawn(color, self, Point(row, col))

            if piece is not Empty:
                if color == Color.White:
                    self._white_team.add(piece)
                    if king is not None:
                        self._white_king = king
                else:
                    self._black_team.add(piece)
                    if king is not None:
                        self._black_king = king

                _board[row, col] = piece

        return sf.Frame.from_records(_board, columns=tuple('ABCDEFGH'))

    def __init__(self):
        self._enpassant_location: Ref[Point] = Ref(Point())
        self._white_team = set()
        self._black_team = set()
        self._white_king = None
        self._black_king = None

        self._board: sf.Frame = self._gen_board()

        self.white_score: float = 0.0
        self.black_score: float = 0.0

    @property
    def screenshot(self):
        return Screenshot.from_board(self)

    def _key_to_call(self, key):
        if isinstance(key, Point):
            row = key.x
            col = key.y
        elif isinstance(key, tuple):
            if len(key) != 2:
                raise KeyError('Unknown key type')

            if not isinstance(key[0], int):
                raise KeyError('Unknown key type')

            row, col = key

        elif isinstance(key, str):
            row = int(key[1]) - 1
            col = Point.KEY_MAP[key[0]]
        else:
            raise KeyError('Unknown key type')

        if check_bounds(row) and check_bounds(col):
            return row, col
        return None

    # @property
    # def iloc(self):
    #     class ILocInterface:
    #         def __init__(self, frame):
    #             self.frame = frame

    #         def __getitem__(self, key):
    #             return self.frame.iloc[key[0]-1, key[0]-1]

    #     return ILocInterface(self._board)

    def __getitem__(self, key):
        key = self._key_to_call(key)
        if key is None:
            return Empty
        return self._board.iloc[key]

    def remove_piece(self, key):
        key = self._key_to_call(key)
        if key is not None:
            piece = self._board.iloc[key]
            if piece is not Empty:
                self.get_team(piece.color).remove(piece)
                self._board = self._board.assign.iloc[key](Empty)
                del piece

    def get_king(self, color: Color) -> King:
        if color == color.White:
            return self._white_king
        return self._black_king

    def get_team(self, color: Color) -> tp.Set[Piece]:
        if color == Color.White:
            return self._white_team
        return self._black_team

    def is_enpassant(self, p: Point) -> bool:
        '''Checks if a given location is subject to en passant'''
        return self._enpassant_location() == p

    def is_attackable(self, p: Point, opposing_color: Color) -> bool:
        for enemy in self.get_team(opposing_color):
            if enemy.can_attack(p):
                return True
        return False

    def move_exposes_king(self, piece: Piece, move: Point, color: Color) -> bool:
        piece_x = piece.pos.x
        piece_y = piece.pos.y
        move_x = move.x
        move_y = move.y

        # Temporarily move piece
        original_occupant = self._board.iloc[move_x, move_y]
        self._board = self._board.assign.iloc[piece_x, piece_y](Empty)
        self._board = self._board.assign.iloc[move_x, move_y](piece)

        king_pos = self.get_king(color).pos

        king_exposed = False
        for enemy in self.get_team(get_opposite_color(color)):
            # Ignore the potential attack of a piece that might be removed
            if enemy.can_attack(king_pos) and enemy.pos != move:
                king_exposed = True
                break

        # Put piece back
        self._board = self._board.assign.iloc[piece_x, piece_y](piece)
        self._board = self._board.assign.iloc[move_x, move_y](original_occupant)

        return king_exposed

    def get_board_status(self, color: Color) -> Status:
        total_moves = 0

        # If any piece has a valid move, the game is in progress
        for piece in self.get_team(color):
            if len(piece.get_all_valid_moves()) > 0:
                return Status.InProgress

        # No moves + check = checkmate
        if self.get_king(color).in_check:
            return Status.Checkmate

        # No moves without check = stalemate
        return Status.Stalemate

    def perform_move(self, piece: Piece, to: Point, default_promotion=False):
        starting_pos = piece.pos

        # Update piece's internal state
        piece.perform_move(to, self._enpassant_location)

        # Move piece on board
        self.remove_piece(to)
        self._board = self._board.assign.iloc[to.x, to.y](piece)

        # Clear starting loction
        self._board = self._board.assign.iloc[starting_pos.x, starting_pos.y](Empty)

        # Check for pawn promotion
        if isinstance(piece, Pawn):
            color = piece.color
            if ((color == Color.White and to.x == 7) or
                (color == Color.Black and to.x == 0)):

                if default_promotion:
                    new_piece = Queen(color, self, to)
                else:
                    print('Congratulations! Pawn reached promotion row.')
                    promote_type = input('Please enter desired promotion: ')

                    if promote_type in ('Q', 'q', 'Qu', 'qu', 'Queen', 'queen'):
                        new_piece = Queen(color, self, to)
                    elif promote_type in ('R', 'r', 'Ro', 'ro', 'Rook', 'rook'):
                        new_piece = Rook(color, self, to)
                    elif promote_type in ('K', 'k', 'Kn', 'kn', 'Knigh', 'knight'):
                        new_piece = Queen(color, self, to)
                    elif promote_type in ('Q', 'q', 'Queen', 'queen'):
                        new_piece = Queen(color, self, to)
                    else:
                        print(f"Unknown promotion '{promote_type}'. Defaulting to a new Queen.")
                        new_piece = Queen(color, self, to)

                self._board = self._board.assign.iloc[to.x, to.y](new_piece)

                self.get_team(color).remove(piece)
                self.get_team(color).add(new_piece)
                del piece

        self._update_check_state()

    def _update_check_state(self):
        def upddate_team_check_state(color):
            enemy_king = self.get_king(get_opposite_color(color))
            team = self.get_team(color)
            in_check = False

            for piece in team:
                if piece.can_attack(enemy_king.pos):
                    in_check = True
                    break
            enemy_king.in_check = in_check

        upddate_team_check_state(Color.White)
        upddate_team_check_state(Color.Black)

    def _repr(self):
        s = BOARD_STR
        row_width = 52
        row_offset = 2
        col_offset = 4
        col_width = 6
        bloat = 0

        def update_s(row: int, col: int, val: str):
            nonlocal bloat
            val = f' {val} '

            if val[1] == 'w':
                val = colored(val, 'yellow', attrs=['bold'])
            else:
                val = colored(val, 'blue', attrs=['bold'])

            i = (row_width * (row_offset + row * 2)) + col_offset + (col_width * col) + bloat
            bloat += len(val) - 5
            return s[:i] + val + s[i + 5:]

        for i, j in product(range(8), range(8)):
            s = update_s(i, j, str(self._board.iloc[i, j]))

        return s

    def __repr__(self):
        return self._repr()

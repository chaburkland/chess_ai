import static_frame as sf
import numpy as np
from itertools import product
import typing as tp

from chess_ai.core.Pieces.piece import Queen, King, Pawn, Rook, Knight, Bishop, Piece, PieceType
from chess_ai.core.Mechanics.color import Color, get_opposite_color
from chess_ai.core.Mechanics.point import Point, check_bounds
from chess_ai.core.Mechanics.status import Status
from chess_ai.core.Mechanics.move import Move, Castle
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
        _board = np.full((8, 8), fill_value=None)

        for row, col in product(range(8), range(8)):
            color = Color.White if row <= 1 else Color.Black

            piece = None

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
            elif row == 1 or row == 6:
                piece = Pawn(color, self, Point(row, col))

            if piece is not None:
                if piece.piece_type == PieceType.King:
                    self._kings[color] = piece
                else:
                    self._pieces[color][piece.piece_type].add(piece)

                _board[row, col] = piece

        return sf.Frame.from_records(_board, columns=tuple('ABCDEFGH'))

    def __init__(self):
        self._enpassant_location: Ref[Point] = Ref(Point())

        self._kings: tp.Dict[Color, King] = {}

        self._pieces: tp.Dict[Color, tp.Dict[PieceType, tp.Set[Piece]]] = {}
        for color in Color:
            piece_collection: tp.Dict[PieceType, tp.Set[Piece]] = {}
            for piece_type in (pt for pt in PieceType if pt != PieceType.King):
                piece_collection[piece_type] = set()
            self._pieces[color] = piece_collection

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


    def _find_target_piece(self, move: Move) -> Piece:

        row = move.row_helper - 1 if move.row_helper is not None else None
        col = Point.KEY_MAP[move.col_helper] if move.col_helper is not None else None

        for piece in self._pieces[move.color][move.piece]:
            if col is None and row is None and piece.can_attack(move.destination):
                return piece
            elif col is not None and row is None:
                if piece.pos.y == col and piece.can_attack(move.destination):
                    return piece
            elif col is None and row is not None:
                if piece.pos.x == row and piece.can_attack(move.destination):
                    return piece
            else:
                if piece.pos == Point(row, col) and piece.can_attack(move.destination):
                    return piece

        breakpoint()
        raise RuntimeError(f'No target found for move: {move}')


    def parse_points_from_move(self, move: Move) -> tp.Tuple[Piece, Point, tp.Optional[PieceType]]:

        if move.piece == PieceType.King:
            king = self.get_king(move.color)

            if move.castle in (Castle.Queenside, Castle.Kingside):
                direction = 2 if Castle.Kingside else -2
                return king, Point(king.pos.x, king.pos.y + direction), None

            return king, move.destination, None

        else:
            target = self._find_target_piece(move)
            return target, move.destination, move.upgrade

    def __getitem__(self, key) -> tp.Optional[Piece]:
        key = self._key_to_call(key)
        if key is None:
            return None
        return self._board.iloc[key]

    def remove_piece(self, key):
        key = self._key_to_call(key)
        if key is not None:
            piece = self._board.iloc[key]
            if piece is not None:
                self._pieces[piece.color][piece.piece_type].remove(piece)
                self._board = self._board.assign.iloc[key](None)
                del piece

    def get_king(self, color: Color) -> King:
        return self._kings[color]

    def get_team(self, color: Color) -> tp.Set[Piece]:
        team: tp.Set[Piece] = set()
        for collection in self._pieces[color].values():
            team.update(collection)
        return team | {self._kings[color]}

    def is_enpassant(self, p: Point) -> bool:
        '''Checks if a given location is subject to en passant'''
        return self._enpassant_location() == p

    def is_attackable(self, p: Point, opposing_color: Color) -> bool:
        for enemy in self.get_team(opposing_color):
            if enemy.can_attack(p, ignore_color=True):
                return True
        return False

    def move_exposes_king(self, piece: Piece, move: Point, color: Color) -> bool:
        piece_x = piece.pos.x
        piece_y = piece.pos.y
        move_x = move.x
        move_y = move.y

        # Temporarily move piece
        original_occupant = self._board.iloc[move_x, move_y]
        self._board = self._board.assign.iloc[piece_x, piece_y](None)
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

    def perform_move(self, piece: Piece, to: Point, promotion: tp.Optional[PieceType] = None):
        starting_pos = piece.pos
        en_passant_start = self._enpassant_location.value

        # Update piece's internal state
        piece.perform_move(to, self._enpassant_location)

        # Move piece on board
        self.remove_piece(to)
        self._board = self._board.assign.iloc[to.x, to.y](piece)

        # Clear starting loction
        self._board = self._board.assign.iloc[starting_pos.x, starting_pos.y](None)

        x_movement = to.x - starting_pos.x
        y_movement = to.y - starting_pos.y

        # A castle was performed!
        if piece.piece_type == PieceType.King and abs(y_movement) == 2:
            x = piece.pos.x
            if y_movement > 0:
                rook_pos_y = 7
                rook_to_y = 5
            else:
                rook_pos_y = 0
                rook_to_y = 3

            rook_pos = Point(x, rook_pos_y)
            rook_to = Point(x, rook_to_y)
            rook = self[rook_pos]

            rook.perform_move(rook_to, self._enpassant_location)

            self.remove_piece(rook_to)
            self._board = self._board.assign.iloc[x, rook_to_y](rook)
            self._board = self._board.assign.iloc[x, rook_pos_y](None)

        # An en passant was performed!
        if piece.piece_type == PieceType.Pawn and to == en_passant_start:
            self.remove_piece((starting_pos.x, to.y))


        # Check for pawn promotion
        if piece.piece_type == PieceType.Pawn:
            color = piece.color
            if ((color == Color.White and to.x == 7) or
                (color == Color.Black and to.x == 0)):

                if promotion is not None:
                    new_piece = Piece.from_piece_type(promotion, color, self, to)
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

                self._pieces[color][piece.piece_type].remove(piece)
                self._pieces[color][new_piece.piece_type].add(new_piece)
                del piece

        self._update_check_state()

    def invalidate_cache(self):
        for piece in self.get_team(Color.White):
            piece.invalidate_cache()

        for piece in self.get_team(Color.Black):
            piece.invalidate_cache()

    def _update_check_state(self):
        def update_team_check_state(color):
            enemy_king = self.get_king(get_opposite_color(color))
            in_check = False

            for piece in self.get_team(color):
                if piece.can_attack(enemy_king.pos):
                    in_check = True
                    break
            enemy_king.in_check = in_check

        update_team_check_state(Color.White)
        update_team_check_state(Color.Black)

    def __repr__(self) -> str:
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
            piece = self._board.iloc[i, j]
            if piece is not None:
                s = update_s(i, j, str(piece))

        return s
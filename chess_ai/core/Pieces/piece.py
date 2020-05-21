from abc import abstractclassmethod
import typing as tp
from itertools import product

from chess_ai.core.Utils.reference import Ref
from chess_ai.core.Mechanics.color import Color, get_opposite_color
from chess_ai.core.Mechanics.point import Point, check_bounds

from termcolor import colored


BAR = '-----'


class _Empty:
    def __repr__(self):
        return '   '

Empty = _Empty()


class Piece:
    color: Color
    _board: 'Board'
    _pos: Point
    _is_first_move: bool

    def __init__(self, color: Color, board: 'Board', pos: Point):
        self.color: Color = color
        self._board: 'Board' = board
        self._pos: Point = pos
        self._is_first_move: bool = True

    @abstractclassmethod
    def can_attack(self, pos: Point) -> bool:
        raise NotImplementedError()

    def try_attack_from(self, try_from: Point, attack_to: Point) -> bool:
        '''
        Attemps to see if a piece can attack antoher piece given an arbitrary staring location
        '''
        original_pos = self._pos
        self._pos = try_from # Pretend to be in a different location

        can_attack = self.can_attack(attack_to)

        self._pos = original_pos # Restore original state

        return can_attack

    def is_valid_move(self, pos: Point) -> bool:
        if not self.can_attack(pos):
            return False
        return not self._board.move_exposes_king(self, pos, self.color)

    def perform_move(self, to: Point, en_passant: Ref[Point]):
        '''
        Updates piece's internal state to reflect move. Do before changing actual board!

        Callers must remember to reset en_passant
        '''
        if self._is_first_move:
            self._is_first_move = False
        self._pos = to

        en_passant.update(Point())

    @abstractclassmethod
    def get_all_valid_moves(self) -> tp.List[Point]:
        raise NotImplementedError()

    @property
    def is_first_move(self) -> bool:
        return self._is_first_move

    @property
    def pos(self) -> Point:
        return self._pos

    def _can_move_horizontally_to(self, to: int) -> bool:
        if self._check_illegal_move(Point(self._pos.x, to)):
            return False

        me_x = self._pos.x
        me_y = self._pos.y
        direction = 1 if to > me_y else -1 # 1 = right, -1 = left
        col = me_y + direction # Move one space away as starting square

        # Keep advancing along empty spaces until end is hit
        while col != to:
            if self._board[me_x, col] is not Empty:
                return False
            col += direction

        return True

    def _can_move_vertically_to(self, to: int) -> bool:
        if self._check_illegal_move(Point(to, self._pos.y)):
            return False

        me_x = self._pos.x
        me_y = self._pos.y
        direction = 1 if to > me_x else -1 # 1 = down, -1 = up
        row = me_x + direction # Move one space away as starting square

        # Keep advancing along empty spaces until end is hit
        while row != to:
            if self._board[row, me_y] is not Empty:
                return False
            row += direction

        return True

    def _can_move_diagonally_to(self, to: Point) -> bool:
        if self._check_illegal_move(to):
            return False

        me_x = self._pos.x
        me_y = self._pos.y

        x_direction = 1 if to.x > me_x else -1
        y_direction = 1 if to.y > me_y else -1

        # Move one space away as starting square
        row = me_x + x_direction
        col = me_y + y_direction

        # Keep advancing along empty spaces until end is hit
        while not to.equals(row, col):
            if self._board[row, col] is not Empty:
                return False
            row += x_direction
            col += y_direction

        return True

    def _check_illegal_move(self, to: Point) -> bool:
        # Cannot move outisde board or to same spot
        if not to.is_valid() or self._pos == to:
            return True

        # Cannot move to teammate spot
        actual_piece = self._board[to]
        if actual_piece is not Empty and actual_piece.color == self.color:
            return True

        return False

    def __repr__(self) -> str:
        return self.color.value[0].lower() + self.__class__.__name__[:2]

class Queen(Piece):
    def can_attack(self, pos: Point) -> bool:
        if self._check_illegal_move(pos):
            return False

        me_x = self.pos.x
        me_y = self.pos.y
        to_x = pos.x
        to_y = pos.y
        v_distance = me_x - to_x
        h_distance = me_y - to_y

        if v_distance == 0:
            return self._can_move_horizontally_to(to_y)

        if h_distance == 0:
            return self._can_move_vertically_to(to_x)

        if v_distance == h_distance or v_distance + h_distance == 0:
            return self._can_move_diagonally_to(pos)

        return False

    def get_all_valid_moves(self) -> tp.List[Point]:
        moves = []
        for row, col in product(range(8), range(8)):
            move = Point(row, col)
            if self.is_valid_move(move):
                moves.append(move)
        return moves


class King(Piece):
    def __init__(self, color: Color, board: 'Board', pos: Point):
        super().__init__(color, board, pos)
        self.in_check = False

    def is_valid_move(self, pos: Point) -> bool:
        if not self.can_attack(pos):
            return False

        # Cannot move into check
        return not self._board.is_attackable(pos, get_opposite_color(self.color))

    def can_attack(self, pos: Point) -> bool:
        if self._check_illegal_move(pos):
            return False

        me_x = self.pos.x
        me_y = self.pos.y
        to_x = pos.x
        to_y = pos.y
        v_distance = abs(me_x - to_x)
        h_distance = abs(me_y - to_y)

        # Check if standard move
        if ((v_distance == 0 and h_distance == 1) or
                (v_distance == 1 and h_distance == 0) or
                (v_distance == 1 and h_distance == 1)):
            return True

        # Castling is illegal if the king has already moved
        if not self._is_first_move:
            return False

        # A castle is a horizontal movement by the king 2 spaces over
        if v_distance > 0 or h_distance != 2:
            return False

        # Castling left
        if (to_y == 2 and
                self._board[me_x, 0] is not Empty and self._board[me_x, 0].is_first_move and  # Col A rook hasn't moved yet
                self._board[me_x, 1] is Empty and                                             # Col B in first row is unoccupied
                self._board[me_x, 2] is Empty and                                             # Col C in first row is unoccupied
                self._board[me_x, 3] is Empty):                                               # Col D in first row is unoccupied
            return True

        # Castling right
        if (to_y == 6 and
                self._board[me_x, 7] is not Empty and self._board[me_x, 7].is_first_move and  # Col H rook hasn't moved yet
                self._board[me_x, 6] is Empty and                                             # Col G in first row is unoccupied
                self._board[me_x, 5] is Empty):                                               # Col F in first row is unoccupied
            return True

        # Any other option is illegal
        return False

    def get_all_valid_moves(self) -> tp.List[Point]:
        moves = []

        x = self.pos.x
        y = self.pos.y

        for row, col in product(range(-1, 2), range(-1, 2)):
            move = Point(x + row, y + col)
            if self.is_valid_move(move):
                moves.append(move)

        # Check potential castle moves
        if self._is_first_move:
            row = 0 if self.color == Color.White else 7

            move_left = Point(row, 3)
            move_right = Point(row, 6)

            if self.is_valid_move(move_left):
                moves.append(move_left)

            if self.is_valid_move(move_right):
                moves.append(move_right)

        return moves

class Pawn(Piece):
    def can_attack(self, pos: Point) -> bool:
        if self._check_illegal_move(pos):
            return False

        x = pos.x
        y = pos.y
        v_distance = x - self.pos.x
        h_distance = y - self.pos.y

        if abs(h_distance) > 1 or abs(v_distance) > 2:
            return False

        # Ensure direction is correct
        if self.color == Color.White and v_distance < 0:
            return False
        elif self.color == Color.Black and v_distance > 0:
            return False

        to_attack = self._board[x, y]

        # Check forward 1 space is vacant
        if abs(v_distance) == 1 and abs(h_distance) == 0:
            return to_attack is Empty

        # Check forward 2 spaces is vacant if first move
        if self._is_first_move and abs(v_distance) == 2 and abs(h_distance) == 0:
            return to_attack is Empty

        # Check left/right attack and en passant
        if abs(v_distance) == 1 and abs(h_distance) == 1:
            if self._board.is_enpassant(pos) and to_attack is Empty:
                return True

            if to_attack is not Empty:
                return True

        return False

    def perform_move(self, to: Point, en_passant: Ref[Point]):
        piece_x = self.pos.x
        to_x = to.x
        to_y = to.y

        new_en_passant = Point()

        # If double-step, any existing en passant was effectively ignored and a new en passant is in effect
        if abs(piece_x - to_x) == 2:
            direction = -1 if piece_x > to_x else 1

            new_en_passant = Point(piece_x + direction, to_y)
        else:
            if to == en_passant():
                self._board.remove_piece((piece_x, to_y))

        super().perform_move(to, en_passant)
        en_passant.update(new_en_passant)

    def get_all_valid_moves(self) -> tp.List[Point]:
        moves = []
        x = self.pos.x
        y = self.pos.y
        direction = 1 if self.color == Color.White else -1

        possible_moves = [Point(x + direction, y),
                          Point(x + 2 * direction, y),
                          Point(x + direction, y - 1),
                          Point(x + direction, y + 1)]

        for move in possible_moves:
            if self.is_valid_move(move):
                moves.append(move)
        return moves


class Rook(Piece):
    def can_attack(self, pos: Point) -> bool:
        if self._check_illegal_move(pos):
            return False

        me_x = self.pos.x
        me_y = self.pos.y
        to_x = pos.x
        to_y = pos.y
        v_distance = me_x - to_x
        h_distance = me_y - to_y

        if v_distance == 0:
            return self._can_move_horizontally_to(to_y)

        if h_distance == 0:
            return self._can_move_vertically_to(to_x)

        return False

    def get_all_valid_moves(self) -> tp.List[Point]:
        moves = []

        x = self.pos.x
        y = self.pos.y

        for i in range(8):
            v_move = Point(i, y)
            h_move = Point(x, i)

            if self.is_valid_move(v_move):
                moves.append(v_move)
            if self.is_valid_move(h_move):
                moves.append(h_move)

        return moves


class Knight(Piece):
    def can_attack(self, pos: Point) -> bool:
        if self._check_illegal_move(pos):
            return False

        v_distance = abs(self.pos.x - pos.x)
        h_distance = abs(self.pos.y - pos.y)

        return ((v_distance == 1 and h_distance == 2) or
                (v_distance == 2 and h_distance == 1))

    def get_all_valid_moves(self) -> tp.List[Point]:
        moves = []
        x = self.pos.x
        y = self.pos.y

        possible_moves = [Point(x + 1, y + 2),
                          Point(x + 1, y - 2),
                          Point(x - 1, y + 2),
                          Point(x - 1, y - 2),
                          Point(x + 2, y + 1),
                          Point(x + 2, y - 1),
                          Point(x - 2, y + 1),
                          Point(x - 2, y - 1)]

        for move in possible_moves:
            if self.is_valid_move(move):
                moves.append(move)
        return moves


class Bishop(Piece):
    def can_attack(self, pos: Point) -> bool:
        if self._check_illegal_move(pos):
            return False

        v_distance = self.pos.x - pos.x
        h_distance = self.pos.y - pos.y

        if v_distance == h_distance or v_distance + h_distance == 0:
            return self._can_move_diagonally_to(pos)

        return False

    def get_all_valid_moves(self) -> tp.List[Point]:
        moves = []
        for row, col in product(range(8), range(8)):
            move = Point(row, col)
            if self.is_valid_move(move):
                moves.append(move)
        return moves

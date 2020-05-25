import typing as tp
from enum import Enum

from chess_ai.core.Mechanics.point import Point
from chess_ai.core.Mechanics.color import Color
from chess_ai.core.Pieces.piece import PieceType


class Castle(Enum):
    Kingside = 'Kingside'
    Queenside = 'Queeenside'


class Move(tp.NamedTuple):
    move: str
    color: Color
    piece: PieceType
    col_helper: tp.Optional[str]
    row_helper: tp.Optional[int]
    destination: tp.Optional[Point]
    en_passant: bool
    upgrade: tp.Optional[PieceType]
    castle: tp.Optional[Castle]
    action: str

    def __repr__(self):
        move = self.move.ljust(11)
        color = self.color.value

        if self.castle is not None:
            return f'{move}{color} King castles {self.castle.value}'

        loc_helper = ''
        if self.col_helper is not None and self.row_helper is not None:
            loc_helper = f' at {self.col_helper}{self.row_helper}'
        elif self.col_helper is not None:
            loc_helper = f' in col {self.col_helper}'
        elif self.row_helper is not None:
            loc_helper = f' in row {self.row_helper}'

        upgrade = ''
        if self.upgrade:
            upgrade = f'. Upgrades to {self.upgrade.value}'

        return f'{move}{color} {self.piece.value}{loc_helper}{self.action}{self.destination.to_str()}{upgrade}'

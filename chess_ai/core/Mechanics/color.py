from enum import Enum

class Color(Enum):
    White: str = 'White'
    Black: str = 'Black'


def get_opposite_color(color):
    if color == Color.White:
        return Color.Black
    return Color.White

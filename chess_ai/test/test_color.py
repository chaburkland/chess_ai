from pytest import main

from chess_ai.core.Mechanics.color import Color, get_opposite_color


def test_opposite_color():
    assert Color.White == get_opposite_color(Color.Black)
    assert Color.Black == get_opposite_color(Color.White)
    assert Color.White != get_opposite_color(Color.White)
    assert Color.Black != get_opposite_color(Color.Black)


if __name__ == '__main__':
    main()
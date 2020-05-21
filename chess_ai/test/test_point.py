from pytest import main


from chess_ai.core.Mechanics.point import Point, check_bounds


def test_constructor():
    point = Point()
    assert not point.is_valid()

    point = Point(1, 4)
    assert point.x == 1 and point.y == 4

def test_is_valid():
    assert Point(0, 0).is_valid()
    assert Point(4, 4).is_valid()
    assert Point(7, 7).is_valid()

    assert not Point(-1, 0).is_valid()
    assert not Point(0, -1).is_valid()
    assert not Point(0, 8).is_valid()
    assert not Point(8, 0).is_valid()

def test_check_bounds():
    assert check_bounds(0)
    assert check_bounds(4)
    assert check_bounds(7)

    assert not check_bounds(-1)
    assert not check_bounds(8)

def test_equals_point():
    p = Point(1, 4)
    q = Point(2, 3)
    assert p != q

    q = Point(1, 4)
    assert p == q

def test_equals_xy():
    p = Point(1, 4)
    assert p.equals(1, 4)
    assert not p.equals(2, 3)



if __name__ == '__main__':
    main()
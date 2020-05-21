
def check_bounds(x):
    return 0 <= x <= 7

class Point:
    KEY_MAP = dict(
            a=0, b=1, c=2, d=3, e=4, f=5, g=6, h=7,
            A=0, B=1, C=2, D=3, E=4, F=5, G=6, H=7)

    @classmethod
    def from_str(cls, coordinates: str) -> 'Point':
        try:
            y = cls.KEY_MAP.get(coordinates[0], -1)
            return cls(int(coordinates[1]) - 1, y)
        except:
            breakpoint()
            stop_here = True
            return Point()

    def __init__(self, x=-1, y=-1):
        self._x = x
        self._y = y

    def is_valid(self):
        return check_bounds(self._x) and check_bounds(self._y)

    def __eq__(self, other):
        return self._x == other.x and self._y == other.y

    def equals(self, x, y):
        return self._x == x and self._y == y

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, val):
        assert check_bounds(val)
        self._x = x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, val):
        assert check_bounds(val)
        self._y = y

    def __repr__(self):
        return f'Point<{self.x}, {self.y}>'

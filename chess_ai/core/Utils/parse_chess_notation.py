
class UnknownMove(Exception):
    pass


class Parser:
    _PIECE_MAP = dict(K='King', Q='Queen', N='Knight', B='Bishop', R='Rook')

    @staticmethod
    def _iter_input_triplets(iterable):
        it = iter(iterable)
        while True:
            try:
                skip = next(it)
            except StopIteration:
                return

            white, black = None, None
            try:
                white = next(it)
            except StopIteration:
                return

            try:
                black = next(it)
            except StopIteration:
                yield white, None
                return
            else:
                yield white, black

    @classmethod
    def from_fp(cls, fp: str):
        with open(fp, 'r') as f:
            contents = f.read().replace('\n', ' ')

        moves = []
        for move in cls._iter_input_triplets(contents.split()):
            moves.append(move)

        return cls(moves)

    def __init__(self, moves):
        self.moves = moves

    @classmethod
    def pretty_print_move(cls, move, color):
        check = False
        if '+' in move:
            check = True
            move = move.replace('+', '')

        upgrade = ''
        if '=' in move:
            upgrade = f'. Upgrades to {cls._PIECE_MAP[move[-1]]}'
            move = move[:-2]

        checkmate = False
        if '#' in move:
            move = move[:-1]
            checkmate = True

        en_passant = False
        if '(ep)' in move:
            en_passant = True
            move = move[:-4]

        if len(move) == 2:
            result = f'Pawn to {move.upper()}'

        elif move == '0-0':
            result = 'King castles kingside'

        elif move == '0-0-0':
            result = 'King castles quenside'

        else:
            post = move.split('x')
            if len(post) == 1:
                action = 'moves to'
                prefix, destination = move[1:-2], move[-2:]
            else:
                prefix, destination = post
                prefix = prefix[1:]
                action = 'captures piece on'

            piece = cls._PIECE_MAP.get(move[0], 'Pawn')
            destination = destination.upper()

            if len(prefix) == 0:
                piece_modifier = ''
            elif len(prefix) == 1:
                if prefix[0] in tuple('abcdefgh'):
                    piece_modifier =  f' in col {prefix.upper()}'
                else:
                    piece_modifier =  f' in row {prefix}'
            elif len(prefix) == 2:
                piece_modifier = f'at {prefix.upper()}'
            else:
                raise UnknownMove(move)

            if en_passant:
                action = 'en passants to'

            result = f'{piece}{piece_modifier} {action} {destination}{upgrade}'

        if check:
            return f'{color} {result}. Check.'

        if checkmate:
            return f'{color} {result}. Checkmate.'

        return f'{color} {result}.'

    def pretty_ouptut(self):
        for white, black in self.moves:
            if not white:
                print('Black wins. Game over')
                break

            og = (white, black)

            white = self.pretty_print_move(white, 'White')

            if not black:
                print(og[0].ljust(10), white)
                print('White wins. Game over')
                break

            black = self.pretty_print_move(black, 'Black')

            print(og[0].ljust(10), white.ljust(47), og[1].ljust(10), black)


moves = [
    ('e4',          'e5'        ),
    ('Nf3',         'Nc6'       ),
    ('Bb5',         'Nf6'       ),
    ('Nc3',         'Bc5'       ),
    ('0-0',         'd5'        ),
    ('exd5',        'Nxd5'      ),
    ('Nxd5',        'Qxd5'      ),
    ('Bxc6+',       'bxc6'      ),
    ('c3',          '0-0'       ),
    ('Ng5',         'e4'        ),
    ('d4',          'exd3(ep)'  ),
    ('Qf3',         'd2'        ),
    ('Qxd5',        'dxc1=Q'    ),
    ('Raxc1',       'cxd5'      ),
    ('Kh1',         'Bb7'       ),
    ('f4',          'Rfe8'      ),
    ('Nh3',         'Rad8'      ),
    ('g3',          'Be3'       ),
    ('Rcd1',        'f6'        ),
    ('Rfc1',        'd4#'       ),

]


if __name__ == '__main__':
    parser = Parser.from_fp('/home/burkland/github/chess_ai_pkg/chess_ai/test/input/moves.txt')
    parser.pretty_ouptut()

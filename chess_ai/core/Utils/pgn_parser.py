from collections import namedtuple
from enum import Enum
import typing as tp

from chess_ai.core.Pieces.piece import PieceType
from chess_ai.core.Mechanics.color import Color
from chess_ai.core.Mechanics.point import Point
from chess_ai.core.Mechanics.move import Move, Castle


class UnknownMove(Exception):
    pass


class Parser:
    _PIECE_MAP = dict(
            K=PieceType.King,
            Q=PieceType.Queen,
            N=PieceType.Knight,
            B=PieceType.Bishop,
            R=PieceType.Rook,
    )

    @classmethod
    def from_pgn(cls, fp: str):
        def strip_comments(line, is_multiline_comment):
            if is_multiline_comment:
                ending = line.find('}')
                if ending != -1:
                    return line[ending+1:], False
                return '', True

            semicolon = line.find(';')
            if semicolon != -1:
                return line[:semicolon], False

            start = line.find('{')
            end = line.find('}')
            if start != -1:
                if line.find('}') == -1:
                    return line[:start], True
                return line[:start], False
            return line, False

        def iter_tuplets(iterable):
            it = iter(iterable)
            while True:
                try:
                    first = next(it)
                except StopIteration:
                    return

                first = first[first.find('.')+1:]

                try:
                    yield first, next(it)
                except StopIteration:
                    yield first, ''
                    return

        core_lines = []
        intro = True
        is_multiline_comment = False

        with open(fp, 'r') as f:
            lines = f.read()

        for drop in ('1/2-1/2', '1-0', '0-1', '+', '#'):
            lines = lines.replace(drop, '')

        for line in lines.splitlines():
            if not intro:
                line, is_multiline_comment = strip_comments(line, is_multiline_comment)
                core_lines.append(line)
            else:
                if line[:2] == '1.':
                    line, is_multiline_comment = strip_comments(line, is_multiline_comment)
                    core_lines.append(line)
                    intro = False

        raw_moves = ' '.join(core_lines).replace('\n', ' ').replace('  ', ' ').replace('. ', '.').split()
        return cls(list(iter_tuplets(raw_moves)))

    @classmethod
    def from_fools_mate(cls):
        moves = [
                ('f3', 'e5'),
                ('g4', 'Qh4#'),
        ]
        return cls(moves)

    @classmethod
    def from_sample_games(cls, key):
        sample_games = {
                'one': [('e4',    'e5'),
                        ('Nf3',   'Nc6'),
                        ('Bb5',   'Nf6'),
                        ('Nc3',   'Bc5'),
                        ('0-0',   'd5'),
                        ('exd5',  'Nxd5'),
                        ('Nxd5',  'Qxd5'),
                        ('Bxc6+', 'bxc6'),
                        ('c3',    '0-0'),
                        ('Ng5',   'e4'),
                        ('d4',    'exd3(ep)'),
                        ('Qf3',   'd2'),
                        ('Qxd5',  'dxc1=Q'),
                        ('Raxc1', 'cxd5'),
                        ('Kh1',   'Bb7'),
                        ('f4',    'Rfe8'),
                        ('Nh3',   'Rad8'),
                        ('g3',    'Be3'),
                        ('Rcd1',  'f6'),
                        ('Rfe1',  'd4#')],
        }

        return cls(sample_games[key])

    def __init__(self, moves):
        self.moves = moves

    @classmethod
    def parse_move(cls, move: str, color: Color) -> Move:
        og_move = move
        if '+' in move:
            move = move.replace('+', '')

        if '#' in move:
            move = move[:-1]

        upgrade = None
        if '=' in move:
            upgrade = cls._PIECE_MAP[move[-1]]
            move = move[:-2]

        en_passant = False
        if '(ep)' in move:
            en_passant = True
            move = move[:-4]

        action = ''
        destination = None
        castle = None
        col_helper = None
        row_helper = None

        if len(move) == 2:
            piece = PieceType.Pawn
            destination = Point.from_str(move)
            action = ' moves to '
        elif move in ('0-0', 'O-O'):
            piece = PieceType.King
            castle = Castle.Kingside
        elif move in ('0-0-0', 'O-O-O'):
            piece = PieceType.King
            castle = Castle.Queenside
        else:
            post = move.split('x')
            if len(post) == 1:
                action = ' moves to '
                prefix, dest_str = move[1:-2], move[-2:]
            else:
                action = ' captures piece on '
                prefix, dest_str = post
                prefix = prefix[1:]

            piece = cls._PIECE_MAP.get(move[0], PieceType.Pawn)
            destination = Point.from_str(dest_str)

            if len(prefix) == 0:
                pass
            elif len(prefix) == 1:
                if prefix[0] in tuple('abcdefgh'):
                    col_helper = prefix.upper()
                else:
                    row_helper = int(prefix)
            elif len(prefix) == 2:
                col_helper = prefix[0].upper()
                row_helper = int(prefix[1])
            else:
                raise UnknownMove(move)

        if en_passant:
            action = ' en passants to '

        return Move(
                move=og_move,
                color=color,
                piece=piece,
                col_helper=col_helper,
                row_helper=row_helper,
                destination=destination,
                en_passant=en_passant,
                upgrade=upgrade,
                castle=castle,
                action=action,
        )

    def yield_moves(self) -> tp.Generator[tp.Tuple[Move, Move], None, None]:
        for white_move, black_move in self.moves:
            if not white_move:
                break

            white = self.parse_move(white_move, Color.White)

            if not black_move:
                yield white, None
                break

            black = self.parse_move(black_move, Color.Black)

            yield white, black

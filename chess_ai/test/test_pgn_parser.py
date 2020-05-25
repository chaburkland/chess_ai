import os
from collections import Counter
from pytest import main

from chess_ai.core.Mechanics.point import Point
from chess_ai.core.Mechanics.move import Move, Castle
from chess_ai.core.Pieces.piece import PieceType
from chess_ai.core.Utils.pgn_parser import Parser
from chess_ai.test import get_input


def get_parser_stats(parser):
    total = 0
    white_pieces = Counter()
    white_destinations = Counter()
    col_helpers = Counter()
    row_helpers = Counter()
    black_pieces = Counter()
    black_destinations = Counter()
    upgrades = Counter()
    en_passants = 0
    queensides = 0
    kingsides = 0

    for white, black in parser.yield_moves():
        if white is not None:
            if white.en_passant:
                en_passants += 1
            if white.castle == Castle.Kingside:
                kingsides += 1
            if white.castle == Castle.Queenside:
                queensides += 1
            if white.upgrade is not None:
                upgrades.update([white.upgrade.value])
            if white.col_helper:
                col_helpers.update(white.col_helper)
            if white.row_helper:
                row_helpers.update([white.row_helper])

            white_pieces.update([white.piece.value])
            if white.destination is not None:
                white_destinations.update([white.destination])

        if black is not None:
            if black.en_passant:
                en_passants += 1
            if black.castle == Castle.Kingside:
                kingsides += 1
            if black.castle == Castle.Queenside:
                queensides += 1
            if black.upgrade is not None:
                upgrades.update([black.upgrade.value])
            if black.col_helper:
                col_helpers.update(black.col_helper)
            if black.row_helper:
                row_helpers.update([black.row_helper])

            black_pieces.update([black.piece.value])
            if black.destination is not None:
                black_destinations.update([black.destination])

        total += 1

    return dict(
            total=total,
            white_pieces=white_pieces,
            white_destinations=white_destinations,
            col_helpers=col_helpers,
            row_helpers=row_helpers,
            black_pieces=black_pieces,
            black_destinations=black_destinations,
            upgrades=upgrades,
            en_passants=en_passants,
            queensides=queensides,
            kingsides=kingsides,
    )


def test_parse_raphael_hiaves_2006():
    parser = Parser.from_pgn(get_input.get('raphael_hiaves_2006.pgn'))

    stats = get_parser_stats(parser)
    total = stats['total']
    white_pieces = stats['white_pieces']
    white_destinations = stats['white_destinations']
    col_helpers = stats['col_helpers']
    row_helpers = stats['row_helpers']
    black_pieces = stats['black_pieces']
    black_destinations = stats['black_destinations']
    upgrades = stats['upgrades']
    en_passants = stats['en_passants']
    queensides = stats['queensides']
    kingsides = stats['kingsides']

    assert len(parser.moves) == total
    assert (2 * total) - kingsides - queensides == sum(white_destinations.values()) + sum(black_destinations.values())

    assert 1 == en_passants
    assert 2 == kingsides
    assert 0 == queensides
    assert dict(Queen=1) == upgrades
    assert dict(A=2, C=1, F=2) == col_helpers
    assert {} == row_helpers

    assert dict(Pawn=6, Rook=3, Knight=5, Bishop=2, Queen=2, King=2) == white_pieces
    assert 3 == white_destinations[Point(4, 3)]
    assert 15 == len(white_destinations)

    assert dict(Pawn=10, Rook=2, Knight=3, Bishop=3, Queen=1, King=1) == black_pieces
    assert 4 == black_destinations[Point(4, 3)]
    assert 14 == len(black_destinations)


def test_parse_fischer_spassky_1992():
    parser = Parser.from_pgn(get_input.get('fischer_spassky_1992.pgn'))

    stats = get_parser_stats(parser)
    total = stats['total']
    white_pieces = stats['white_pieces']
    white_destinations = stats['white_destinations']
    col_helpers = stats['col_helpers']
    row_helpers = stats['row_helpers']
    black_pieces = stats['black_pieces']
    black_destinations = stats['black_destinations']
    upgrades = stats['upgrades']
    en_passants = stats['en_passants']
    queensides = stats['queensides']
    kingsides = stats['kingsides']

    assert len(parser.moves) == total
    assert (2 * total) - kingsides - queensides - 1 == sum(white_destinations.values()) + sum(black_destinations.values())

    assert 0 == en_passants
    assert 2 == kingsides
    assert 0 == queensides
    assert {} == upgrades
    assert dict(A=1, B=2) == col_helpers
    assert {} == row_helpers

    assert dict(Pawn=14, Rook=7, Knight=7, Bishop=8, Queen=3, King=4) == white_pieces

    assert 3 == white_destinations[Point(0, 4)]
    assert 28 == len(white_destinations)

    assert dict(Pawn=12, Rook=3, Knight=12, Bishop=5, Queen=3, King=7) == black_pieces
    assert 3 == black_destinations[Point(4, 1)]
    assert 29 == len(black_destinations)


def test_parse_lucky_bardwick_1995():
    parser = Parser.from_pgn(get_input.get('lucky_bardwick_1995.pgn'))

    stats = get_parser_stats(parser)
    total = stats['total']
    white_pieces = stats['white_pieces']
    white_destinations = stats['white_destinations']
    col_helpers = stats['col_helpers']
    row_helpers = stats['row_helpers']
    black_pieces = stats['black_pieces']
    black_destinations = stats['black_destinations']
    upgrades = stats['upgrades']
    en_passants = stats['en_passants']
    queensides = stats['queensides']
    kingsides = stats['kingsides']

    assert len(parser.moves) == total
    assert (2 * total) - kingsides - queensides == sum(white_destinations.values()) + sum(black_destinations.values())

    assert 0 == en_passants
    assert 0 == kingsides
    assert 1 == queensides
    assert {} == upgrades
    assert dict(D=1, F=1) == col_helpers
    assert {} == row_helpers

    assert dict(Pawn=20, Rook=55, Knight=30, Bishop=3, Queen=8, King=27) == white_pieces
    assert 10 == white_destinations[Point(4, 4)]
    assert 49 == len(white_destinations)

    assert dict(Pawn=12, Rook=60, Knight=15, Bishop=8, Queen=3, King=45) == black_pieces
    assert 8 == black_destinations[Point(6, 3)]
    assert 51 == len(black_destinations)


def test_parse_mecking_h_donner_1971():
    parser = Parser.from_pgn(get_input.get('mecking_h_donner_1971.pgn'))

    stats = get_parser_stats(parser)
    total = stats['total']
    white_pieces = stats['white_pieces']
    white_destinations = stats['white_destinations']
    col_helpers = stats['col_helpers']
    row_helpers = stats['row_helpers']
    black_pieces = stats['black_pieces']
    black_destinations = stats['black_destinations']
    upgrades = stats['upgrades']
    en_passants = stats['en_passants']
    queensides = stats['queensides']
    kingsides = stats['kingsides']

    assert len(parser.moves) == total
    assert (2 * total) - kingsides - queensides - 1 == sum(white_destinations.values()) + sum(black_destinations.values())

    assert 0 == en_passants
    assert 2 == kingsides
    assert 0 == queensides
    assert {} == upgrades
    assert dict(F=1) == col_helpers
    assert {} == row_helpers

    assert dict(Pawn=8, Rook=1, Knight=3, Bishop=2, Queen=2, King=1) == white_pieces
    assert 2 == white_destinations[Point(4, 2)]
    assert 15 == len(white_destinations)

    assert dict(Pawn=6, Knight=3, Bishop=5, Queen=1, King=1) == black_pieces
    assert 3 == black_destinations[Point(4, 2)]
    assert 11 == len(black_destinations)


def test_parse_moves_fools_mate():
    parser = Parser.from_fools_mate()

    stats = get_parser_stats(parser)
    total = stats['total']
    white_pieces = stats['white_pieces']
    white_destinations = stats['white_destinations']
    col_helpers = stats['col_helpers']
    row_helpers = stats['row_helpers']
    black_pieces = stats['black_pieces']
    black_destinations = stats['black_destinations']
    upgrades = stats['upgrades']
    en_passants = stats['en_passants']
    queensides = stats['queensides']
    kingsides = stats['kingsides']

    assert 2 == total
    assert (2 * total) - kingsides - queensides == sum(white_destinations.values()) + sum(black_destinations.values())

    assert 0 == en_passants
    assert 0 == kingsides
    assert 0 == queensides
    assert {} == upgrades
    assert {} == col_helpers
    assert {} == row_helpers

    assert dict(Pawn=2) == white_pieces
    assert 1 == white_destinations[Point(3, 6)]
    assert 2 == len(white_destinations)

    assert dict(Pawn=1, Queen=1) == black_pieces
    assert 1 == black_destinations[Point(4, 4)]
    assert 2 == len(black_destinations)


def test_parse_length8848_5():

    parser = Parser.from_pgn(get_input.get('length8848.5.pgn'))

    stats = get_parser_stats(parser)
    total = stats['total']
    white_pieces = stats['white_pieces']
    white_destinations = stats['white_destinations']
    col_helpers = stats['col_helpers']
    row_helpers = stats['row_helpers']
    black_pieces = stats['black_pieces']
    black_destinations = stats['black_destinations']
    upgrades = stats['upgrades']
    en_passants = stats['en_passants']
    queensides = stats['queensides']
    kingsides = stats['kingsides']

    white_sum = sum(white_destinations.values())
    black_sum = sum(black_destinations.values())

    assert 8849 == total
    assert 1 == white_sum - black_sum
    assert (2 * total) - kingsides - queensides - 1 == white_sum + black_sum
    assert 0 == en_passants
    assert 0 == kingsides
    assert 0 == queensides
    assert dict(Queen=16) == upgrades

    assert dict(A=593, B=762, C=885, D=914, E=750, F=803, G=781, H=536) == col_helpers
    assert {1: 173, 2: 158, 3: 198, 4: 183, 5: 142, 6: 126, 7: 95, 8: 81} == row_helpers

    assert dict(Pawn=48, Rook=962, Knight=1487, Bishop=716, Queen=4818, King=818) == white_pieces
    assert 144 == white_destinations[Point(3, 2)]
    assert 64 == len(white_destinations)

    assert dict(Pawn=48, Rook=1269, Knight=531, Bishop=701, Queen=5146, King=1153) == black_pieces
    assert 121 == black_destinations[Point(3, 2)]
    assert 64 == len(black_destinations)



if __name__ == '__main__':
    main()

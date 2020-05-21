import typing as tp
from enum import Enum
from itertools import product
from collections import namedtuple

from chess_ai.core.Game.screenshot import Screenshot
from chess_ai.core.Game.board import Board
from chess_ai.core.Mechanics.point import Point
from chess_ai.core.Mechanics.color import Color, get_opposite_color
from chess_ai.core.Mechanics.status import Status
from chess_ai.core.Pieces.piece import Empty, Piece, Queen, Knight, Rook, Pawn, Bishop


class CompetitiveRulesetEndings(Enum):
    ThreefoldRepeat = 0
    FivefoldRepeat = 1
    FiftyNoProgress = 2
    SeventyFiveNoProgress = 3
    InsufficientMaterials = 4


def competitive_ruleset_endings_text(ending: CompetitiveRulesetEndings) -> str:
    if ending == CompetitiveRulesetEndings.ThreefoldRepeat:
        return "three-fold repeat of the exact same board state.\n"
    elif ending == CompetitiveRulesetEndings.FivefoldRepeat:
        return "three-fold repeat of the exact same board state.\n"
    elif ending == CompetitiveRulesetEndings.FiftyNoProgress:
        return "fifty moves without any progress.\n"
    elif ending == CompetitiveRulesetEndings.SeventyFiveNoProgress:
        return "seventy-five moves without any progress.\n"
    elif ending == CompetitiveRulesetEndings.InsufficientMaterials:
        return "insufficient materials to force a checkmate.\n"
    else:
        return "unknown reasons.\n"


GameHistory = namedtuple('GameHistory', ('screenshot', 'count'))


class UserQuitMidGameException(Exception):
    pass


class Game:
    '''Responsible for managing the start, flow, and ending of a chess game'''

    INPUT_DELIMS = (' ', ',', ';', ':', '-')
    INVALID_INPUT_MSG = f'Invalid input. Please seperate two moves in standard chess format using one of these separators: {INPUT_DELIMS}'

    def __init__(self):
        self.board: Board = Board()
        self.current_team: Color = Color.White

        self.game_history: tp.List[GameHistory] = [GameHistory(self.board.screenshot, 1)]

        self.threefold_repetitions_forfeited: bool = False
        self.fifty_moves_no_progress_forfeited: bool = False
        self.stagnant_move_count: int = 0

    def start_game(self, initial_moves: tp.Optional[tp.List[tp.Tuple[str, str]]] = None):
        game_status: Status = Status.InProgress
        competitive_ending: tp.Optional[CompetitiveRulesetEndings] = None

        def reset_after_turn():
            nonlocal game_status

            # Change team
            self.current_team = get_opposite_color(self.current_team)

            # Screenshot state
            self.game_history.append(GameHistory(self.board.screenshot, 1))

            # Update status
            game_status = self.board.get_board_status(self.current_team)

        if initial_moves is not None:
            i = 0
            for move1, move2 in initial_moves:
                destination = Point.from_str(move2)
                self.board.perform_move(self.board[move1], destination, default_promotion=True)

                reset_after_turn()


        def continue_playing():
            nonlocal game_status
            nonlocal competitive_ending

            game_status = self.board.get_board_status(self.current_team)
            competitive_ending = self.check_competitive_ruleset()

            if game_status in (Status.Checkmate, Status.Stalemate) or competitive_ending is not None:
                return False
            return True

        while continue_playing():
            print(self.board)
            #print(f'White Score: {self.get_score(Color.White)}')
            #print(f'Black Score: {self.get_score(Color.Black)}')

            print(f"{self.current_team.value} team's turn.")

            try:
                piece_location, move_to = self.get_input('Please input your move: ')
            except UserQuitMidGameException as e:
                print(e)
                return

            piece = self.board[piece_location]

            # Cache values before move
            white_check = self.board.get_king(Color.White).in_check
            black_check = self.board.get_king(Color.Black).in_check

            self.board.perform_move(piece, move_to)

            self.output_check_status_updates(white_check, black_check)

            reset_after_turn()

        self.display_game_ending(game_status, competitive_ending)

        return game_status, competitive_ending

    def get_input(self, msg: str) -> Point:
        '''Prompts for input from the user. Parses input'''
        piece_location, move_to = '', ''

        while True:
            user_input = input(msg)

            if user_input in ('Quit', 'quit', 'q', 'Q'):
                raise UserQuitMidGameException

            for delim in self.INPUT_DELIMS:
                if delim in user_input:
                    try:
                        piece_location, move_to = user_input.split(delim)
                    except ValueError:
                        print(self.INVALID_INPUT_MSG)
                        continue

            if not piece_location or not move_to:
                print(self.INVALID_INPUT_MSG)
                continue

            piece_location = Point.from_str(piece_location)
            move_to = Point.from_str(move_to)

            if not self.validate_input(piece_location, move_to):
                continue
            break

        return piece_location, move_to

    def validate_input(self, piece_location: Point, move_to: Point) -> bool:
        '''Validates whether or not a move is complete'''
        piece: Piece = self.board[piece_location]

        if piece is Empty:
            print('Not a piece! Try again.\n')
            return False

        if piece.color != self.current_team:
            print("You cannot move the enemy's piece! Try again.\n")
            return False

        if not piece.is_valid_move(move_to):
            print('Invalid move. Try again.\n')
            return False

        return True

    def output_check_status_updates(self, white_check: bool, black_check: bool):
        '''Displays whether or not a king's check status updated'''
        white_check_board = self.board.get_king(Color.White).in_check
        black_check_board = self.board.get_king(Color.Black).in_check

        if white_check != white_check_board:
            print(f"White king is{'' if white_check_board else ' no longer'} in check!")

        if black_check != black_check_board:
            print(f"Black king is{'' if black_check_board else ' no longer'} in check!")

    def check_competitive_ruleset(self) -> tp.Optional[CompetitiveRulesetEndings]:
        '''Implements uncommon competitive rules like threefold/fivefold repeat, 50/75 no move progress, etc..'''
        repetitions: CompetitiveRulesetEndings = self.check_repetitions()
        if repetitions is not None:
            return repetitions

        no_progress: CompetitiveRulesetEndings = self.check_no_progress()
        if no_progress is not None:
            return no_progress

        insufficient_materials = self.check_insufficient_materials()
        if insufficient_materials is not None:
            return insufficient_materials

        return None

    def display_game_ending(self, game_status: Status, competitive_ending: CompetitiveRulesetEndings) -> None:
        '''Displays how the game ended.'''
        if game_status == Status.Checkmate:
            print(f'{get_opposite_color(self.current_team).value} just checkmated {self.current_team.value}!')

        elif game_status == Status.Checkmate:
            print('Stalemate!')

        else:
            print(f'Draw due to {competitive_ruleset_endings_text(competitive_ending)}')

    def check_repetitions(self) -> tp.Optional[CompetitiveRulesetEndings]:
        '''Checks to see if repeat games occured'''
        found_match = False
        first = True

        # Start from the top as the most likely occurrence of a threefold/fivefold repetition will be the most recent games
        for game_history in reversed(self.game_history):
            if first:
                first = False
                continue

            last_game = self.game_history[-1]

            if last_game.screenshot.compare_available_moves(game_history.screenshot):
                # Found a match. Propogate up from that state the number of matches it found and aggregate into the most recent find
                self.game_history[-1] = GameHistory(last_game.screenshot, last_game.count + 1)
                found_match = True

            if last_game.count == 5:
                # Fivefold repeat draw is mandatory
                return CompetitiveRulesetEndings.FivefoldRepeat
            elif last_game.count >= 3 and not self.threefold_repetitions_forfeited:
                print('There have been three previous states exactly the smae as this one. Would anyone like to call a draw?')
                response = input()
                if response in ('Y', 'y', 'Yes', 'yes'):
                    return CompetitiveRulesetEndings.ThreefoldRepeat
                else:
                    print('Ok. Right to draw for three-fold state repetition has been forfeited. Will auto-draw at a five-fold repeition streak.')

                    #  Players have forfeited the right to end at three-fold repetitions
                    self.threefold_repetitions_forfeited = True
                    return None
            elif found_match:
                # We documented the match, but it didn't warrant a competitive ending.
                break

        return None

    def check_no_progress(self) -> tp.Optional[CompetitiveRulesetEndings]:
        '''Checks to see if no progress streaks have occured'''
        if len(self.game_history) == 1:
            self.stagnant_move_count = 1
            return

        screenshot1: Screenshot = self.game_history[-1].screenshot
        screenshot2: Screenshot = self.game_history[-2].screenshot

        # Check to see if any pawns moved or if any pieces were captured
        if not screenshot1.compare_piece_count(screenshot2) or not screenshot1.compare_pawn_locations(screenshot2):
            # Reset since a significant change happened
            self.stagnant_move_count = 0
            return None

        self.stagnant_move_count += 1

        if self.stagnant_move_count >= 75:
            # Seventy-five moves with no progress draw is mandatory
            return CompetitiveRulesetEndings.SeventyFiveNoProgress

        if self.stagnant_move_count >= 50 and not self.fifty_moves_no_progress_forfeited:
            response = input('There have been 50 moves without any pawns moved or any pieces captured. Would anyone like to draw? ')

            if respone in ('Y', 'y', 'Yes', 'yes'):
                return CompetitiveRulesetEndings.FiftyNoProgress
            else:
                print('Ok. Right to draw for stagnant board state has been forfeited. Will auto-draw at a 75 no-progress streak.')

                # Players have forfeited the right to end at fifty-fold repetitions
                self.fifty_moves_no_progress_forfeited = True
                return None

        return None

    def check_insufficient_materials(self) -> tp.Optional[CompetitiveRulesetEndings]:
        '''Checks to see if either team has insufficient materials to force a check'''
        white_bishop_a = False
        white_bishop_b = False
        black_bishop_a = False
        black_bishop_b = False
        white_knights = 0
        black_knights = 0

        for row, col in product(range(8), range(8)):
            piece = self.board[row, col]

            # If there is a single queen, rook, or pawn in play there is sufficient material to force a check
            if isinstance(piece, (Queen, Rook, Pawn)):
                return None

            if isinstance(piece, Knight):
                if piece.color == Color.White:
                    white_knights += 1
                else:
                    black_knights += 1
            elif isinstance(piece, Bishop):
                if piece.color == Color.White:
                    white_bishop_a |= (row + col) % 2 == 0
                    white_bishop_b |= (row - col) % 2 != 0
                else:
                    black_bishop_a |= (row + col) % 2 == 0
                    black_bishop_b |= (row - col) % 2 != 0

        no_white_bishops = not white_bishop_a and not white_bishop_b
        no_black_bishops = not black_bishop_a and not black_bishop_b
        no_bishops = no_white_bishops and no_black_bishops
        no_knights = white_knights == 0 and black_knights == 0

        # King & bishop(A or B) vs King & bishop(A or B) - (Same A or B on both sides)
        if ((whiteBishopA == 0 and whiteBishopB != 0 and blackBishopA == 0 and blackBishopB != 0) or
                (whiteBishopA != 0 and whiteBishopB == 0 and blackBishopA != 0 and blackBishopB == 0) and noKnights):
            return CompetitiveRulesetEndings.InsufficientMaterials

        # King vs King & bishop(A or B)
        elif ((((not whiteBishopA) ^ (not whiteBishopB)) and noBlackBishops) or
                 (((not blackBishopA) ^ (not blackBishopB)) and noWhiteBishops) and noKnights):
            return CompetitiveRulesetEndings.InsufficientMaterials

        # King vs King and Knight
        elif ((whiteKnights == 1 and blackKnights == 0) or
                (blackKnights == 1 and whiteKnights == 0) and noBishops):
            return CompetitiveRulesetEndings.InsufficientMaterials

        # King vs King
        elif (noBishops and noKnights):
            return CompetitiveRulesetEndings.InsufficientMaterials

        return None

    def get_score(self, color: Color) -> float:
        if color == Color.White:
            return self.board.white_score
        return self.board.black_score

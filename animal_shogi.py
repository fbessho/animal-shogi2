from collections import namedtuple
from enum import Enum, auto
import logging

logger = logging.getLogger(__name__)

Position = namedtuple('Position', 'bw, position, koma')


class Move:
    def __init__(self, bw, koma, orig, new):
        self.bw = bw  # str: Turn ('b'lack or 'w'hite)
        self.koma = koma  # a Koma instance
        self.orig = orig  # Original position (e.g. 'a4', 'mochigoma')
        self.new = new  # Original position (e.g. 'a4', 'mochigoma')


class Koma(Enum):
    LION = auto()
    ELEPHANT = auto()
    GIRAFFE = auto()
    HIYOKO = auto()
    CHICKEN = auto()

    def __str__(self):
        return self.name


INITIAL_BOARD = [
    Position('b', 'b4', Koma.LION),
    Position('b', 'a4', Koma.ELEPHANT),
    Position('b', 'c4', Koma.GIRAFFE),
    Position('b', 'b3', Koma.HIYOKO),
    Position('w', 'b1', Koma.LION),
    Position('w', 'c1', Koma.ELEPHANT),
    Position('w', 'a1', Koma.GIRAFFE),
    Position('w', 'b2', Koma.HIYOKO),
]

POINTS = {
    Koma.LION: 100,
    Koma.ELEPHANT: 5,
    Koma.GIRAFFE: 6,
    Koma.HIYOKO: 1,
    Koma.CHICKEN: 8
}

ACRONYMS = {
    Koma.LION: 'L',
    Koma.ELEPHANT: 'E',
    Koma.GIRAFFE: 'G',
    Koma.HIYOKO: 'H',
    Koma.CHICKEN: 'C'
}


MOVES = {
    Koma.LION: [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)],
    Koma.ELEPHANT: [(-1, -1), (-1, 1), (1, -1), (1, 1)],
    Koma.GIRAFFE: [(-1, 0), (1, 0), (0, -1), (0, 1)],
    Koma.HIYOKO: [(0, -1)],
    Koma.CHICKEN: [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (0, 1)]
}


def coord_to_name(x, y):
    # (0, 0) -> a1
    return '{}{}'.format('abc'[x], y+1)


def name_to_coord(name):
    # a1 -> (0, 0)
    x = ord(name[0]) - ord('a')
    y = int(name[1]) - 1
    return x, y


def get_pos_short_name(position):
    up_down = {'b': '^', 'w': 'v'}[position.bw]
    koma_short = ACRONYMS[position.koma]
    return f'{up_down}{koma_short}'


def move_to_str(move):
    turn_str = '▲' if move.bw == 'b' else '△'
    return '{}{} {} ({})'.format(turn_str, move.new, move.koma, move.orig)


def get_blank_cells(board):
    all_cells = [coord_to_name(x, y) for x in range(3) for y in range(4)]
    filled_cells = [p.position for p in board]
    return [c for c in all_cells if c not in filled_cells]


def get_cells_with_my_koma(board, turn):
    return [p.position for p in board if p.bw == turn]


def possible_moves(board, turn):
    tmp = []
    blank_cells = get_blank_cells(board)
    cells_with_my_koma = get_cells_with_my_koma(board, turn)

    for p in board:
        if p.bw != turn:
            continue  # not your piece

        if p.position == 'mochigoma':
            for c in blank_cells:
                tmp.append(Move(turn, p.koma, p.position, c))
            continue

        moves = MOVES[p.koma][:]
        if turn == 'w':
            moves = [(-x, -y) for x, y in moves]

        orig = p.position
        orig_x, orig_y = name_to_coord(orig)
        for dx, dy in moves:
            new_x = orig_x + dx
            new_y = orig_y + dy

            # possible?
            # out of bound
            if not (0 <= new_x <= 2):
                continue
            if not (0 <= new_y <= 3):
                continue
            # filled with my koma
            new = coord_to_name(new_x, new_y)
            if new in cells_with_my_koma:
                continue

            tmp.append(Move(turn, p.koma, p.position, new))

    return tmp


def is_valid_move(board, move):
    """Check if `move` is a valid move on the `board`

    :return: (is_valid, reason)
        is_valid is a boolean
        reason is a string
    """
    # Koma exists in the original position?
    existing_komas = [pos for pos in board if (pos.bw == move.bw) and (pos.position == move.orig) and (pos.koma == move.koma)]
    if not existing_komas:
        return False, f'Koma does not exit in the original position [{move.orig}]'

    # Ensure that there's no koma owned by the player at the new position
    my_komas_in_the_new_position = [pos for pos in board if (pos.bw == move.bw) and (pos.position == move.new)]
    if my_komas_in_the_new_position:
        return False, f'Your Koma exists in the new position [{move.new}]'

    # Is the new position valid?
    valid_new_positions = [x + y for x in 'abc' for y in '1234']
    if move.new not in valid_new_positions:
        return False, f'Invalid position name [{move.new}]'

    # Could the koma move from orig to new?
    if move.orig != 'mochigoma':
        orig_x, orig_y = name_to_coord(move.orig)
        new_x, new_y = name_to_coord(move.new)
        actual_move = (new_x - orig_x, new_y - orig_y)
        valid_moves = MOVES[move.koma]
        if actual_move not in valid_moves:
            return False, f'Invalid movement ({move.koma} cannot move from {move.orig} to {move.new}.'

    # All checks passed!
    return True, ''


def get_new_board(board, move):
    # process mochigoma first
    tmp = []
    for p in board:
        if p.position == move.new:
            tmp.append(Position(move.bw, 'mochigoma', p.koma))
        else:
            tmp.append(p)

    new_board = []
    moved = False
    for p in tmp:
        if (not moved) and (p.bw == move.bw) and (p.position == move.orig) and (p.koma == move.koma):
            new_pos = Position(move.bw, move.new, move.koma)
            new_board.append(new_pos)
            moved = True
        else:
            new_board.append(p)

    return new_board


def print_board(board, file=None):
    white_mochigoma = [ACRONYMS[p.koma] for p in board if p.bw == 'w' and p.position == 'mochigoma']
    black_mochigoma = [ACRONYMS[p.koma] for p in board if p.bw == 'b' and p.position == 'mochigoma']

    # 'a3' -> Position()
    board_dict = {p.position: p for p in board}

    print(*white_mochigoma, sep=',', file=file)
    print(file=file)
    for y in range(4):
        for x in range(3):
            pos = coord_to_name(x, y)
            if pos in board_dict:
                print(get_pos_short_name(board_dict[pos]), end='', file=file)
            else:
                print('..', end='', file=file)
        print(file=file)
    print(file=file)
    print(*black_mochigoma, sep=',', file=file)


def evaluate(board, turn, depth=3):
    """

    :param board:
    :param turn: 'b' or 'w'
    :param depth:
    :return: (score, best_path)
    """
    lion_mochigoma = [p for p in board if p.position == 'mochigoma' and p.koma == Koma.LION]
    if lion_mochigoma:
        if lion_mochigoma[0].bw == 'b':
            return 9999, []
        else:
            return -9999, []

    if depth == 0:
        point = 0
        for p in board:
            coef = 1 if p.bw == 'b' else -1
            point += coef * POINTS[p.koma]
        return point, []

    best_point = None
    best_path = None

    moves = possible_moves(board, turn)
    for m in moves:
        next_board = get_new_board(board, m)
        next_turn = 'w' if turn == 'b' else 'b'
        sign = -1 if turn == 'w' else 1  # reverse sign if white
        point, path = evaluate(next_board, next_turn, depth=depth-1)
        if (
                (best_point is None)  # first evaluation
                or (sign * point) > (sign * best_point)  # found a better path
                or ((point == best_point) and (len(path)+1) > len(best_path))  # a longer path with the same point
        ):
            best_point = point
            best_path = [m] + path
    return best_point, best_path

# Play a game
from animal_shogi import *

DEPTH = 5
MY_COLOR = 'b'
OPPONENT_COLOR = 'w' if MY_COLOR == 'b' else 'b'

board = INITIAL_BOARD

while True:
    print_board(board)
    print('Input your move')

    valid_move = False

    while not valid_move:
        original_position = input('Original position [a1, mochigoma, m]:')
        new_position = input('New position:')
        koma = input('Koma [LION, ELEPHANT, GIRAFFE, HIYOKO, CHICKEN]:')

        # create move
        original_position = 'mochigoma' if original_position.startswith('m') else original_position
        try:
            koma = Koma[koma]
        except KeyError:
            print(f'Invalid Koma name: {koma}')
            continue

        move = Move(MY_COLOR, koma, original_position, new_position)

        valid_move, reason = is_valid_move(board, move)
        if not valid_move:
            print('Invalid movement: ' + reason)

    board = get_new_board(board, move)
    print()
    print(f'Your move: {move_to_str(move)}')
    print_board(board)

    score, path = evaluate(board, OPPONENT_COLOR, depth=DEPTH)
    their_move = path[0]
    print()
    print(f'Score: {score}')
    print(f'Their move: {move_to_str(their_move)}')
    board = get_new_board(board, their_move)


import copy
import random

SIZE = 9
EMPTY = 0

EASY_CLUES = 45
MEDIUM_CLUES = 35
HARD_CLUES = 30
DIFFICULTY_CLUES = {
    'easy': EASY_CLUES,
    'medium': MEDIUM_CLUES,
    'hard': HARD_CLUES,
}

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def count_solutions(board, limit=2):
    """Count solutions, stopping once ``limit`` solutions are found."""
    if limit < 1:
        return 0

    working_board = deep_copy(board)
    for row in range(SIZE):
        for col in range(SIZE):
            value = working_board[row][col]
            if value == EMPTY:
                continue
            if value not in range(1, SIZE + 1):
                return 0
            working_board[row][col] = EMPTY
            valid = is_safe(working_board, row, col, value)
            working_board[row][col] = value
            if not valid:
                return 0

    def count_from_board():
        best_cell = None
        best_candidates = None
        for row in range(SIZE):
            for col in range(SIZE):
                if working_board[row][col] != EMPTY:
                    continue
                candidates = [
                    number for number in range(1, SIZE + 1)
                    if is_safe(working_board, row, col, number)
                ]
                if not candidates:
                    return 0
                if best_candidates is None or len(candidates) < len(best_candidates):
                    best_cell = (row, col)
                    best_candidates = candidates

        if best_cell is None:
            return 1

        row, col = best_cell
        solution_count = 0
        for candidate in best_candidates:
            working_board[row][col] = candidate
            solution_count += count_from_board()
            working_board[row][col] = EMPTY
            if solution_count >= limit:
                return limit
        return solution_count

    return count_from_board()


def has_unique_solution(board):
    return count_solutions(board, limit=2) == 1


def remove_cells(board, clues):
    if not 0 <= clues <= SIZE * SIZE:
        raise ValueError('clues must be between 0 and 81')

    cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(cells)
    target_removals = SIZE * SIZE - clues
    removed = 0
    for row, col in cells:
        if removed == target_removals:
            break
        value = board[row][col]
        if value == EMPTY:
            continue
        board[row][col] = EMPTY
        if has_unique_solution(board):
            removed += 1
        else:
            board[row][col] = value

    if removed != target_removals:
        raise ValueError('could not create a puzzle with the requested clue count')
    return board


def generate_puzzle(clues=MEDIUM_CLUES, difficulty=None):
    if isinstance(clues, str) and difficulty is None:
        difficulty = clues
    if difficulty is not None:
        try:
            clues = DIFFICULTY_CLUES[difficulty.lower()]
        except (AttributeError, KeyError) as error:
            raise ValueError('difficulty must be Easy, Medium, or Hard') from error
    if not isinstance(clues, int) or not 0 <= clues <= SIZE * SIZE:
        raise ValueError('clues must be between 0 and 81')

    while True:
        solution = create_empty_board()
        fill_board(solution)
        puzzle = deep_copy(solution)
        try:
            remove_cells(puzzle, clues)
        except ValueError:
            continue
        if count_solutions(puzzle, limit=2) == 1:
            return puzzle, solution

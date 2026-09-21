import sudoku_logic


def test_create_empty_board_returns_9x9_board_of_empty_cells():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_is_safe_rejects_row_conflict():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5

    assert not sudoku_logic.is_safe(board, 0, 4, 5)


def test_is_safe_rejects_column_conflict():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5

    assert not sudoku_logic.is_safe(board, 4, 0, 5)


def test_is_safe_rejects_box_conflict():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5

    assert not sudoku_logic.is_safe(board, 2, 2, 5)


def test_fill_board_produces_a_complete_valid_sudoku_board():
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.fill_board(board)
    assert all(cell in range(1, sudoku_logic.SIZE + 1) for row in board for cell in row)
    for index in range(sudoku_logic.SIZE):
        assert set(board[index]) == set(range(1, sudoku_logic.SIZE + 1))
        assert {board[row][index] for row in range(sudoku_logic.SIZE)} == set(range(1, sudoku_logic.SIZE + 1))


def test_deep_copy_creates_an_independent_copy():
    board = [[1, 2], [3, 4]]
    copied_board = sudoku_logic.deep_copy(board)

    copied_board[0][0] = 9

    assert board == [[1, 2], [3, 4]]
    assert copied_board != board


def test_remove_cells_leaves_expected_number_of_clues():
    board = sudoku_logic.create_empty_board()
    assert sudoku_logic.fill_board(board)

    sudoku_logic.remove_cells(board, clues=35)

    assert sum(cell != sudoku_logic.EMPTY for row in board for cell in row) == 35


def test_generate_puzzle_returns_9x9_puzzle_and_solution():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)

    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert all(len(row) == sudoku_logic.SIZE for row in solution)
    assert all(cell in range(1, sudoku_logic.SIZE + 1) for row in solution for cell in row)
    assert all(set(row) == set(range(1, sudoku_logic.SIZE + 1)) for row in solution)
    assert all(
        {solution[row][col] for row in range(sudoku_logic.SIZE)}
        == set(range(1, sudoku_logic.SIZE + 1))
        for col in range(sudoku_logic.SIZE)
    )


def test_puzzle_givens_match_corresponding_solution_values():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)

    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if puzzle[row][col] != sudoku_logic.EMPTY:
                assert puzzle[row][col] == solution[row][col]


def test_generate_puzzle_uses_current_default_clue_behavior():
    puzzle, _ = sudoku_logic.generate_puzzle()

    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 35


def test_count_solutions_distinguishes_zero_one_and_multiple_solutions():
    invalid = sudoku_logic.create_empty_board()
    invalid[0][0] = 1
    invalid[0][1] = 1
    assert sudoku_logic.count_solutions(invalid) == 0

    solved = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]
    assert sudoku_logic.count_solutions(solved) == 1

    almost_empty = sudoku_logic.create_empty_board()
    assert sudoku_logic.count_solutions(almost_empty) == 2


def test_difficulty_levels_use_centralized_clue_counts():
    for difficulty, clues in sudoku_logic.DIFFICULTY_CLUES.items():
        puzzle, _ = sudoku_logic.generate_puzzle(difficulty=difficulty)

        assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == clues
        assert sudoku_logic.count_solutions(puzzle) == 1
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


def test_puzzle_givens_match_corresponding_solution_values():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)

    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if puzzle[row][col] != sudoku_logic.EMPTY:
                assert puzzle[row][col] == solution[row][col]


def test_generate_puzzle_uses_current_default_clue_behavior():
    puzzle, _ = sudoku_logic.generate_puzzle()

    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 35
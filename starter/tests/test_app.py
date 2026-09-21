from copy import deepcopy

def test_get_root_returns_http_200(client):
    response = client.get('/')

    assert response.status_code == 200


def test_get_new_returns_http_200_and_valid_9x9_puzzle(client):
    response = client.get('/new')

    assert response.status_code == 200
    puzzle = response.get_json()['puzzle']
    assert len(puzzle) == 9
    assert all(len(row) == 9 for row in puzzle)


def test_get_new_supports_each_difficulty_case_insensitively(client):
    expected_clues = {'easy': 45, 'medium': 35, 'hard': 30}

    for difficulty, clues in expected_clues.items():
        response = client.get(f'/new?difficulty={difficulty.upper()}')

        assert response.status_code == 200
        puzzle = response.get_json()['puzzle']
        assert sum(cell != 0 for row in puzzle for cell in row) == clues


def test_get_new_rejects_invalid_difficulty(client):
    response = client.get('/new?difficulty=impossible')

    assert response.status_code == 400
    assert response.get_json() == {'error': 'Invalid difficulty'}


def test_post_check_with_current_solution_reports_no_incorrect_cells(client):
    new_response = client.get('/new')
    board = solve_board(new_response.get_json()['puzzle'])

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': [], 'correct': True}


def test_post_check_with_incorrect_values_reports_incorrect_cells(client):
    client.get('/new')
    board = [[0] * 9 for _ in range(9)]
    board[0][0] = 1

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json()['incorrect']
    assert response.get_json()['correct'] is False


def test_post_check_rejects_missing_json_body(client):
    response = client.post('/check')

    assert response.status_code == 400
    assert response.get_json() == {'error': 'Request must contain JSON'}


def test_post_check_rejects_missing_board(client):
    response = client.post('/check', json={})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'JSON must contain a board property'}


def test_post_check_rejects_wrong_board_dimensions(client):
    response = client.post('/check', json={'board': [[0] * 9 for _ in range(8)]})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'Board must contain exactly 9 rows of 9 cells'}


def test_post_check_rejects_non_integer_cells(client):
    board = [[0] * 9 for _ in range(9)]
    board[0][0] = '0'

    response = client.post('/check', json={'board': board})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'Board cells must be integers from 0 through 9'}


def test_post_check_rejects_values_outside_allowed_range(client):
    board = [[0] * 9 for _ in range(9)]
    board[0][0] = 10

    response = client.post('/check', json={'board': board})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'Board cells must be integers from 0 through 9'}


def test_post_check_before_a_game_exists_returns_existing_error(client):
    response = client.post('/check', json={'board': [[0] * 9 for _ in range(9)]})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


def solve_board(puzzle):
    board = deepcopy(puzzle)
    solve(board)
    return board


def solve(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] != 0:
                continue
            for value in range(1, 10):
                if (value not in board[row]
                        and all(board[index][col] != value for index in range(9))
                        and all(board[index][other] != value
                                for index in range(row // 3 * 3, row // 3 * 3 + 3)
                                for other in range(col // 3 * 3, col // 3 * 3 + 3))):
                    board[row][col] = value
                    if solve(board):
                        return True
                    board[row][col] = 0
            return False
    return True
from copy import deepcopy

from app import CURRENT


def test_get_root_returns_http_200(client):
    response = client.get('/')

    assert response.status_code == 200


def test_get_new_returns_http_200_and_valid_9x9_puzzle(client):
    response = client.get('/new')

    assert response.status_code == 200
    puzzle = response.get_json()['puzzle']
    assert len(puzzle) == 9
    assert all(len(row) == 9 for row in puzzle)


def test_post_check_with_current_solution_reports_no_incorrect_cells(client):
    client.get('/new')

    response = client.post('/check', json={'board': deepcopy(CURRENT['solution'])})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': []}


def test_post_check_with_incorrect_values_reports_incorrect_cells(client):
    client.get('/new')
    board = deepcopy(CURRENT['solution'])
    original_value = board[0][0]
    board[0][0] = original_value % 9 + 1

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json()['incorrect'] == [[0, 0]]


def test_post_check_before_a_game_exists_returns_existing_error(client):
    response = client.post('/check', json={'board': [[0] * 9 for _ in range(9)]})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}
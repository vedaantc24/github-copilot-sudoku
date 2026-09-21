import os
import uuid

from flask import Flask, jsonify, render_template, request, session
import sudoku_logic

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sudoku-development-key')
app.extensions['sudoku_games'] = {}


def get_game_store():
    return app.extensions['sudoku_games']


def validate_board_payload(data):
    if not isinstance(data, dict):
        return None, 'Request must contain a JSON object'
    if 'board' not in data:
        return None, 'JSON must contain a board property'

    board = data['board']
    if (not isinstance(board, list)
            or len(board) != sudoku_logic.SIZE
            or any(not isinstance(row, list) or len(row) != sudoku_logic.SIZE for row in board)):
        return None, 'Board must contain exactly 9 rows of 9 cells'
    if any(type(cell) is not int or not 0 <= cell <= sudoku_logic.SIZE
           for row in board for cell in row):
        return None, 'Board cells must be integers from 0 through 9'
    return board, None


def get_current_game():
    return get_game_store().get(session.get('game_id'))


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty')
    if difficulty is not None:
        difficulty = difficulty.lower()
        if difficulty not in sudoku_logic.DIFFICULTY_CLUES:
            return jsonify({'error': 'Invalid difficulty'}), 400
        puzzle, solution = sudoku_logic.generate_puzzle(difficulty=difficulty)
    else:
        difficulty = 'medium'
        try:
            clues = int(request.args.get('clues', sudoku_logic.MEDIUM_CLUES))
        except (TypeError, ValueError):
            return jsonify({'error': 'Invalid clues value'}), 400
        try:
            puzzle, solution = sudoku_logic.generate_puzzle(clues)
        except ValueError:
            return jsonify({'error': 'Invalid clues value'}), 400

    game_id = uuid.uuid4().hex
    get_game_store()[game_id] = {
        'puzzle': puzzle,
        'solution': solution,
        'hints_used': 0,
        'hinted_cells': set(),
        'completed': False,
    }
    session['game_id'] = game_id
    return jsonify({'puzzle': puzzle, 'difficulty': difficulty})

@app.route('/check', methods=['POST'])
def check_solution():
    if not request.is_json:
        return jsonify({'error': 'Request must contain JSON'}), 400

    board, error = validate_board_payload(request.get_json(silent=True))
    if error:
        return jsonify({'error': error}), 400

    game = get_current_game()
    if game is None:
        return jsonify({'error': 'No game in progress'}), 400

    solution = game['solution']
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    correct = not incorrect
    if correct:
        game['completed'] = True
    return jsonify({'incorrect': incorrect, 'correct': correct})


@app.route('/hint', methods=['POST'])
def get_hint():
    if not request.is_json:
        return jsonify({'error': 'Request must contain JSON'}), 400

    board, error = validate_board_payload(request.get_json(silent=True))
    if error:
        return jsonify({'error': error}), 400

    game = get_current_game()
    if game is None:
        return jsonify({'error': 'No game in progress'}), 400
    if game['completed']:
        return jsonify({'hint': None, 'hints_used': game['hints_used']})

    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if board[row][col] == sudoku_logic.EMPTY:
                game['hinted_cells'].add((row, col))
                game['hints_used'] += 1
                return jsonify({
                    'hint': {'row': row, 'col': col, 'value': game['solution'][row][col]},
                    'hints_used': game['hints_used'],
                })

    return jsonify({'hint': None, 'hints_used': game['hints_used']})

if __name__ == '__main__':
    app.run(debug=True)
import os
import uuid

from flask import Flask, jsonify, render_template, request, session
import sudoku_logic

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sudoku-development-key')
app.extensions['sudoku_games'] = {}


def get_game_store():
    return app.extensions['sudoku_games']

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
        try:
            clues = int(request.args.get('clues', sudoku_logic.MEDIUM_CLUES))
        except (TypeError, ValueError):
            return jsonify({'error': 'Invalid clues value'}), 400
        try:
            puzzle, solution = sudoku_logic.generate_puzzle(clues)
        except ValueError:
            return jsonify({'error': 'Invalid clues value'}), 400

    game_id = uuid.uuid4().hex
    get_game_store()[game_id] = {'puzzle': puzzle, 'solution': solution}
    session['game_id'] = game_id
    return jsonify({'puzzle': puzzle})

@app.route('/check', methods=['POST'])
def check_solution():
    if not request.is_json:
        return jsonify({'error': 'Request must contain JSON'}), 400

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'Request must contain a JSON object'}), 400
    if 'board' not in data:
        return jsonify({'error': 'JSON must contain a board property'}), 400

    board = data['board']
    if (not isinstance(board, list)
            or len(board) != sudoku_logic.SIZE
            or any(not isinstance(row, list) or len(row) != sudoku_logic.SIZE for row in board)):
        return jsonify({'error': 'Board must contain exactly 9 rows of 9 cells'}), 400
    if any(type(cell) is not int or not 0 <= cell <= sudoku_logic.SIZE
           for row in board for cell in row):
        return jsonify({'error': 'Board cells must be integers from 0 through 9'}), 400

    game_id = session.get('game_id')
    game = get_game_store().get(game_id)
    if game is None:
        return jsonify({'error': 'No game in progress'}), 400

    solution = game['solution']
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect, 'correct': not incorrect})

if __name__ == '__main__':
    app.run(debug=True)
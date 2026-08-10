from flask import Flask, render_template, jsonify, request

try:
    from . import sudoku_logic
except ImportError:
    import sudoku_logic

app = Flask(__name__, template_folder='templates', static_folder='static')

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None
}


def _find_empty_cell(board):
    # Return the first empty cell in the board so the hint can fill one square.
    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if board[row][col] == sudoku_logic.EMPTY:
                return row, col
    return None, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty', 'medium').lower()
    if difficulty not in {'easy', 'medium', 'hard'}:
        return jsonify({'error': 'difficulty must be one of: easy, medium, hard'}), 400

    puzzle, solution = sudoku_logic.generate_puzzle(difficulty=difficulty)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    return jsonify({'puzzle': puzzle, 'difficulty': difficulty})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})


@app.route('/hint')
def get_hint():
    puzzle = CURRENT.get('puzzle')
    solution = CURRENT.get('solution')
    if puzzle is None or solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    row, col = _find_empty_cell(puzzle)
    if row is None:
        return jsonify({'error': 'No empty cells left'}), 400

    puzzle[row][col] = solution[row][col]
    return jsonify({'row': row, 'col': col, 'value': solution[row][col], 'locked': True})


if __name__ == '__main__':
    app.run(debug=True)
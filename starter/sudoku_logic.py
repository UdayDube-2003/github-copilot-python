import copy
import random

SIZE = 9
EMPTY = 0

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

def _count_solutions_recursive(board, limit):
    # Find the next empty cell and try each possible value.
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                solutions_found = 0
                for candidate in range(1, SIZE + 1):
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        solutions_found += _count_solutions_recursive(board, limit - solutions_found)
                        board[row][col] = EMPTY
                        if solutions_found >= limit:
                            return limit
                return solutions_found
    return 1


def count_solutions(board, limit=2):
    # Count how many valid completions a puzzle has, stopping early once the limit is reached.
    working_board = deep_copy(board)
    return _count_solutions_recursive(working_board, limit)


def remove_cells(board, clues):
    # Remove cells only when the puzzle still has exactly one valid solution.
    attempts = SIZE * SIZE - clues
    cells = [(row, col) for row in range(SIZE) for col in range(SIZE) if board[row][col] != EMPTY]
    random.shuffle(cells)

    removed = 0
    for row, col in cells:
        if removed >= attempts:
            break

        original_value = board[row][col]
        board[row][col] = EMPTY
        if count_solutions(board) != 1:
            board[row][col] = original_value
        else:
            removed += 1


def generate_puzzle(difficulty="medium"):
    # Map each difficulty to a target number of clues for a 9x9 Sudoku board.
    clue_counts = {
        "easy": 40,
        "medium": 32,
        "hard": 24,
    }

    if difficulty not in clue_counts:
        raise ValueError("difficulty must be one of: easy, medium, hard")

    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clue_counts[difficulty])
    puzzle = deep_copy(board)
    return puzzle, solution

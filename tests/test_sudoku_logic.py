"""Tests for the Sudoku game logic module."""

import pytest

from starter import app as sudoku_app
from starter import sudoku_logic


def is_complete_and_valid(board):
    """Return True when the board is a valid completed Sudoku solution."""
    if len(board) != sudoku_logic.SIZE:
        return False

    expected = set(range(1, sudoku_logic.SIZE + 1))

    for row in board:
        if len(row) != sudoku_logic.SIZE:
            return False
        if set(row) != expected:
            return False

    for col in range(sudoku_logic.SIZE):
        column_values = [board[row][col] for row in range(sudoku_logic.SIZE)]
        if set(column_values) != expected:
            return False

    for box_row in range(0, sudoku_logic.SIZE, 3):
        for box_col in range(0, sudoku_logic.SIZE, 3):
            values = []
            for row in range(box_row, box_row + 3):
                for col in range(box_col, box_col + 3):
                    values.append(board[row][col])
            if set(values) != expected:
                return False

    return True


def test_create_empty_board_returns_a_9x9_grid_of_zeros():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_is_safe_detects_conflicts_in_row_column_and_box():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5
    board[0][1] = 3
    board[1][0] = 6
    board[2][2] = 5

    assert sudoku_logic.is_safe(board, 0, 2, 5) is False
    assert sudoku_logic.is_safe(board, 0, 2, 7) is True
    assert sudoku_logic.is_safe(board, 1, 1, 5) is False
    assert sudoku_logic.is_safe(board, 1, 1, 8) is True


def test_fill_board_creates_a_complete_valid_solution():
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.fill_board(board) is True
    assert is_complete_and_valid(board)


def test_remove_cells_reduces_the_board_to_the_requested_clue_count():
    board = sudoku_logic.create_empty_board()
    sudoku_logic.fill_board(board)

    sudoku_logic.remove_cells(board, 35)
    clue_count = sum(1 for row in board for cell in row if cell != sudoku_logic.EMPTY)

    assert clue_count == 35


def test_count_solutions_returns_one_for_a_completed_board():
    board = sudoku_logic.create_empty_board()
    sudoku_logic.fill_board(board)

    assert sudoku_logic.count_solutions(board) == 1


def test_remove_cells_keeps_the_puzzle_unique():
    board = sudoku_logic.create_empty_board()
    sudoku_logic.fill_board(board)

    sudoku_logic.remove_cells(board, 40)

    assert sudoku_logic.count_solutions(board) == 1


@pytest.mark.parametrize(
    ("difficulty", "expected_min", "expected_max"),
    [
        ("easy", 38, 42),
        ("medium", 30, 34),
        ("hard", 22, 26),
    ],
)
def test_generate_puzzle_returns_a_puzzle_and_full_solution_for_each_difficulty(
    difficulty, expected_min, expected_max
):
    puzzle, solution = sudoku_logic.generate_puzzle(difficulty=difficulty)
    filled_cells = sum(1 for row in puzzle for cell in row if cell != sudoku_logic.EMPTY)

    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert expected_min <= filled_cells <= expected_max
    assert sum(1 for row in solution for cell in row if cell != sudoku_logic.EMPTY) == 81
    assert is_complete_and_valid(solution)
    assert puzzle != solution


def test_hint_endpoint_returns_a_single_correct_cell_and_marks_it_locked():
    sudoku_app.CURRENT['puzzle'] = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]
    sudoku_app.CURRENT['solution'] = [
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

    client = sudoku_app.app.test_client()
    response = client.get('/hint')

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['row'] in range(9)
    assert payload['col'] in range(9)
    assert payload['value'] == sudoku_app.CURRENT['solution'][payload['row']][payload['col']]
    assert payload['locked'] is True

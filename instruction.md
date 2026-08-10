# Project Instructions for GitHub Copilot

## Project Overview
This is a Python Flask web application for a Sudoku game. It has a Python backend (game logic, puzzle generation, validation) and a frontend using HTML, CSS, and JavaScript (rendering the board, handling clicks, timer, dark mode).

## Code Style
- Use clear, descriptive names for functions and variables (e.g. `check_puzzle_solution`, not `chk`).
- Add a short comment above each function explaining what it does.
- Keep functions small and focused on one task.
- Add a comment at the top of each file explaining what the file is for.

## Python Backend
- Follow standard Python style (PEP8): 4 spaces for indentation, snake_case for variable and function names.
- Handle errors with try/except where user input or file/data access is involved.
- Keep game logic (Sudoku generation, validation) separate from Flask route handling.

## Frontend
- Keep JavaScript, CSS, and HTML organized in separate files.
- Use plain CSS with clear class names.
- Make sure the layout works on both desktop and mobile screens.
- Support both light mode and dark mode.

## Testing
- Use pytest for testing Python code.
- Write tests for game logic functions (puzzle generation, validation, checking).

## General
- Explain any code suggestion in simple terms if it uses something advanced, since I am a beginner.
- Prefer simple, readable solutions over clever but hard-to-read code.
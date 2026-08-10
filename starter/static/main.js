// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const STORAGE_KEY = 'sudoku-top-scores';
const DARK_MODE_KEY = 'sudoku-dark-mode';
let puzzle = [];
let timerInterval = null;
let startTime = null;
let hintsUsed = 0;
let currentDifficulty = 'medium';

function formatTime(seconds) {
  const mins = String(Math.floor(seconds / 60)).padStart(2, '0');
  const secs = String(seconds % 60).padStart(2, '0');
  return `${mins}:${secs}`;
}

function updateTimer() {
  if (!startTime) return;
  const elapsed = Math.floor((Date.now() - startTime) / 1000);
  document.getElementById('timer').innerText = `Time: ${formatTime(elapsed)}`;
}

function startTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
  }
  startTime = Date.now();
  updateTimer();
  timerInterval = setInterval(updateTimer, 1000);
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

function getLeaderboard() {
  const raw = localStorage.getItem(STORAGE_KEY);
  return raw ? JSON.parse(raw) : [];
}

function saveLeaderboard(entries) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
}

function renderLeaderboard() {
  const tbody = document.getElementById('leaderboard-body');
  if (!tbody) return;
  const entries = getLeaderboard().sort((a, b) => a.timeSeconds - b.timeSeconds).slice(0, 10);
  tbody.innerHTML = '';
  if (entries.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5">No completed games yet.</td></tr>';
    return;
  }
  entries.forEach((entry, index) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${index + 1}</td>
      <td>${entry.name}</td>
      <td>${formatTime(entry.timeSeconds)}</td>
      <td>${entry.difficulty}</td>
      <td>${entry.hintsUsed}</td>
    `;
    tbody.appendChild(row);
  });
}

function toggleTheme() {
  document.body.classList.toggle('dark-theme');
  const enabled = document.body.classList.contains('dark-theme');
  localStorage.setItem(DARK_MODE_KEY, enabled ? 'true' : 'false');
  const button = document.getElementById('theme-toggle');
  if (button) {
    button.innerText = enabled ? 'Light Mode' : 'Dark Mode';
  }
}

function applySavedTheme() {
  const enabled = localStorage.getItem(DARK_MODE_KEY) === 'true';
  if (enabled) {
    document.body.classList.add('dark-theme');
  } else {
    document.body.classList.remove('dark-theme');
  }
  const button = document.getElementById('theme-toggle');
  if (button) {
    button.innerText = document.body.classList.contains('dark-theme') ? 'Light Mode' : 'Dark Mode';
  }
}
// NOTE: Copilot originally claimed it had added this live-conflict feature
// automatically, but after reviewing the code, no such logic actually existed
// (only digit-filtering was present). I rejected that response and wrote this
// checkLiveConflict function myself to genuinely add the missing behavior.
//
// Checks if a typed number conflicts with any other visible number
// in the same row, column, or 3x3 box, and highlights it red instantly.
function checkLiveConflict(changedInput) {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const row = parseInt(changedInput.dataset.row, 10);
  const col = parseInt(changedInput.dataset.col, 10);
  const value = changedInput.value;

  // Clear this cell's conflict styling first, we will recheck it below
  changedInput.classList.remove('incorrect');

  if (!value) {
    return; // empty cell, nothing to check
  }

  let conflictFound = false;
  const boxRowStart = Math.floor(row / 3) * 3;
  const boxColStart = Math.floor(col / 3) * 3;

  for (let idx = 0; idx < inputs.length; idx++) {
    const other = inputs[idx];
    if (other === changedInput) continue;
    const otherRow = parseInt(other.dataset.row, 10);
    const otherCol = parseInt(other.dataset.col, 10);
    const sameRow = otherRow === row;
    const sameCol = otherCol === col;
    const sameBox =
      otherRow >= boxRowStart && otherRow < boxRowStart + 3 &&
      otherCol >= boxColStart && otherCol < boxColStart + 3;

    if ((sameRow || sameCol || sameBox) && other.value === value) {
      conflictFound = true;
      break;
    }
  }

  if (conflictFound) {
    changedInput.classList.add('incorrect');
  }
}
function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        checkLiveConflict(e.target);
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className += ' prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

async function newGame() {
  const difficultySelect = document.getElementById('difficulty-select');
  const difficulty = difficultySelect ? difficultySelect.value : 'medium';
  currentDifficulty = difficulty;
  hintsUsed = 0;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  renderPuzzle(data.puzzle);
  document.getElementById('message').innerText = '';
  startTimer();
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = 'sudoku-cell';
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    }
  }
  if (incorrect.size === 0) {
    msg.style.color = '#388e3c';
    msg.innerText = 'Congratulations! You solved it!';
    stopTimer();
    const elapsedSeconds = Math.floor((Date.now() - startTime) / 1000);
    const playerName = prompt('You solved it! Enter your name for the leaderboard:');
    if (playerName && playerName.trim()) {
      const entries = getLeaderboard();
      entries.push({
        name: playerName.trim(),
        timeSeconds: elapsedSeconds,
        difficulty: currentDifficulty,
        hintsUsed
      });
      saveLeaderboard(entries.sort((a, b) => a.timeSeconds - b.timeSeconds).slice(0, 10));
      renderLeaderboard();
    }
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  }
}

async function getHint() {
  const res = await fetch('/hint');
  const data = await res.json();
  if (data.error) {
    document.getElementById('message').innerText = data.error;
    return;
  }

  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const idx = data.row * SIZE + data.col;
  const inp = inputs[idx];
  if (inp) {
    inp.value = data.value;
    inp.disabled = true;
    inp.className = 'sudoku-cell prefilled';
    puzzle[data.row][data.col] = data.value;
    hintsUsed += 1;
  }
}

// Wire buttons
window.addEventListener('load', () => {
  applySavedTheme();
  renderLeaderboard();
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint-button').addEventListener('click', getHint);
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  // initialize
  newGame();
});
const SIZE = 9;
const gameState = {
  puzzle: [],
  hintedCells: new Set(),
  completed: false,
  checking: false,
  hintsUsed: 0,
};

function getInputs() {
  return Array.from(document.querySelectorAll('.sudoku-cell'));
}

function getInput(row, col) {
  return document.querySelector(`.sudoku-cell[data-row="${row}"][data-col="${col}"]`);
}

function setMessage(text, color) {
  const message = document.getElementById('message');
  message.innerText = text;
  message.style.color = color;
}

function setControlsDisabled(disabled) {
  document.getElementById('check-solution').disabled = disabled;
  document.getElementById('get-hint').disabled = disabled;
}

function isValidCoordinate(value) {
  return Number.isInteger(value) && value >= 0 && value < SIZE;
}

function isValidHintResponse(data) {
  return data && typeof data === 'object'
    && (data.hint === null || (data.hint && isValidCoordinate(data.hint.row)
      && isValidCoordinate(data.hint.col)
      && Number.isInteger(data.hint.value) && data.hint.value >= 1 && data.hint.value <= 9))
    && Number.isInteger(data.hints_used) && data.hints_used >= 0;
}

function isValidPuzzle(puz) {
  return Array.isArray(puz) && puz.length === SIZE
    && puz.every(row => Array.isArray(row) && row.length === SIZE
      && row.every(value => Number.isInteger(value) && value >= 0 && value <= 9));
}

function getBoard() {
  const inputs = getInputs();
  const board = [];
  for (let row = 0; row < SIZE; row++) {
    board[row] = [];
    for (let col = 0; col < SIZE; col++) {
      const input = inputs[row * SIZE + col];
      board[row][col] = input.value ? Number.parseInt(input.value, 10) : 0;
    }
  }
  return board;
}

function boardIsFull(board) {
  return board.every(row => row.every(value => value >= 1 && value <= 9));
}

function clearMoveFeedback() {
  getInputs().forEach(input => input.classList.remove('conflict'));
}

function findConflictingCells(board) {
  const conflicts = new Set();
  for (let row = 0; row < SIZE; row++) {
    for (let col = 0; col < SIZE; col++) {
      const value = board[row][col];
      if (!value) continue;
      for (let index = 0; index < SIZE; index++) {
        if (index !== col && board[row][index] === value) {
          conflicts.add(row * SIZE + col);
          conflicts.add(row * SIZE + index);
        }
        if (index !== row && board[index][col] === value) {
          conflicts.add(row * SIZE + col);
          conflicts.add(index * SIZE + col);
        }
      }
      const startRow = row - row % 3;
      const startCol = col - col % 3;
      for (let boxRow = startRow; boxRow < startRow + 3; boxRow++) {
        for (let boxCol = startCol; boxCol < startCol + 3; boxCol++) {
          if ((boxRow !== row || boxCol !== col) && board[boxRow][boxCol] === value) {
            conflicts.add(row * SIZE + col);
            conflicts.add(boxRow * SIZE + boxCol);
          }
        }
      }
    }
  }
  return conflicts;
}

function validateMoves() {
  clearMoveFeedback();
  const conflicts = findConflictingCells(getBoard());
  conflicts.forEach(index => getInputs()[index].classList.add('conflict'));
  return conflicts;
}

async function checkForCompletion() {
  const board = getBoard();
  if (boardIsFull(board) && validateMoves().size === 0) {
    await checkSolution();
  }
}

function handleCellInput(event) {
  if (gameState.completed) return;
  const input = event.target;
  input.value = input.value.replace(/[^1-9]/g, '').slice(0, 1);
  input.classList.remove('incorrect');
  validateMoves();
  checkForCompletion();
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
      input.addEventListener('input', handleCellInput);
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  gameState.puzzle = puz;
  gameState.hintedCells = new Set();
  gameState.completed = false;
  gameState.checking = false;
  gameState.hintsUsed = 0;
  createBoardElement();
  const inputs = getInputs();
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puz[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.classList.add('prefilled');
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
  document.getElementById('hint-count').innerText = 'Hints used: 0';
  setControlsDisabled(false);
}

async function newGame() {
  try {
    const res = await fetch('/new');
    const data = await res.json();
    if (!res.ok || !data || !isValidPuzzle(data.puzzle)) {
      throw new Error(data.error || 'Unable to start a new game.');
    }
    renderPuzzle(data.puzzle);
    setMessage('', '');
  } catch (error) {
    setMessage(error.message || 'Unable to start a new game.', '#d32f2f');
  }
}

async function checkSolution() {
  if (gameState.completed || gameState.checking) return;
  gameState.checking = true;
  try {
    const res = await fetch('/check', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({board: getBoard()})
    });
    const data = await res.json();
    if (!res.ok || !data || !Array.isArray(data.incorrect)
        || typeof data.correct !== 'boolean'
        || data.incorrect.some(cell => !Array.isArray(cell) || cell.length !== 2
          || !isValidCoordinate(cell[0]) || !isValidCoordinate(cell[1]))) {
      throw new Error(data && data.error ? data.error : 'Unable to check the board.');
    }
    clearMoveFeedback();
    const incorrect = new Set(data.incorrect.map(cell => cell[0] * SIZE + cell[1]));
    incorrect.forEach(index => getInputs()[index].classList.add('incorrect'));
    if (data.correct) {
      completeGame();
    } else {
      setMessage('Some cells are incorrect.', '#d32f2f');
    }
  } catch (error) {
    setMessage(error.message || 'Unable to check the board.', '#d32f2f');
  } finally {
    gameState.checking = false;
  }
}

function completeGame() {
  if (gameState.completed) return;
  gameState.completed = true;
  getInputs().forEach(input => { input.disabled = true; });
  setControlsDisabled(true);
  setMessage('Congratulations! You solved it!', '#388e3c');
}

async function getHint() {
  if (gameState.completed) return;
  try {
    const res = await fetch('/hint', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({board: getBoard()})
    });
    const data = await res.json();
    if (!res.ok || !isValidHintResponse(data)) {
      throw new Error(data && data.error ? data.error : 'Unable to get a hint.');
    }
    gameState.hintsUsed = data.hints_used;
    document.getElementById('hint-count').innerText = `Hints used: ${gameState.hintsUsed}`;
    if (data.hint === null) {
      setMessage('There are no empty cells left for a hint.', '#d32f2f');
      return;
    }
    const {row, col, value} = data.hint;
    const input = getInput(row, col);
    if (!input || input.value) {
      throw new Error('The server returned an invalid hint.');
    }
    input.value = value;
    input.disabled = true;
    input.classList.add('hinted');
    gameState.hintedCells.add(row * SIZE + col);
    validateMoves();
    await checkForCompletion();
  } catch (error) {
    setMessage(error.message || 'Unable to get a hint.', '#d32f2f');
  }
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('get-hint').addEventListener('click', getHint);
  newGame();
});
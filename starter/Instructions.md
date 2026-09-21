# Sudoku Project Instructions

## Project Goal

This project is a refactoring of a legacy Python Sudoku application into a
clean, maintainable Flask web application with additional gameplay features.

The application must provide:

- Easy, Medium, and Hard difficulty levels
- Sudoku puzzles with exactly one unique solution
- Locked prefilled cells
- Invalid-move feedback
- Check functionality
- Hint functionality
- A game timer
- Dark/light mode
- A persistent Top 10 leaderboard using browser local storage
- A completion message when the puzzle is solved correctly

## Code Quality

- Prefer clean, readable, modular, and maintainable code.
- Follow modern Python practices.
- Keep responsibilities separated between Flask routes, Sudoku/game logic,
  frontend JavaScript, HTML templates, and CSS.
- Avoid unnecessary duplication.
- Use descriptive variable and function names.
- Keep functions focused on one responsibility.
- Add comments only where they improve understanding of non-obvious logic.
- Include appropriate error handling.
- Do not introduce unnecessary dependencies.

## Sudoku Logic

- Every generated puzzle must have exactly one valid solution.
- Difficulty should control the number of prefilled cells.
- Prefilled cells must not be editable by the player.
- Player moves must be validated against Sudoku rules.
- The application should provide clear feedback for invalid moves.
- Sudoku logic should be testable independently from the Flask UI.

## Frontend

- Use semantic and readable HTML.
- Keep JavaScript modular and understandable.
- Make the application responsive for desktop and mobile screens.
- The 3x3 Sudoku regions must have visually distinguishable alternating
  styling without changing the board layout.
- Support both light and dark modes.
- Ensure text, buttons, and controls remain readable in both modes.

## Testing

- Use automated tests for core Sudoku logic and important application
  functionality.
- Run the test suite after significant refactors or feature changes.
- Do not remove or weaken existing tests merely to make them pass.
- When changing behavior, update or add appropriate tests.

## Copilot Usage

- Before making significant changes, explain the proposed approach.
- Prefer small, reviewable changes instead of rewriting unrelated code.
- Do not modify unrelated functionality.
- If a suggestion conflicts with the project requirements, explain the issue
  and propose an alternative.
- Favor maintainability and correctness over unnecessary complexity.

## Important Development Rule

Do not assume that generated code is correct.

Review, test, and evaluate Copilot-generated suggestions before accepting them.
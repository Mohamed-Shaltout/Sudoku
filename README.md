# Sudoku Solver with AC-3 Algorithm and GUI

This project is a Sudoku solver implemented in Python using the AC-3 (Arc Consistency Algorithm #3) for constraint propagation and backtracking for solving the puzzle. The solver is equipped with a graphical user interface (GUI) built using the `tkinter` library, allowing users to interactively solve Sudoku puzzles or watch the solver in action.

## Features

- **AC-3 Algorithm**: Implements the AC-3 algorithm for constraint propagation to reduce the search space before applying backtracking.
- **Backtracking with Forward Checking**: Uses backtracking with forward checking to solve the Sudoku puzzle efficiently.
- **Interactive GUI**: Provides a user-friendly interface for solving Sudoku puzzles interactively or automatically.
- **Multiple Modes**:
  - **Input Mode**: Allows users to input their own Sudoku puzzle.
  - **Solve Mode**: Automatically solves a randomly generated Sudoku puzzle based on the selected difficulty level (Easy, Medium, Hard, Expert).
  - **Interactive Mode**: Allows users to solve the puzzle interactively with real-time validation.
- **Visualization**: Displays the arc consistency tree and updates the GUI in real-time as the solver progresses.

## Requirements

- Python 3.x
- `tkinter` (usually comes pre-installed with Python)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/sudoku-solver.git

import tkinter as tk
from collections import deque
from time import sleep
from tkinter import messagebox
import random
import time
import random
from tkinter import ttk
def show_arc_tree_gui(root, arcs):
    # Create a new window to display the arc consistency tree
    tree_window = tk.Toplevel(root)
    tree_window.title("Arc Consistency Tree")
    
    # Create a Treeview widget to display the arcs and constraints
    tree = ttk.Treeview(tree_window, columns=("Arc", "Domains"), show="headings")
    tree.heading("Arc", text="Arc")
    tree.heading("Domains", text="Domains")
    
    # Insert the arcs and their corresponding domains
    for arc, domain in arcs.items():
        tree.insert("", "end", values=(str(arc), str(domain)))
    
    tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
def forward_check(domains, cell, value):
    updates = []
    for neighbor in NEIGHBORS_CACHE[cell]:
        if value in domains[neighbor]:
            domains[neighbor].remove(value)
            updates.append((neighbor, value))
            if not domains[neighbor]:  
                return False, updates
    return True, updates

def restore_domains(domains, updates):
    for cell, value in updates:
        domains[cell].add(value)
def generate_random_sudoku(difficulty):
    def is_valid(board, num, row, col):
        for i in range(9):
            if board[row][i] == num or board[i][col] == num:
                return False

        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if board[start_row + i][start_col + j] == num:
                    return False
        return True

    def solve(board):
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    random.shuffle(numbers)
                    for num in numbers:
                        if is_valid(board, num, row, col):
                            board[row][col] = num
                            if solve(board):
                                return True
                            board[row][col] = 0
                    return False
        return True

    def remove_numbers(board, clues):
        count = 81 - clues
        while count > 0:
            row, col = random.randint(0, 8), random.randint(0, 8)
            if board[row][col] != 0:
                board[row][col] = 0
                count -= 1

    clues_dict = {
        "easy": 35,
        "medium": 31,
        "hard": random.randint(22, 27),
        "expert": 17
    }

    if difficulty.lower() not in clues_dict:
        raise ValueError("Invalid difficulty level. Choose from 'easy', 'medium', 'hard', or 'expert'.")

    clues = clues_dict[difficulty.lower()]

    board = [[0 for _ in range(9)] for _ in range(9)]
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    solve(board)

    remove_numbers(board, clues)

    return [cell for row in board for cell in row]


def is_solved(board):
    if 0 in board:
        return False
    
    for i in range(9):
        row = board[i * 9:(i + 1) * 9]
        if len(set(row)) != 9:  
            return False
        col = [board[j * 9 + i] for j in range(9)]
        if len(set(col)) != 9: 
            return False
        

        box_row, box_col = (i // 3) * 3, (i % 3) * 3
        box = [board[box_row * 9 + box_col], board[box_row * 9 + box_col + 1], board[box_row * 9 + box_col + 2],
               board[(box_row + 1) * 9 + box_col], board[(box_row + 1) * 9 + box_col + 1], board[(box_row + 1) * 9 + box_col + 2],
               board[(box_row + 2) * 9 + box_col], board[(box_row + 2) * 9 + box_col + 1], board[(box_row + 2) * 9 + box_col + 2]]
        if len(set(box)) != 9:  
            return False
    
    return True

# AC-3 Algorithm
def arc_consistency(board,root):
    domains = {(r, c): set(range(1, 10)) if board[r * 9 + c] == 0 else {board[r * 9 + c]} for r in range(9) for c in range(9)}
    arcs = deque([(cell, neighbor) for cell in domains for neighbor in neighbors(cell)])
    arc_domains = {}
    while arcs:
        cell, neighbor = arcs.popleft()
        if revise(domains, cell, neighbor):
            arc_domains[(cell, neighbor)] = (domains[cell], domains[neighbor])
            if not domains[cell]:
                return None
            for other_neighbor in neighbors(cell):
                if other_neighbor != neighbor:
                    arcs.append((other_neighbor, cell))
    show_arc_tree_gui(root, arc_domains)
    return domains

def revise(domains, cell, neighbor):
    revised = False
    for value in set(domains[cell]):
        if value in domains[neighbor] and len(domains[neighbor]) == 1:
            domains[cell].remove(value)
            revised = True
    return revised

def neighbors(cell):
    row, col = cell
    neighbors = set()
    neighbors.update((row, c) for c in range(9) if c != col)
    neighbors.update((r, col) for r in range(9) if r != row)
    box_row, box_col = row // 3 * 3, col // 3 * 3
    neighbors.update((r, c) for r in range(box_row, box_row + 3) for c in range(box_col, box_col + 3) if (r, c) != cell)
    return neighbors
NEIGHBORS_CACHE = {cell: neighbors(cell) for cell in [(r, c) for r in range(9) for c in range(9)]}

def solve_with_ac3(board,root, update_gui):
    domains = arc_consistency(board,root)
    if domains is None:
        return False
    return backtracking_with_domains(board, domains, update_gui)


def backtracking_with_domains(board, domains, update_gui):
    empty = find_empty(board, domains)
    if not empty:
        return True

    row, col = empty
    cell = (row, col)
    possible_values = sorted(domains[cell], key=lambda v: count_constraints(board, row, col, v, domains))

    for value in possible_values:
        if valid(board, value, cell):
            board[row * 9 + col] = value
            update_gui(board, row, col, value, "forward")
            
            # Apply forward checking
            success, updates = forward_check(domains, cell, value)
            if success:
                if backtracking_with_domains(board, domains, update_gui):
                    return True

            restore_domains(domains, updates)
            board[row * 9 + col] = 0
            update_gui(board, row, col, 0, "backward")

    return False

def count_constraints(board, row, col, value,domains):
    """Count constraints introduced by assigning a value."""
    count = 0

    for r, c in neighbors((row, col)):
        if board[r * 9 + c] == 0 and value in domains[(r, c)]:
            count += 1
    return count


def find_empty(board, domains):
    min_domain_size = float('inf')
    best_cell = None

    for i in range(len(board)):
        if board[i] == 0:  
            row, col = i // 9, i % 9
            domain_size = len(domains[(row, col)])
            if domain_size < min_domain_size:
                min_domain_size = domain_size
                best_cell = (row, col)
    
    return best_cell

def valid(board, num, pos):
    row, col = pos
    for i in range(9):
        if board[row * 9 + i] == num and col != i:
            return False
    for i in range(9):
        if board[i * 9 + col] == num and row != i:
            return False
    box_row, box_col = row // 3 * 3, col // 3 * 3
    for i in range(box_row, box_row + 3):
        for j in range(box_col, box_col + 3):
            if board[i * 9 + j] == num and (i, j) != (row, col):
                return False
    return True

def print_board(board):
    for i in range(9):
        row = board[i * 9:(i + 1) * 9]
        print(" ".join(str(x) if x != 0 else "." for x in row))
    print("\n")

def get_board_from_input():
    board = []
    print("Please enter the Sudoku board row by row (9 digits, use 0 for empty cells):")
    for i in range(9):
        while True:
            row = input(f"Row {i+1}: ")
            if len(row) == 9 and all(c.isdigit() and (0 <= int(c) <= 9) for c in row):
                board.extend([int(c) for c in row])
                break
            else:
                print("Invalid input. Please enter exactly 9 digits (0 for empty cells).")
    return board

def create_gui(board, mode):
    root = tk.Tk()
    root.title("Sudoku Solver")

    def validate_input(value):
        return value.isdigit() and 1 <= int(value) <= 9 or value == ""

    validate_cmd = root.register(validate_input)

    cells = []
    for i in range(9):
        row = []
        for j in range(9):
            entry = tk.Entry(
                root, width=4, font=("Arial", 18), justify="center", borderwidth=1, relief="solid",
                validate="key", validatecommand=(validate_cmd, "%P")
            )
            entry.grid(row=i, column=j, padx=2, pady=2)

            if mode == "interactive":
                entry.bind("<Return>", lambda e, r=i, c=j: check_interactive_input(r, c))

            row.append(entry)
        cells.append(row)

    def initialize_gui(board):
        for i in range(9):
            for j in range(9):
                value = board[i * 9 + j]
                if value != 0:
                    cells[i][j].insert(0, str(value))
                    if mode == "interactive":
                        cells[i][j].config(state="disabled", disabledforeground="black")

    def get_board():
        return [int(cell.get()) if cell.get().isdigit() else 0 for row in cells for cell in row]

    def check_interactive_input(row, col):
        value = cells[row][col].get()
        if value.isdigit():
            num = int(value)
            board = get_board()
            if valid(board, num, (row, col)):
                cells[row][col].config(bg="lightgreen")
            else:
                messagebox.showerror("Invalid Entry", f"Number {value} violates Sudoku constraints!")
                cells[row][col].delete(0, tk.END)
                cells[row][col].config(bg="pink")
        else:
            cells[row][col].config(bg="white")

        if is_solved(board):
            messagebox.showinfo("Puzzle Solved!", "Congratulations! You have solved the puzzle.")
            for row in cells:
                for cell in row:
                    cell.config(state="disabled")  


    def update_gui(board, row, col, value, action):
        bg_color = "lightgreen" if action == "forward" else "pink"
        cells[row][col].delete(0, tk.END)
        if value != 0:
            cells[row][col].insert(0, str(value))
        cells[row][col].config(bg=bg_color)
        root.update_idletasks()
        root.update()

    def start_solver():
        """Start solving in Solve Mode."""
        timer_label = tk.Label(root, text="Time: 0s", font=("Arial", 14), bg="lightblue")
        timer_label.grid(row=11, column=0, columnspan=9, pady=10)
        start_time = time.time()
        board = get_board()
        if solve_with_ac3(board,root, update_gui):
            end_time = time.time()
            elapsed_time = end_time - start_time
            timer_label.config(text=f"Time: {elapsed_time:.2f}s")
            messagebox.showinfo("Sudoku Solver", f"Sudoku solved successfully in {elapsed_time:.2f} seconds!")
        else:
            messagebox.showerror("Sudoku Solver", "The Sudoku puzzle is unsolvable!")

    def restart_game():
        """Restart the game."""
        for row in cells:
            for cell in row:
                cell.delete(0, tk.END)
                cell.config(bg="white", state="normal")
        initialize_gui(board)

    if mode == "solve":
        solve_button = tk.Button(root, text="Solve", command=start_solver, font=("Arial", 14))
        solve_button.grid(row=10, column=0, columnspan=4, pady=10)

    tk.Button(root, text="Restart", command=restart_game, font=("Arial", 14)).grid(row=10, column=4, columnspan=5, pady=10)

    initialize_gui(board)
    root.mainloop()



def mode_selection_gui():
    root = tk.Tk()
    root.title("Select Mode")

    window_width = 400
    window_height = 300
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_top = (screen_height // 2) - (window_height // 2)
    position_right = (screen_width // 2) - (window_width // 2)
    root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
    root.resizable(False, False)

    frame = tk.Frame(root, bg="lightblue", padx=20, pady=20)
    frame.pack(expand=True, fill=tk.BOTH)

    info_label = tk.Label(frame, text="Choose a mode to start the Sudoku Solver:", font=("Arial", 12, "bold"), bg="lightblue")
    info_label.pack(pady=20)

    button_style = {
        "font": ("Arial", 14),
        "width": 20,  
        "height": 2,  
        "relief": "raised",
        "bd": 2,
        "highlightthickness": 0
    }

    def on_hover(event):
        event.widget.config(bg="lightblue")

    def on_leave(event):
        event.widget.config(bg=event.widget.default_bg)

    def select_input_mode():
        root.destroy()
        board = get_board_from_input()  
        create_gui(board, mode="solve")

    def select_solve_mode():
        def start_game():
            difficulty = difficulty_var.get().lower()
            difficulty_root.destroy()
            board = generate_random_sudoku(difficulty)  
            create_gui(board, mode="solve")

        root.destroy()
        difficulty_root = tk.Tk()
        difficulty_root.title("Select Difficulty")
        difficulty_root.geometry("400x200")

        tk.Label(difficulty_root, text="Choose Difficulty Level:", font=("Arial", 14, "bold")).pack(pady=20)

        difficulty_var = tk.StringVar(value="Easy")
        difficulties = ["Easy", "Medium", "Hard", "Expert"]
        for diff in difficulties:
            tk.Radiobutton(difficulty_root, text=diff, variable=difficulty_var, value=diff, font=("Arial", 12)).pack(anchor="w")

        tk.Button(difficulty_root, text="Start Game", command=start_game, **button_style).pack(pady=20)

        difficulty_root.mainloop()

    def select_mode3():
        def generate_random_board(difficulty):
            root2.destroy()
            random_board = generate_random_sudoku(difficulty)  
            create_gui(random_board, mode="interactive")

        def input_custom_board():
            root2.destroy()
            user_board = get_board_from_input()
            create_gui(user_board, mode="interactive")

        root.destroy()
        root2 = tk.Tk()
        root2.title("Mode 3 - Board Selection")
        root2.geometry("400x300")  

        tk.Label(root2, text="Select a Board Source:", font=("Arial", 14, "bold")).pack(pady=20)

        difficulty_frame = tk.Frame(root2)
        difficulty_frame.pack(pady=10)

        tk.Label(difficulty_frame, text="Select Difficulty Level:", font=("Arial", 12, "bold")).pack(pady=10)

        def start_game_with_difficulty(difficulty):
            generate_random_board(difficulty)  

        difficulties = ["Easy", "Medium", "Hard", "Expert"]
        for diff in difficulties:
            tk.Button(difficulty_frame, text=diff, command=lambda d=diff: start_game_with_difficulty(d),
                    font=("Arial", 12), width=20, height=2, relief="raised", bd=2).pack(pady=5)

        input_button = tk.Button(root2, text="Input Custom Board", command=input_custom_board, **button_style)
        input_button.default_bg = "lightcoral"
        input_button.config(bg="lightcoral")
        input_button.pack(pady=10)
        input_button.bind("<Enter>", on_hover)
        input_button.bind("<Leave>", on_leave)

        root2.mainloop()


    input_button = tk.Button(frame, text="Input Mode", command=select_input_mode, **button_style)
    input_button.default_bg = "lightcoral"
    input_button.config(bg="lightcoral")
    input_button.pack(pady=10)
    input_button.bind("<Enter>", on_hover)
    input_button.bind("<Leave>", on_leave)

    solve_button = tk.Button(frame, text="Solve Mode", command=select_solve_mode, **button_style)
    solve_button.default_bg = "lightgreen"
    solve_button.config(bg="lightgreen")
    solve_button.pack(pady=10)
    solve_button.bind("<Enter>", on_hover)
    solve_button.bind("<Leave>", on_leave)

    mode3_button = tk.Button(frame, text="Interactive", command=select_mode3, **button_style)
    mode3_button.default_bg = "lightblue"
    mode3_button.config(bg="lightblue")
    mode3_button.pack(pady=10)
    mode3_button.bind("<Enter>", on_hover)
    mode3_button.bind("<Leave>", on_leave)

    root.mainloop()
    

if __name__ == "__main__":
    mode_selection_gui()
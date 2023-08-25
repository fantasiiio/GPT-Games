from memory_profiler import profile
import multiprocessing
import concurrent.futures
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
import pickle
from multiprocessing import Process, Manager
from multiprocessing import Pool, cpu_count
import pygame.gfxdraw  # Import the gfxdraw module
import math
import sys
import numpy as np
import pygame
import random
from MCTS import MCTS, Node
import numpy as np
from Connect4Node import Connect4Node
from tqdm import tqdm
from multiprocessing import  Queue

class DefaultDictManager:
    def __init__(self, default_factory, manager_dict=None):
        self.default_factory = default_factory
        self.manager_dict = manager_dict if manager_dict is not None else Manager().dict()

    def __getitem__(self, key):
        if key not in self.manager_dict:
            self.manager_dict[key] = self.default_factory()
        return self.manager_dict[key]

    def __setitem__(self, key, value):
        self.manager_dict[key] = value

    def __delitem__(self, key):
        del self.manager_dict[key]

    def keys(self):
        return self.manager_dict.keys()

    def values(self):
        return self.manager_dict.values()

    def items(self):
        return self.manager_dict.items()
    
class Game:
    def __init__(self):
        self.ROW_COUNT = 6
        self.COLUMN_COUNT = 7
        self.PLAYER = 1
        self.AI = 2
        self.EMPTY = 0
        self.board = self.create_board()
        self.board_history = []
        self.game_over = False
        self.node = Connect4Node(self.board, self.PLAYER, False, 0)
        self.iterations = 100
        self.start_iterations = self.iterations

    def create_board(self):
        return np.zeros((self.ROW_COUNT, self.COLUMN_COUNT), int)

    def drop_piece(self, board, row, col, piece):
        board[row][col] = piece

    def is_valid_location(self, board, col):
        return board[self.ROW_COUNT-1][col] == 0

    def get_next_open_row(self, board, col):
        for r in range(self.ROW_COUNT):
            if board[r][col] == 0:
                return r

    def check_winner(self,board, piece):
        for c in range(self.COLUMN_COUNT - 3):
            for r in range(self.ROW_COUNT):
                if board[r][c] == board[r][c+1] == board[r][c+2] == board[r][c+3] == piece:
                    return True
        for c in range(self.COLUMN_COUNT):
            for r in range(self.ROW_COUNT - 3):
                if board[r][c] == board[r+1][c] == board[r+2][c] == board[r+3][c] == piece:
                    return True
        for c in range(self.COLUMN_COUNT - 3):
            for r in range(self.ROW_COUNT - 3):
                if board[r][c] == board[r+1][c+1] == board[r+2][c+2] == board[r+3][c+3] == piece:
                    return True
        for c in range(self.COLUMN_COUNT - 3):
            for r in range(3, self.ROW_COUNT):
                if board[r][c] == board[r-1][c+1] == board[r-2][c+2] == board[r-3][c+3] == piece:
                    return True


    def get_available_moves(self, board):
        return [c for c in range(self.COLUMN_COUNT) if self.is_valid_location(board, c)]

    def is_terminal(self, valid_moves):
        return len(valid_moves) == 0 or self.check_winner(self.board, self.PLAYER) or self.check_winner(self.board, self.AI)

    def end_game(self, winner):
        if winner == self.PLAYER:
            print("Player wins!")
        elif winner == self.AI:
            print("AI wins!")
        else:
            print("Tie game!")

    def calculate_iterations(self, board, initial_iterations):
        rows, cols = board.shape
        total_cells = rows * cols
        filled_cells = np.count_nonzero(board)
        fraction_filled = filled_cells / total_cells
        iterations = int(initial_iterations * (1 - fraction_filled))
        return iterations
    
    def run(self):
        board = self.board
        game_over = False
        turn = self.PLAYER

        while not game_over:
            if turn == self.PLAYER:
                i = input(f"Enter your move (0-{self.COLUMN_COUNT-1} i): ")
                if not (i.isdigit() and 0 <= int(i) <= 6 or i == "i"):
                    print("Invalid input.")
                    continue
                if(i == 'i'):
                    i = input(f"Iterations count: ")
                    self.iterations = int(i)
                    continue
                else:
                    col = int(i)

                if self.is_valid_location(board, col):
                    row = self.get_next_open_row(board, col)
                    self.drop_piece(board, row, col, self.PLAYER)
                    self.node.update_node(board, col, self.PLAYER)
                    # Add the current board state to the history
                    self.board_history.append(board.copy())

                    if self.check_winner(board, self.PLAYER):
                        self.end_game(self.PLAYER)
                        game_over = True

                turn = self.AI
            else:
                if turn == self.AI and not game_over:
                    # self.iterations = self.calculate_iterations(board, self.start_iterations)
                    col = self.get_mcts_move_single()
                    if self.is_valid_location(board, col):
                        row = self.get_next_open_row(board, col)
                        self.drop_piece(board, row, col, self.AI)

                        # Add the current board state to the history
                        self.board_history.append(board.copy())

                        if self.check_winner(board, self.AI):
                            self.end_game(self.AI)
                            game_over = True

                turn = self.PLAYER

            if len([c for c in range(self.COLUMN_COUNT) if self.is_valid_location(board, c)]) == 0:
                self.end_game(0)
                game_over = True

            draw_text_board(board)

        
            
    def get_mcts_move_single(self):
        mcts = MCTS()
        # iterations = 10000
        
        for _ in tqdm(range(self.iterations), desc="Running MCTS"):
            mcts.do_rollout(self.node)

        # mcts.propagate_win_count_root()
        mcts.draw_tree(self.node)

        self.node = mcts.choose(self.node)
        column_number = self.node.last_move        
        return column_number


    def parallel_mcts_multi(self, iterations, column):
        mcts = MCTS()
        
        node = self.node.create_from_existing(self.node)
        row = self.get_next_open_row(self.board, column)
        node.board[row][column] = self.AI  # Assuming self.AI is the AI player's piece
        node.history = node.history + [column]
        node.last_move = column
        node.update_game_state()
        # node = Connect4Node(initial_board, self.PLAYER, False, None)
        for _ in tqdm(range(iterations), desc="Running MCTS"):
            mcts.do_rollout(node)
        node.update_game_state()
        return mcts


    def get_mcts_move_multi(self):
        iterations = 400
        iterations_per_process = iterations

        mcts_results = []
        valid_columns = self.get_available_moves(self.board)
        process_count = len(valid_columns)

        with multiprocessing.Pool(process_count) as pool:
            mcts_results = pool.starmap(self.parallel_mcts_multi, [(iterations_per_process, col) for col in valid_columns])
            # mcts_results.append(mcts)

        # Create a new parent node representing the current state of the board
        parent_node = Connect4Node(self.board, self.PLAYER)

        # Merge only the root nodes of each MCTS and add them as children to the parent node
        for mcts in mcts_results:
            root_node = list(mcts.mcts_results.keys())[0]  # Get the root node of each MCTS
            if parent_node.children:
                same = list(parent_node.children)[0] == root_node
            parent_node.children.add(root_node)

        # Create a new MCTS instance with the parent node as the root
        mcts = MCTS()
        mcts.mcts_results[parent_node] = parent_node.children

        # Continue the rest of your code...
        mcts.propagate_win_count_root()
        # mcts.draw_tree(None, color_func=self.custom_color, label_func=lambda node: f"m{node.value.last_move} 1:{node.value.win_count[1]} 2:{node.value.win_count[2]} d:{node.value.win_delta} \nQ: {node.value.Q} N: {node.value.N}\nid:{node.value.id}")

        self.node = mcts.choose(parent_node)
        column_number = self.node.last_move        
        return column_number




def draw_text_board(board):
    ROW_COUNT = board.shape[0]
    COLUMN_COUNT = board.shape[1]

    for r in range(ROW_COUNT - 1, -1, -1):
        row_string = "|"
        for c in range(COLUMN_COUNT):
            piece = board[r][c]
            if piece == 0:
                row_string += " . "
            elif piece == 1:
                row_string += " X "
            elif piece == 2:
                row_string += " O "
            row_string += "|"
        print(row_string)
    print("+" + "---+" * COLUMN_COUNT)
    print(" " + " ".join([f" {i} " for i in range(COLUMN_COUNT)]))

if __name__ == "__main__":
    game = Game()
    game.run()


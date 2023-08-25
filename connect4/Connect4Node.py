from functools import lru_cache
import math
from memory_profiler import profile
from MCTS import Node
import numpy as np
import random
from collections import defaultdict
import itertools
import time
import os

gen = itertools.count(1)
step = itertools.count(1)

SHIFT_VALUES = [[2 * (row * 7 + col) for col in range(7)] for row in range(7)]

class Connect4Node(Node):
    def __init__(self, board = None, player = 1, is_terminal = False, reward = 0, last_move=None, history=[], winner=None, resnet = None):
        if board is not None:
            type = self.detect_board_type(board)
            if(type == "ndarray"):
                self.board = self.board_to_int(board)
            elif(type.startswith("int")):
                self.board = board
        self.player = player
        self._is_terminal = is_terminal
        self._reward = reward
        self.last_move = last_move
        self.history = history if history is not None else []  
        self.history = history.copy() 
        self.children = []
        self.winner = winner
        self.Q = 0
        self.N = 0
        self.visited = False
        self.win_count = {1: 0, 2: 0}
        self.visit_count = 0
        self.depth = -1
        self.simulation_paths = dict()

    def update_node(self, board, last_move, new_player, winner=None):
        if board is not None:
            type = self.detect_board_type(board)
            if(type == "ndarray"):
                self.board = self.board_to_int(board)
            elif(type.startswith("int")):
                self.board = board
        self.player = new_player
        self.last_move = last_move
        self.history.append(last_move)
        self.winner = winner

    def create_from_existing(self, existing_node, resnet):
        # Create a new node with attributes from the existing node
        new_node = Connect4Node(board=existing_node.board.copy(),
                                player=existing_node.player,
                                is_terminal=existing_node._is_terminal,
                                reward=existing_node._reward,
                                last_move=existing_node.last_move,
                                history=existing_node.history.copy(),
                                winner=existing_node.winner,
                                resnet=resnet)
        return new_node        


    def detect_board_type(self, board):
        return type(board).__name__

    def int_to_board(self, board_int):
        rows, cols = 6, 7
        board = np.zeros((rows, cols), dtype=np.int8)
        mask = 0b11  # Mask to extract 2 bits
        
        for row in range(rows):
            for col in range(cols):
                # Calculate the position of the bits in the integer
                pos = 2 * ((rows - row - 1) * cols + col)
                # Extract the bits for the current cell and assign it to the board
                board[row, col] = (board_int >> pos) & mask
        
        return board

    def board_to_int(self, board):
        """Convert a board from numpy array format to integer format."""
        board_int = 0
        for row in range(board.shape[0]):
            for col in range(board.shape[1]):
                value = board[row, col]
                mask = value << (2 * (row * 7 + col))
                board_int |= mask
        return board_int            


    @lru_cache(maxsize=None)
    def get_cell(self, row, col):
        mask = 0b11 << SHIFT_VALUES[row][col]
        return (int(self.board) & int(mask)) >> SHIFT_VALUES[row][col]
        
    def set_cell(self, row, col, value):
        mask = 0b11 << (2 * (row * 7 + col))
        board = (self.board & ~mask) | (value << (2 * (row * 7 + col)))
        self.board = int(board)

    def drop_piece(self, col, piece):
        row = self.get_next_open_row(col)
        self.set_cell(row, col, piece)

    def get_next_open_row(self, col):
        for r in range(6):
            if self.get_cell(r,col) == 0:
                return r

    def create_children(self):
        if self.is_terminal():
            return []
        for col in range(7):
            if self.get_cell(5, col) == 0:
                new_board = self.board
                for row in range(6):
                    if self.get_cell(row, col) == 0:
                        id = next(gen)
                        new_history = self.history + [col]                             
                        new_node = Connect4Node(board=new_board, player=3 - self.player, last_move=col, history=new_history, winner=self.winner)
                        if(not hasattr(new_node, "board")):
                            new_node = Connect4Node(board=new_board, player=3 - self.player)
                        new_node.set_cell(row, col, self.player)
                        is_terminal, player_win = new_node.check_terminal(row, col)
                        new_node.winner = self.player if is_terminal and player_win else None
                        new_node._is_terminal = is_terminal
                        self.children.append(new_node)
                        break
        return self.children

    def check_terminal(self, row, col):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            for i in range(1, 4):
                r, c = row + dr * i, col + dc * i
                if 0 <= r < 6 and 0 <= c < 7 and self.get_cell(r,c) == self.player:
                    count += 1
                else:
                    break
            for i in range(1, 4):
                r, c = row - dr * i, col - dc * i
                if 0 <= r < 6 and 0 <= c < 7 and self.get_cell(r,c) == self.player:
                    count += 1
                else:
                    break
            if count >= 4:
                return True, True
        if self.is_board_full():
            return True, False
        return False, False

    def is_board_full(self):
        mask = 0b11  # Binary mask for two bits
        for i in range(42):  # Total cells in a 6x7 board
            cell_value = (self.board >> (2 * i)) & mask
            if cell_value == 0:
                return False
        return True
    
    def is_terminal(self):
        return self._is_terminal

    def reward(self):
        return self._reward

    def __eq__(self, other):
        if isinstance(other, Connect4Node):
            return self.board == other.board and self.history == other.history
        return False

    def __hash__(self):
        return hash((self.board, tuple(self.history)))
    
    def get_valid_moves(self, board_int):
        rows, cols = 6, 7
        valid_moves = []

        for child in self.children:
            col = child.last_move
            # Check if the top cell of the column is empty
            if self.get_cell(rows-1, col) == 0:
                valid_moves.append(child)

        return valid_moves

    def find_random_child(self):
        if self.is_terminal():
            return None
        if not self.children:
            self.create_children()
            return random.choice(self.children)
        else:
            available_moves = self.get_valid_moves(self.board)
            best_child = self._uct_select(available_moves)
            return best_child
    
    def _uct_select(self, nodeList):
        total_simulations = sum(child.N for child in nodeList) + 1e-6  # Avoid division by zero
        total_score = sum(child.Q for child in nodeList)
        total_score_avg = total_score / total_simulations

        def uct(n):
            if n.N == 0:
                return float("inf")
            Q = n.Q if n.player == 2 else -n.Q
            exploitation_value = Q / n.N
            if total_simulations > 0 and n.N > 0:
                exploration_value = total_score_avg * math.sqrt(math.log(total_simulations) / n.N)
            else:
                exploration_value = 0
                
            return exploitation_value + exploration_value
        scores = [uct(child) for child in nodeList]
        return max(nodeList, key=uct)

    #  function calculates the total of a player's specific sequences on a game board.
    #  Valid patterns are considered if they are open-ended.
    #  The result is the total count of such valid patterns.
    def count_patterns(self, board_int, player, length, marked=None):
        count = 0
        rows, cols = 6, 7
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # (dx, dy) for horizontal, vertical, and both diagonals

        if marked is None:
            marked = np.zeros((rows, cols), dtype=bool)

        for dx, dy in directions:
            for i in range(rows):
                for j in range(cols):
                    if marked[i, j] or i + (length - 1) * dx >= rows or j + (length - 1) * dy < 0 or j + (length - 1) * dy >= cols:
                        continue

                    pattern = [self.get_cell(i + k * dx, j + k * dy) for k in range(length)]
                    if all(p == player for p in pattern):
                        start_x, start_y = i - dx, j - dy
                        end_x, end_y = i + length * dx, j + length * dy
                        if (0 <= start_x < rows and 0 <= start_y < cols and self.get_cell(start_x, start_y) == 0) or (0 <= end_x < rows and 0 <= end_y < cols and self.get_cell( end_x, end_y) == 0):
                            count += 1
                            for k in range(length):
                                marked[i + k * dx, j + k * dy] = True
            
        return count, marked


    def evaluate_board(self):
        score = 0

        PATTERN_SCORES = {
            4: 1000,  # Four in a line
            3: 100,   # Three in a line
            2: 10,    # Two in a line
        }

        marked = np.zeros((6, 7), dtype=bool)

        # Check for the player's threats and add to score
        for pattern_len in range(4, 1, -1):
            patterns_count, marked = self.count_patterns(self.board, 2, pattern_len, marked)
            score += PATTERN_SCORES[pattern_len] * patterns_count

        # Now, check for opponent's threats and subtract from score
        # opponent = 3 - self.player
        marked = np.zeros((6, 7), dtype=bool)
        for pattern_len in range(4, 1, -1):
            patterns_count, marked = self.count_patterns(self.board, 1, pattern_len, marked)
            score -= PATTERN_SCORES[pattern_len] * patterns_count

        return score
    
    def update_win_count(self, winner):
        if winner in self.win_count:
            self.win_count[winner] += 1

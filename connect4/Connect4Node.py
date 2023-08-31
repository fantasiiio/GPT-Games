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
    def __init__(self, board = None, player = 1, is_terminal = False, last_move=None, history=[], winner=None, resnet = None):
        if board is not None:
            type = self.detect_board_type(board)
            if(type == "ndarray"):
                self.board = self.board_to_int(board)
            elif(type.startswith("int")):
                self.board = board
        self.player = player
        self._is_terminal = is_terminal
        self.reward = {1: 0, 2:0}
        self.total_reward = {1: 0, 2:0}
        self.last_move = last_move
        self.history = history if history is not None else []  
        self.history = history.copy() 
        self.children = []
        self.winner = winner
        self.Q = {1: 0, 2:0}
        self.N = {1: 0, 2:0}
        self.visited = False
        self.win_count = {1: 0, 2: 0}
        self.visit_count = 0
        self.depth = -1
        self.simulation_paths = []
        self.simulated = False
        self.uct_value = {1: 0, 2: 0}
        self.hash = hash((self.board, tuple(self.history)))

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

    def int_to_board(self):
        rows, cols = 6, 7
        board = np.zeros((rows, cols), dtype=np.int8)
        mask = 0b11  # Mask to extract 2 bits
        
        for row in range(rows):
            for col in range(cols):
                # Calculate the position of the bits in the integer
                pos = 2 * (row * cols + col)
                # Extract the bits for the current cell and assign it to the board
                board[row, col] = (self.board >> pos) & mask
        
        return board

    def board_to_int(self, board):
        board_int = 0
        for row in range(6):
            for col in range(7):
                value = int(board[row][col])
                shift_value = 2 * (row * 7 + col)
                mask = value << shift_value
                board_int |= mask
        return board_int          


    @lru_cache(maxsize=None)
    def get_cell(self, row, col):
        shift_value = 2 * (row * 7 + col)
        mask = 0b11 << shift_value
        return (self.board & mask) >> shift_value
        
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
                        opponent = 3 - self.player                     
                        new_node = Connect4Node(board=new_board, player=opponent, last_move=col, history=new_history, winner=self.winner)
                        if(not hasattr(new_node, "board")):
                            new_node = Connect4Node(board=new_board, player=opponent)
                        new_node.set_cell(row, col, opponent)
                        is_terminal, player_win = new_node.check_terminal()
                        new_node.winner = opponent if is_terminal and player_win else None
                        new_node._is_terminal = is_terminal
                        if is_terminal:
                            new_node.reward[new_node.player] = new_node.evaluate_board()
                            new_node.total_reward[new_node.player] = new_node.reward[new_node.player]
                            new_node.update_win_count(new_node.winner)

                        self.children.append(new_node)
                        break
        return self.children


    def check_terminal(self):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        rows, cols = 6, 7
        
        for row in range(rows):
            for col in range(cols):
                current_cell = self.get_cell(row, col)
                
                # Skip empty cells
                if current_cell == 0:
                    continue
                
                for dr, dc in directions:
                    # Limit the search space to avoid unnecessary checks
                    if not (0 <= row + 3*dr < rows and 0 <= col + 3*dc < cols):
                        continue
                    
                    count = 0
                    for i in range(4):  # You only need to check the next 3 cells
                        r, c = row + dr * i, col + dc * i
                        if self.get_cell(r, c) == current_cell:
                            count += 1
                        else:
                            break  # Sequence broken, no need to continue
                        
                        if count == 4:
                            return True, True  # Winning condition met
                    
        if self.is_board_full():
            return True, False  # Draw condition
            
        return False, False  # Game is not over


    
    def is_board_full(self):
        mask = 0b11  # Binary mask for two bits
        for i in range(42):  # Total cells in a 6x7 board
            cell_value = (self.board >> (2 * i)) & mask
            if cell_value == 0:
                return False
        return True
    
    def is_terminal(self):
        return self._is_terminal

    def __eq__(self, other):
        if isinstance(other, Connect4Node):
            return self.board == other.board and self.history == other.history
        return False

    def __hash__(self):
        return self.hash
    
    def get_valid_moves(self):
        rows, cols = 6, 7
        valid_moves = []

        for child in self.children:
            col = child.last_move
            # Check if the top cell of the column is empty
            if self.get_cell(rows-1, col) == 0:
                valid_moves.append(child)

        return valid_moves
    
    def is_valid_location(self, col):
        return self.get_cell(5, col) == 0

    def find_random_child(self):
        if self.is_terminal():
            return None
        if not self.children:
            self.create_children()
            return random.choice(self.children)
        else:
            available_moves = self.get_valid_moves()
            best_child = self._uct_select(available_moves)
            return best_child
    
    # def _uct_select(self, node):
    #     "Select a child of node, balancing exploration & exploitation"

    #     # All children of node should already be expanded:
    #     assert all(n in self.children for n in self.children[node])

    #     log_N_vertex = math.log(self.N[node])

    #     def uct(n):
    #         "Upper confidence bound for trees"
    #         return self.Q[n] / self.N[n] + self.exploration_weight * math.sqrt(
    #             log_N_vertex / self.N[n]
    #         )

    #     return max(self.children[node], key=uct)

    def _uct_select(self, nodeList):
        total_simulations = self.N[1] + self.N[2]
        total_simulations = 1 if total_simulations == 0 else total_simulations
        log_N = math.log(total_simulations)
        def uct(n):
            N = n.N[n.player]+1
            Q = n.Q[n.player] 
            
            C = 2
            if N == 0:
                return float("inf")

            exploitation_value = n.win_count[n.player] / (N)

            if total_simulations > 0:
                exploration_value = C * math.sqrt(log_N / (N))
            else:
                exploration_value = 0
                
            return exploitation_value + exploration_value    
        
        for n in nodeList:
            n.uct_value[n.player] = uct(n)        
         
            
        return max(nodeList, key=lambda n: n.uct_value[n.player])

    #  This function counts the number of potential patterns of a given length that could be extended to 4-in-a-line on a board.
    def count_potential_patterns(self, player, length, debug=False):
        count = 0
        rows, cols = 6, 7
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # (dx, dy) for horizontal, vertical, and both diagonals

        empty_spaces_needed = 4 - length

        for dx, dy in directions:
            if debug:
                print(f"Checking direction ({dx}, {dy})")  # Debug line
            for i in range(rows):
                for j in range(cols):
                    if i + (4 - 1) * dx >= rows or j + (4 - 1) * dy < 0 or j + (4 - 1) * dy >= cols:
                        continue

                    pattern = [self.get_cell(i + k * dx, j + k * dy) for k in range(4)]
                    
                    if pattern.count(player) == length and pattern.count(0) == empty_spaces_needed:
                        if debug:
                            # Generate board visualization for each potential pattern
                            visual_board = [['.' for _ in range(cols)] for _ in range(rows)]
                        for k in range(4):
                            row, col = i + k * dx, j + k * dy
                            cell_value = self.get_cell(row, col)
                            if debug:
                                visual_board[row][col] = str(cell_value) if cell_value == player else 'x'
                        
                        if debug:
                            # Print the visual board
                            print("Potential pattern found:")
                            for row in visual_board:
                                print(" ".join(row))
                        
                        count += 1
                            
        return count


    def evaluate_board(self):
        score = 0

        PATTERN_SCORES = {
            4: 1000,  # Four in a line
            3: 100,   # Three in a line
            2: 10,    # Two in a line
        }

        # Check for the player's threats and add to score
        for pattern_len in range(4, 1, -1):
            patterns_count = self.count_potential_patterns(self.player, pattern_len)
            score += PATTERN_SCORES[pattern_len] * patterns_count

        return score
    
    def update_win_count(self, winner):
        if winner in self.win_count:
            self.win_count[winner] += 1

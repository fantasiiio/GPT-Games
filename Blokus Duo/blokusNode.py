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
from BlokusDuo import Board
from bitGrid import BitGrid

gen = itertools.count(1)
step = itertools.count(1)

SHIFT_VALUES = [[2 * (row * 7 + col) for col in range(7)] for row in range(7)]

class Blokus4Node(Board):
    def __init__(self, board = None, player = 1, is_terminal = False, last_move=None, history=[], winner=None):
        if board is not None:
            type = self.detect_board_type(board)
            if(type == "ndarray"):
                self.board = self.board_to_int(board)
            elif(type.startswith("int")):
                self.board = board


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

    def create_children(self):
        if self.is_terminal():
            return []
        for col in range(7):
            new_board = BitGrid(3)
            new_board.compressed_grid = self.board.compressed_grid[:]
            for row in range(6):
                if self.get_cell(row, col) == 0:
                    new_history = self.history + [col]        
                    opponent = 3 - self.player                     
                    new_node = Blokus4Node(board=new_board, player=opponent, last_move=col, history=new_history, winner=self.winner)
                    if(not hasattr(new_node, "board")):
                        new_node = Blokus4Node(board=new_board, player=opponent)
                    new_node.set_cell(row, col, opponent)
                    is_terminal, player_win = new_node.check_terminal()
                    new_node.winner = opponent if is_terminal and player_win else None
                    new_node.is_terminal = is_terminal
                    if is_terminal:
                        new_node.reward[new_node.player] = new_node.evaluate_board()
                        new_node.total_reward[new_node.player] = new_node.reward[new_node.player]
                        new_node.update_win_count(new_node.winner)

                    self.children.append(new_node)
                    break
        return self.children


    def is_terminal(self):
        return self.is_terminal

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

    
    def update_win_count(self, winner):
        if winner in self.win_count:
            self.win_count[winner] += 1

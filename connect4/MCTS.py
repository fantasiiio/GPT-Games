from memory_profiler import profile
import numpy as np
from igraph import Graph, plot
from ete3 import TreeStyle
from ete3 import Tree
from total_size import total_size
from tree import TreeNode, TreePlotter
import networkx as nx
import matplotlib.pyplot as plt
from mctsTree import MCTSTree

"""
A minimal implementation of Monte Carlo tree search (MCTS) in Python 3
Luke Harold Miles, July 2019, Public Domain Dedication
See also https://en.wikipedia.org/wiki/Monte_Carlo_tree_search
https://gist.github.com/qpwo/c538c6f73727e254fdc7fab81024f6e1
"""
from abc import ABC, abstractmethod
from collections import defaultdict
import math

import ete3
class MCTS:
    "Monte Carlo tree searcher. First rollout the tree then choose a move."

    def __init__(self, Q = defaultdict(int), N = defaultdict(int), root_node = None, exploration_weight=1):
        self.root_node = root_node
        self.exploration_weight = exploration_weight


    def choose(self, node):
        "Choose the best successor of node. (Choose a move in the game)"
        if node.is_terminal():
            raise RuntimeError(f"choose called on terminal node {node}")

        if not node.children:
            return node.find_random_child()

        def score(n):
            if n.N == 0:
                return float("-inf")  
            return n.Q / n.N

        return max(node.children, key=score)

    def do_rollout(self, node):        
        if self.root_node is None:
            self.root_node = node
        "Make the tree one layer better. (Train for one iteration.)"
        path = self._select(node)
        leaf = path[-1]
        self._expand(leaf)
        reward, winner = self._simulate(leaf)
        self._backpropagate(path, reward, winner)

    def _select(self, node):
        "Find an unexplored descendant of `node`"
        path = []

        while True:
            path.append(node)

            if not node.children:
                # node is either unexplored or terminal
                return path

            children = node.children
            unexplored = [child for child in children if not child.children]

            if unexplored:
                # Choose randomly an unexplored child node 
                best_child = np.random.choice(unexplored)
                path.append(best_child)
                return path

            node = node._uct_select(node.children)  # descend a layer deeper


    def _expand(self, node):
        "Update the `children` dict with the children of `node`"
        if node.children:
            return  # already expanded
        node.children = node.create_children()
        node = node
    
    def _simulate(self, node):
        path = []
        starting_node = node
        while True:
            path.append(node.last_move)
            if not node.visited:
                node.reward = node.evaluate_board()
            if node.is_terminal():
                starting_node.simulation_paths[','.join(map(str, path))] = path
                return node.reward, node.player
            node = node.find_random_child()

    def _backpropagate(self, path, reward, winner, gamma = 0.5):
        "Send the reward back up to the ancestors of the leaf"
        multiplicator = 1
        total_reward = 0
        for node in reversed(path):
            total_reward += node.reward
            node.update_win_count(winner)
            node.N += 1
            node.Q += total_reward * multiplicator
            total_reward *= gamma
            node.visited = True
            multiplicator = 1 - multiplicator  # Flip the multiplicator for the next player

        depth = 0
        for node in path:
            node.depth = depth
            depth += 1



    def find_uncommon_elements(self, list1, list2):
        set1 = set(list1)
        set2 = set(list2)
        
        # Find elements that are in list1 but not in list2
        difference1 = set1 - set2
        
        # Find elements that are in list2 but not in list1
        difference2 = set2 - set1
        
        # Combine the two sets of differences
        result = difference1.union(difference2)
        
        return list(result)


    def mcts_to_tree_node(self, mcts_node):
        tree_node = TreeNode(mcts_node)
        tree_node.data = mcts_node.simulation_paths
        tree_node.set_visible(mcts_node.visited)
        for child in mcts_node.children:
            tree_node.add_child(self.mcts_to_tree_node(child))
        return tree_node

    def draw_tree(self, root_node):
        root_node = root_node if root_node is None else self.root_node
        tree_root = self.mcts_to_tree_node(root_node)
        tree_plotter = MCTSTree(tree_root)
        tree_plotter.start()    
    

    def propagate_win_count(self, node):
        if node.is_terminal():
            node.win_count = {1: 0, 2: 0}
            node.win_count[node.winner] = 1
            node.win_delta = node.win_count[1] - node.win_count[2]
            return node.win_count
        
        total_win_count = {1: 0, 2: 0}
        total_win_delta = 0
        for child in node.children:
            child_win_count = self.propagate_win_count(child)
            total_win_count[1] += child_win_count[1]
            total_win_count[2] += child_win_count[2]


        if not hasattr(node, 'win_count'):
            node.win_count = {1: 0, 2: 0}
        node.win_count[1] += total_win_count[1]
        node.win_count[2] += total_win_count[2]

        # Update and backpropagate the win_delta for this node
        node.win_delta = node.win_count[1] - node.win_count[2]

        return node.win_count



    def propagate_win_count_root(self):
        self.propagate_win_count(self.root_node)


class Node(ABC):
    """
    A representation of a single board state.
    MCTS works by constructing a tree of these Nodes.
    Could be e.g. a chess or checkers board state.
    """

    @abstractmethod
    def create_children(self):
        "All possible successors of this board state"
        return set()

    @abstractmethod
    def find_random_child(self):
        "Random successor of this board state (for more efficient simulation)"
        return None

    @abstractmethod
    def is_terminal(self):
        "Returns True if the node has no children"
        return True

    @abstractmethod
    def reward(self):
        "Assumes `self` is terminal node. 1=win, 0=loss, .5=tie, etc"
        return 0

    @abstractmethod
    def __hash__(self):
        "Nodes must be hashable"
        return 123456789

    @abstractmethod
    def __eq__(node1, node2):
        "Nodes must be comparable"
        return True
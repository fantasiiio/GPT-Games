from memory_profiler import profile
import numpy as np
from igraph import Graph, plot
from ete3 import TreeStyle
from ete3 import Tree
from total_size import total_size
from tree3 import TreeNode
import networkx as nx
import matplotlib.pyplot as plt
from mctsTree import MCTSTree
import random

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
            #if n.N[n.player] == 0:
            #    return float("-inf")  
            return (n.win_count[n.player] - n.win_count[3-n.player]) / n.N[n.player]
            #return n.total_reward[n.player]

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

            #node = random.choice(children)  # descend a layer deeper
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
            node.simulated = True
            path.append(node.last_move)
            is_terminal = node.check_terminal()
            #if not node.visited:
                # node.reward[node.player] = node.evaluate_board()
                # is_terminal = node.check_terminal()
            if is_terminal[0]:
                starting_node.simulation_paths.append(path)
                # result_reward = self.back_propagate_simulation_reward(path, starting_node)
                return 0, node.player
            node = node.find_random_child()


    def find_nodes_by_path(self, node, path):
        result = []
        
        # Base case: if the path is empty, return the current node
        if not path:
            return [node]
        
        # Add the current node to the result list as it is part of the path being traversed
        result.append(node)
        
        # Look for the first element of the path among the children of the current node
        for child in node.children:
            if len(path) > 1 and child.last_move == path[1]:
                found_nodes = self.find_nodes_by_path(child, path[1:])
                
                if found_nodes:  # If a non-empty list is returned
                    result.extend(found_nodes)
                    break  # No need to look further since we found a matching path
                    
        return result


    def back_propagate_simulation_reward(self, path, starting_node, gamma=0.9):
        total_reward = {1: 0, 2:0}
        nodes = self.find_nodes_by_path(starting_node, path)
        for node in reversed(nodes):
            total_reward[node.player] += node.reward[node.player]
            node.total_reward[1] = total_reward[1]
            node.total_reward[2] = total_reward[2]
            total_reward[node.player] *= gamma
        return total_reward

    def _backpropagate(self, path, reward, winner, gamma = 0.9):
        "Send the reward back up to the ancestors of the leaf"
        total_reward = {1: 0, 2:0}# reward
        for node in reversed(path):
            total_reward[node.player] += node.reward[node.player]
            node.update_win_count(winner)
            node.N[node.player] += 1
            node.Q[node.player] += total_reward[node.player] 
            total_reward[node.player] *= gamma
            node.visited = True

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
        tree_node.index = mcts_node.last_move
        for child in mcts_node.children:
            if not child.visited and not child.simulated:
                continue
            tree_node.add_child(self.mcts_to_tree_node(child))
        return tree_node

    def draw_tree(self, root_node):
        root_node = root_node if root_node is None else self.root_node
        tree_root = self.mcts_to_tree_node(root_node)
        tree_plotter = MCTSTree(tree_root)
        tree_plotter.start()    
    

    # def propagate_win_count(self, node):
    #     if node.is_terminal():
    #         node.win_count = {1: 0, 2: 0}
    #         node.win_count[node.winner] = 1
    #         node.win_delta = node.win_count[1] - node.win_count[2]
    #         return node.win_count
        
    #     total_win_count = {1: 0, 2: 0}
    #     total_win_delta = 0
    #     for child in node.children:
    #         child_win_count = self.propagate_win_count(child)
    #         total_win_count[1] += child_win_count[1]
    #         total_win_count[2] += child_win_count[2]


    #     if not hasattr(node, 'win_count'):
    #         node.win_count = {1: 0, 2: 0}
    #     node.win_count[1] += total_win_count[1]
    #     node.win_count[2] += total_win_count[2]

    #     # Update and backpropagate the win_delta for this node
    #     node.win_delta = node.win_count[1] - node.win_count[2]

    #     return node.win_count



    # def propagate_win_count_root(self):
    #     self.propagate_win_count(self.root_node)


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
    def __hash__(self):
        "Nodes must be hashable"
        return 123456789

    @abstractmethod
    def __eq__(node1, node2):
        "Nodes must be comparable"
        return True
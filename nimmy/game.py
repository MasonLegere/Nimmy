import math
from enum import Enum

'''
References: 
    - https://github.com/deepd/nim-game
    - https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning
'''

# Game states with respect to the
GameStates = Enum('GameStates', 'playing win loss invalid')


class GameInstance:

    def __init__(self, state):
        self.num_piles = len(state)

        self.state = state
        self.seen_states = {}
        self.terminating_states = [[0] * self.num_piles, [0] * max(0, self.num_piles - 3) + [2, 2, 2],
                                   [0] * max(0, self.num_piles - 3) + [1, 2, 3],
                                   [0] * max(0, self.num_piles - 4) + [1, 1, 2, 2]]

        self.game_state = GameStates.playing
        if sorted(self.state) == self.terminating_states[0]:
            self.game_state = GameStates.invalid

    # Returns the possible game states that can be achieved from a given move applied to parameter input state.
    # States are sorted for invariance purposes such that in the future moves can be ran in constant time checks.
    @staticmethod
    def get_children(state):
        children = []
        seen_states = set()

        for i in range(len(state)):
            for j in range(1, state[i] + 1):
                child = state.copy()
                child[i] -= j
                child.sort()

                # Convert to immutable type so it can be hashed

                child_tuple = tuple(child)
                if child_tuple not in seen_states:
                    seen_states.add(child_tuple)
                    children.append((child, child_tuple))
        return children

    # Returns the next move from the AI given the current state along with modifying the internal game state of the
    # instance. If the state is already in a losing then 1 is returned denoting a winning state along with the
    # original array
    def next(self):
        move_path = self.alpha_beta_pruning(self.state, -math.inf, math.inf, True)
        self.state = move_path[1][1]

        if self.state in self.terminating_states:
            self.game_state = GameStates.loss

        return move_path[0], self.state

    # Handles a player's move modifying the game state. A player's move is specified as the pile to pull from as well
    # the number of the beads to pull. Returns a boolean value corresponding to if the move was valid and performed.
    # In the case where the move was not valid, it will of course not be performed and the game state will not change.
    def player_move(self, peg, amount):

        peg -= 1 # move to zero index
        is_valid = (0 <= peg < len(self.state)) and (0 < amount <= self.state[peg])

        if is_valid:
            self.state[peg] -= amount

        if sorted(self.state) in self.terminating_states:
            self.game_state = GameStates.win

        return is_valid

    # Helper function that either:
    #   1) finds that the game path has already been computed taking into account 'equivalent' game states. That is,
    #       board configurations regardless of order
    #   2) moves recursive call further and stores values once computed
    def find_or_tunnel(self, child_pair, alpha, beta, maximizing_player):

        args = (child_pair[1], alpha, beta, maximizing_player)

        # we've already computed this game path
        if args in self.seen_states:
            val, next_states = self.seen_states[args]
        else:
            val, next_states = self.alpha_beta_pruning(child_pair[0], alpha, beta, maximizing_player)
            self.seen_states[args] = val, next_states

        return val, next_states

    # Preforms minimax algorithm with alpha-beta pruning while using memoization to cache/recall previously seen
    # game states.
    def alpha_beta_pruning(self, state, alpha, beta, maximizing_player):

        state_list = [state]

        # Check if opponent lost on their previous turn and that we are not in the starting state
        if state in self.terminating_states and state != self.state:
            if maximizing_player:
                return 1, state_list
            else:
                return -1, state_list

        unseen_children = GameInstance.get_children(state)

        if maximizing_player:
            bound = -math.inf
            path = []
            for child_tuple in unseen_children:
                child_bound, child_state = self.find_or_tunnel(child_tuple, alpha, beta, False)

                if child_bound > bound:
                    bound = child_bound
                    path = child_state

                alpha = max(alpha, child_bound)
                if alpha >= beta:
                    break

            return bound, state_list + path
        else:
            bound = math.inf
            path = []
            for child_tuple in unseen_children:
                child_bound, child_state = self.find_or_tunnel(child_tuple, alpha, beta, True)

                if child_bound < bound:
                    bound = child_bound
                    path = child_state

                beta = min(beta, child_bound)
                if beta <= alpha:
                    break

            return bound, state_list + path

    @staticmethod
    def is_valid_state(input_list):
        return all(i >= 0 for i in input_list)

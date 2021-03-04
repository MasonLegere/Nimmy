import math

'''
References: 
    - https://github.com/deepd/nim-game
    - https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning
'''


class GameInstance:

    def __init__(self, state):
        num_piles = len(state)

        self.state = state
        self.seen_states = {}
        self.terminating_states = [[0] * num_piles, [0] * max(0, num_piles - 3) + [2, 2, 2],
                                   [0] * max(0, num_piles - 3) + [1, 2, 3]]

    @staticmethod
    def get_children(state):
        children = []
        seen_states = set()

        for i in range(len(state)):
            for j in range(1, state[i] + 1):
                child = state.copy()
                child[i] -= j

                # Convert to immutable type so it can be hashed
                child_tuple = tuple(sorted(child))

                if child_tuple not in seen_states:
                    seen_states.add(child_tuple)
                    children.append((child, child_tuple))
        return children

    def next(self):
        if self.state in self.terminating_states:
            return self.state
        self.state = self.alpha_beta_pruning(self.state, -math.inf, math.inf, True)[1]
        return self.state

    # Helper function that either:
    #   1) finds that the game path has already been computed taking into account 'equivalent' game states. That is,
    #       board configurations regardless of order
    #   2) moves recursive call further and stores values once computed
    def find_or_tunnel(self, child_pair, alpha, beta, maximizing_player):
        args = (child_pair[1], alpha, beta, maximizing_player)
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

        # Check if opponent lost on their previous turn
        if state in self.terminating_states:
            if maximizing_player:
                return 1, state_list
            else:
                return -1, state_list

        unseen_children = self.get_children(state)

        if maximizing_player:
            bound = -math.inf
            path = None
            for child_pair in unseen_children:
                val, next_states = self.find_or_tunnel(child_pair, alpha, beta, not maximizing_player)
                if val > bound:
                    bound = val
                    path = next_states
                alpha = max(alpha, val)
                if alpha >= beta:
                    break
            return bound, state_list + path
        else:
            bound = math.inf
            path = None
            for child_pair in unseen_children:
                val, next_states = self.find_or_tunnel(child_pair, alpha, beta, not maximizing_player)
                if val < bound:
                    bound = val
                    path = next_states
                beta = min(beta, val)
                if beta <= alpha:
                    break
            return bound, state_list + path

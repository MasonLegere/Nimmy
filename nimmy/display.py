import argparse
from enum import Enum
from math import floor

import blessed

from nimmy.game import GameInstance, GameStates

up, left = ('w', 'k', 'KEY_UP'), ('a', 'h', 'KEY_LEFT')
down, right = ('s', 'j', 'KEY_DOWN'), ('d', 'l', 'KEY_RIGHT')
Direction = Enum('Direction', 'up left down right')

Turn = Enum('Turn', 'player cpu')

grid_moves = {}
for keys, direction in zip((up, left, down, right), Direction):
    grid_moves.update(dict.fromkeys(keys, direction))

parser = argparse.ArgumentParser(
    description="Play a variation of the game of Nim against a computer",
    epilog="Use the arrow, wasd or hjkl keys to move select tiles and ENTER to remove them as well as to ask the "
           "computer to make a move.")

requiredNamed = parser.add_argument_group('required arguments')
requiredNamed.add_argument('-s', '--state', help='String of non-negative integers separated by commas '
                                                 'representing the initial state of the board', required=True,
                           type=lambda s: [int(item) for item in s.split(',')], dest='state')
parser.add_argument('--cpu', dest='starting_turn', action='store_false',
                    help='Boolean flag to denote if the cpu goes first')
parser.set_defaults(feature=True)


def main():
    term = blessed.Terminal()
    config = {'max_stack': 9}

    args = parser.parse_args()
    state = args.state

    instance = GameInstance(state)
    display = GameDisplay(term, instance, config)
    current_turn = Turn.player

    if not args.starting_turn:
        current_turn = Turn.cpu

    with term.cbreak(), term.hidden_cursor(), term.fullscreen():
        print(term.home + term.clear)
        display.draw_move_title(current_turn)
        display.draw_board()
        display.draw_history()

        if not GameInstance.is_valid_state(state):
            instance.game_state = GameStates.invalid

        while True:
            key = term.inkey()
            if key in ('q', 'KEY_ESCAPE'):
                break

            direction = grid_moves.get(key.name or key)
            if instance.game_state is GameStates.playing:

                if key.name == 'KEY_ENTER':

                    if current_turn is Turn.player:
                        if display.drop_beans():
                            display.state_history.append(str(instance.state.copy()) + '  PLAYER')
                            current_turn = Turn.cpu

                    else:
                        instance.next()
                        display.update_selected_amount()
                        display.state_history.append(str(instance.state.copy()) + '  CPU')
                        current_turn = Turn.player

                    if instance.game_state is GameStates.playing:
                        print(term.clear)
                        display.draw_move_title(current_turn)

                    else:
                        print(term.clear)
                        display.draw_game_state(instance.game_state)

                display.draw_history()
                display.draw_board(direction)

            else:
                print(term.clear)
                display.draw_history()
                display.draw_board()
                display.draw_game_state(instance.game_state)


class GameDisplay:
    BEAN = '█████████'
    ERASER = '         '

    PLAYER_TURN_STRING = 'Your Turn!'
    CPU_TURN_STRING = 'Press Enter for the CPU to Move!'

    def __init__(self, term, instance, config):
        self.term = term
        self.instance = instance
        self.config = config

        self.pile_selection = 0
        self.amount_selection = 1
        self.nonempty_piles = [i for i in range(len(self.instance.state)) if self.instance.state[i] > 0]
        self.state_history = [str(self.instance.state.copy()) + '  START']

    # Draws the history of the last 10 state changes in the top left of the display as well as who made the move that
    # brought the game to that state
    def draw_history(self):

        divider = '=' * 40
        vertical_divider = '|'
        self.state_history = self.state_history[-min(len(self.state_history), 10):]

        print(self.term.move_xy(2, 1) + divider)
        row = 2
        for state in self.state_history:
            print(self.term.move_xy(4, row) + str(state))
            row += 1

        row = 2
        for _ in range(10):
            print(self.term.move_xy(2, row) + vertical_divider)
            print(self.term.move_xy(41, row) + vertical_divider)
            row += 1

        print(self.term.move_xy(2, row) + divider)

    # Prints an indication of who's move it is to play next
    def draw_move_title(self, turn):

        title = GameDisplay.PLAYER_TURN_STRING

        if turn is Turn.cpu:
            title = GameDisplay.CPU_TURN_STRING

        center = int((self.term.width - len(title)) / 2)
        print(self.term.move_xy(center, 13) + title)

    # Draws the game state at the top of the board. This could be when the game concludes or if we start in an
    # invalid state
    def draw_game_state(self, game_state):

        game_string = self.term.red('The computer has won!')

        if game_state is GameStates.loss:
            game_string = self.term.green('You have won!')

        if game_state is GameStates.invalid:
            game_string = self.term.blue('Provided game state is invalid')

        center = int((self.term.width - len(game_string)) / 2)
        print(self.term.move_xy(center, 13) + game_string)

    # High level method that draws the complete board which includes the stacks of all the beans along with the cursor
    # movement patterns. This is often called following a full refresh to avoid state reappearing.
    def draw_board(self, direction=None):

        if direction:
            self._update_cursor(direction)

        gap_size = 3
        spacing = len(GameDisplay.BEAN) + gap_size

        board_width = len(self.instance.state) * spacing
        starting_position = self.term.height - 5

        buffers_space = int(floor((self.term.width - board_width) / 2))

        for stack_number, stack in enumerate(self.instance.state):
            self._draw_stack(buffers_space + stack_number * spacing, starting_position, stack_number, stack)

    # Draws the stack of each of the beans given the index of the stack and the number of beans for that stack. This
    # also draws the colours associated with the bean selection as well as the overhead arrow.
    # This is not good code and should be refactored.
    def _draw_stack(self, x_pos, y_pos, stack_number, amount):

        step_up = 2
        max_stack = self.config['max_stack']
        stack = ''
        for i in range(max_stack):
            if i < amount:
                stack += self.term.move_xy(x_pos, y_pos - step_up * i) + self._get_bean(stack_number, i)
            else:
                stack += self.term.move_xy(x_pos, y_pos - step_up * i) + GameDisplay.ERASER

        stack_title = self.term.move_xy(x_pos, y_pos + 3) + '    ' + str(self.term.bold(str(stack_number + 1))) + '    '
        if self.pile_selection == stack_number:
            stack_arrow = self.term.move_xy(x_pos + 4, y_pos - step_up * max_stack) + self.term.bold('↓')
        else:
            stack_arrow = self.term.move_xy(x_pos + 4, y_pos - step_up * max_stack) + self.term.bold(' ')
        print(stack + stack_title + stack_arrow, end='', flush=True)

    def _get_bean(self, x, y):
        if x == self.pile_selection and y >= self.instance.state[self.pile_selection] - self.amount_selection:
            return self.term.red(GameDisplay.BEAN)
        return GameDisplay.BEAN

    # Moves the position of the cursor for bean selection as a function of the movement keys. There is some logic here
    # around making sure any selection is feasible for the game to run correctly.
    def _update_cursor(self, direction):

        if direction is Direction.up:
            if self.instance.state[self.pile_selection] != 0:
                self.amount_selection = min(max(1, self.amount_selection - 1), self.instance.state[self.pile_selection])
        elif direction is Direction.down:
            if self.instance.state[self.pile_selection] != 0:
                self.amount_selection = max(self.amount_selection % (self.instance.state[self.pile_selection]) + 1,
                                            self.amount_selection)
        elif direction is Direction.right:
            self.pile_selection = (self.pile_selection + 1) % len(self.instance.state)
            self.amount_selection = min(self.instance.state[self.pile_selection], 1)
        elif direction is Direction.left:
            self.pile_selection = (self.pile_selection - 1) % len(self.instance.state)
            self.amount_selection = min(self.instance.state[self.pile_selection], 1)

    # Drops the number of beans based on the pile selection amount and the pile
    def drop_beans(self):

        is_valid = self.instance.player_move(self.pile_selection + 1, self.amount_selection)
        self.amount_selection = min(self.instance.state[self.pile_selection], 1)
        return is_valid

    # Helper function to modify the selected number of tiles when switching over piles
    def update_selected_amount(self):
        self.amount_selection = min(self.instance.state[self.pile_selection], 1)


if __name__ == '__main__':
    main()

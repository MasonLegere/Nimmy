from nimmy.game import GameInstance


# main event loop code here
def main(args=None):
    # example
    lst = [2, 9, 7, 7, 1, 2, 4, 4, 1, 2]
    game = GameInstance(lst)
    state = game.next()

    print(state)

from Game import Game
from Players import HeroAttPlayer, UIPlayer, MTCSPlayer, PlayCardPlayer, RandomPlayer
import numpy as np

def main():
    np.random.seed(986465)
    # g = Game([MTCSPlayer(), UIPlayer()])
    # g = Game([MTCSPlayer(), PlayCardPlayer()])
    # g = Game((HeroAttPlayer(),UIPlayer()))
    # g = Game([RandomPlayer(), PlayCardPlayer()])
    g = Game([RandomPlayer(), MTCSPlayer()])
    g.play()


if __name__ == "__main__":
    main()

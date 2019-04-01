from Game import Game
from Players import HeroAttPlayer, UIPlayer, MTCSPlayer, PlayCardPlayer

def main():
    # g = Game([MTCSPlayer(), UIPlayer()])
    g = Game([MTCSPlayer(), PlayCardPlayer()])
    # g = Game((HeroAttPlayer(),UIPlayer()))
    g.play()


if __name__ == "__main__":
    main()

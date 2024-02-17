from pathlib import Path

from engine.interpreter import Visitor
from engine.parser import parser


class Renderer:
    ...


def main():
    game_yaml = Path("game.yaml")
    ast = parser(game_yaml)
    renderer = Renderer()
    engine = Visitor(ast, renderer)

    engine.start()


if __name__ == "__main__":
    main()

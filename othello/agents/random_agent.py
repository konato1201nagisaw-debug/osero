import random

from othello.engine import get_legal_moves


class RandomAgent:
    def select_action(self, board: list[list[int]], player: int) -> tuple[int, int]:
        return random.choice(get_legal_moves(board, player))

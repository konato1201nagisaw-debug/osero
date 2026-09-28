from othello.engine import get_legal_moves, apply_move, count_stones


class GreedyAgent:
    """一手先で最も自分の石が多くなる手を選ぶ貪欲エージェント"""

    def select_action(self, board: list[list[int]], player: int) -> tuple[int, int]:
        legal = get_legal_moves(board, player)
        return max(legal, key=lambda m: count_stones(apply_move(board, player, m), player))

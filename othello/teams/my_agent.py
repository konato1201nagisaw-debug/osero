import random

from othello.engine import get_legal_moves, apply_move, count_stones

# マスの価値マップ: チームの考えで自由に変えてよい
# 正の値 = 有利なマス、負の値 = 危険なマス
WEIGHT_MAP = [
    [  0,  0,  0,  0,  0,  0,  0,  0],
    [  0,  0,  0,  0,  0,  0,  0,  0],
    [  0,  0,  0,  0,  0,  0,  0,  0],
    [  0,  0,  0,  0,  0,  0,  0,  0],
    [  0,  0,  0,  0,  0,  0,  0,  0],
    [  0,  0,  0,  0,  0,  0,  0,  0],
    [  0,  0,  0,  0,  0,  0,  0,  0],
    [  0,  0,  0,  0,  0,  0,  0,  0],
]


class MyAgent:
    def select_action(self, board: list[list[int]], player: int) -> tuple[int, int]:
        """
        board : 8×8の二重リスト（0=空, 1=黒, -1=白）
        player: 1（黒）または -1（白）
        return: (row, col) — 行・列とも0〜7の座標タプル
        パスはエンジンが処理するため、合法手があるときだけ呼ばれる。
        """
        legal = get_legal_moves(board, player)
        return self.choose(board, player, legal)

    def choose(self, board: list[list[int]], player: int, legal: list) -> tuple[int, int]:
        # ここを実装する（legal は空ではない。1手5秒以内）
        # ステップ1: マスの重み → 2: 着手後の盤面評価 → 3: 相手の応手
        # ヒント1: WEIGHT_MAP[r][c] でマスの価値を取得できる
        # ヒント2: apply_move(board, player, move) で着手後の盤面を取得できる
        # ヒント3: count_stones(board, player) で石数を数えられる
        return random.choice(legal)

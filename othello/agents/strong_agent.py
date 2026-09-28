"""
アルファベータ探索エージェント（教員デモ・チェック用）

AI-Othello-Player/agents/student_agent.py の評価関数とα-β探索を
本プロジェクトの 1/-1 エンコーディング向けに移植。
"""
import random
import time

from othello.engine import BLACK, EMPTY, WHITE, apply_move, count_stones, get_legal_moves


class StrongAgent:
    def select_action(self, board: list[list[int]], player: int) -> tuple[int, int]:
        _, move = self._alphabeta(
            board, player, depth=4, is_max=True,
            alpha=float("-inf"), beta=float("inf"),
            start=time.monotonic(),
        )
        if move is None:
            return random.choice(get_legal_moves(board, player))
        return move

    def _eval(self, board: list[list[int]], player: int) -> float:
        n = len(board)
        opponent = -player
        corners = [(0, 0), (0, n - 1), (n - 1, 0), (n - 1, n - 1)]

        # 角（永続的に安全なマス）
        corner = sum(
            100 if board[r][c] == player else -100 if board[r][c] == opponent else 0
            for r, c in corners
        )

        # 辺の石数（確定石とは限らない）
        edge_score = 0
        for r in range(n):
            for c in range(n):
                on_edge = r in (0, n - 1) or c in (0, n - 1)
                if board[r][c] == player and on_edge:
                    edge_score += 10
                elif board[r][c] == opponent and on_edge:
                    edge_score -= 10

        # 合法手数（mobility）：手が多いほど有利
        p_moves = len(get_legal_moves(board, player))
        o_moves = len(get_legal_moves(board, opponent))
        mobility = 10 * (p_moves - o_moves)

        # 石数（ゲーム進行度に応じて重みを上げる）
        total = sum(board[r][c] != EMPTY for r in range(n) for c in range(n))
        stage = total / (n * n)
        w = 0.2 if stage < 0.3 else 0.5 if stage < 0.7 else 1.0
        pieces = w * (count_stones(board, player) - count_stones(board, opponent))

        return corner + edge_score + mobility + pieces

    def _alphabeta(
        self,
        board: list[list[int]],
        player: int,
        depth: int,
        is_max: bool,
        alpha: float,
        beta: float,
        start: float,
    ) -> tuple[float, tuple[int, int] | None]:
        cur = player if is_max else -player
        legal = get_legal_moves(board, cur)

        if not legal:
            # 合法手がない場合：相手にも手がなければ終局
            if not get_legal_moves(board, -cur):
                diff = count_stones(board, player) - count_stones(board, -player)
                # 非終局の評価値より十分大きい値で、勝敗を最優先する。
                return (10000 + diff if diff > 0 else -10000 + diff if diff < 0 else 0), None
            # パス（手番を交代して続行）
            return self._alphabeta(board, player, depth, not is_max, alpha, beta, start)

        if depth == 0 or time.monotonic() - start > 1.9:
            return self._eval(board, player), None

        best_move = None
        if is_max:
            value = float("-inf")
            for move in legal:
                v, _ = self._alphabeta(
                    apply_move(board, player, move),
                    player, depth - 1, False, alpha, beta, start,
                )
                if v > value:
                    value, best_move = v, move
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
        else:
            value = float("inf")
            for move in legal:
                v, _ = self._alphabeta(
                    apply_move(board, -player, move),
                    player, depth - 1, True, alpha, beta, start,
                )
                if v < value:
                    value, best_move = v, move
                beta = min(beta, value)
                if alpha >= beta:
                    break

        return value, best_move

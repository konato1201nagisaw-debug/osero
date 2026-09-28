"""
観戦スクリプト

使い方:
  uv run python scripts/demo.py                                    # random vs random 1試合（fancy表示）
  uv run python scripts/demo.py --black strong --white mine        # strong vs mine
  uv run python scripts/demo.py --hints                             # 合法手をドット表示
  uv run python scripts/demo.py --black greedy --games 10          # 10試合、表示なしで一気に集計
"""

import argparse
import contextlib
import time
from pathlib import Path

_ROOT = Path(__file__).parent.parent

from othello.engine import (
    BLACK, WHITE,
    _safe_move, apply_move, count_stones, get_legal_moves,
    initial_board,
)

from othello.agent_runner import ProcessAgent

AGENT_CHOICES = ["random", "greedy", "strong", "mine"]


def load_agent(name: str):
    paths = {
        "random": _ROOT / "agents" / "random_agent.py",
        "greedy": _ROOT / "agents" / "greedy_agent.py",
        "strong": _ROOT / "agents" / "strong_agent.py",
        "mine":   _ROOT / "teams"  / "my_agent.py",
    }
    if name not in paths:
        raise ValueError(f"不明なエージェント: {name}。{AGENT_CHOICES} から選んでください")
    return ProcessAgent(paths[name])


def run_game(
    agent_b, agent_w,
    delay: float,
    tui=None,
    name_b: str = "黒",
    name_w: str = "白",
    show_hints: bool = False,
) -> int:
    board = initial_board()
    player = BLACK
    agents = {BLACK: agent_b, WHITE: agent_w}
    syms = {BLACK: "●黒", WHITE: "○白"}

    if tui:
        tui.update(board, player, name_b, name_w, show_hints=show_hints)
        time.sleep(delay)

    while True:
        legal = get_legal_moves(board, player)
        if not legal:
            player = -player
            if not get_legal_moves(board, player):
                break
            if tui:
                tui.update(board, player, name_b, name_w, passed=f"{syms[-player]}はパス", show_hints=show_hints)
                time.sleep(delay)
            continue

        move = _safe_move(agents[player], [row[:] for row in board], player, legal)

        move_text = None
        if tui:
            r, c = move
            move_text = f"{syms[player]} → {'abcdefgh'[c]}{r + 1}"

        board = apply_move(board, player, move)
        player = -player

        if tui:
            tui.update(board, player, name_b, name_w, last_move=move_text, show_hints=show_hints)
            time.sleep(delay)

    b, w = count_stones(board, BLACK), count_stones(board, WHITE)
    winner = BLACK if b > w else WHITE if w > b else 0

    if tui:
        if winner == BLACK:
            result = f"黒の勝ち  ● {b} — ○ {w}"
        elif winner == WHITE:
            result = f"白の勝ち  ● {b} — ○ {w}"
        else:
            result = f"引き分け  ● {b} — ○ {w}"
        tui.update(board, None, name_b, name_w, result=result)
        time.sleep(max(delay, 1.0))

    return winner


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--black", default="random", choices=AGENT_CHOICES)
    parser.add_argument("--white", default="random", choices=AGENT_CHOICES)
    parser.add_argument("--games", type=int, default=1)
    parser.add_argument("--delay", type=float, default=0.3,
                        help="手と手の間隔（秒、1試合のときのみ）")
    parser.add_argument("--hints", action="store_true",
                        help="合法手をドット表示（1試合のときのみ）")
    args = parser.parse_args()

    if args.games < 1:
        parser.error("--games は1以上にしてください")

    tui_cm = contextlib.nullcontext()
    if args.games == 1:
        from othello.tui import TUI
        tui_cm = TUI()

    results = {BLACK: 0, WHITE: 0, 0: 0}

    with tui_cm as tui:
        for _ in range(args.games):
            with load_agent(args.black) as agent_b, load_agent(args.white) as agent_w:
                winner = run_game(
                    agent_b, agent_w, args.delay, tui,
                    args.black, args.white, args.hints,
                )
            results[winner] += 1

    if args.games > 1:
        print(f"{args.games}試合  黒{results[BLACK]}勝 / 白{results[WHITE]}勝 / 引き分け{results[0]}")


if __name__ == "__main__":
    main()

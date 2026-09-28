import tempfile
import time
import unittest
from pathlib import Path

from agents.strong_agent import StrongAgent
from othello.agent_runner import ProcessAgent
from othello.engine import BLACK, WHITE, _safe_move, apply_move, get_legal_moves, initial_board


class EngineTests(unittest.TestCase):
    def test_initial_move_and_copy(self):
        board = initial_board()
        self.assertEqual(get_legal_moves(board, BLACK), [(2, 3), (3, 2), (4, 5), (5, 4)])
        after = apply_move(board, BLACK, (2, 3))
        self.assertEqual(after[3][3], BLACK)
        self.assertEqual(board[3][3], WHITE)

    def test_invalid_move_is_visible(self):
        class Invalid:
            def select_action(self, board, player):
                return (0, 0)
        board = initial_board()
        with self.assertRaisesRegex(ValueError, '不正な手'):
            _safe_move(Invalid(), board, BLACK, get_legal_moves(board, BLACK))

    def test_terminal_score_prioritizes_winner(self):
        # 黒が全ての角・辺を持つが、石数では28対36で負ける。
        board = [[BLACK if r in (0, 7) or c in (0, 7) else WHITE
                  for c in range(8)] for r in range(8)]
        agent = StrongAgent()
        for player, expected in ((BLACK, -10008), (WHITE, 10008)):
            score, move = agent._alphabeta(board, player, 4, True, -float('inf'), float('inf'), time.monotonic())
            self.assertEqual(score, expected)
            self.assertIsNone(move)
        board = [[BLACK] * 8 for _ in range(4)] + [[WHITE] * 8 for _ in range(4)]
        score, _ = agent._alphabeta(board, BLACK, 4, True, -float('inf'), float('inf'), time.monotonic())
        self.assertEqual(score, 0)


class ProcessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def agent(self, name, body):
        path = Path(self.temp.name) / (name + '.py')
        path.write_text(body)
        return path

    def test_timeout_stops_worker(self):
        path = self.agent('slow', 'import time\nclass Agent:\n def select_action(self, board, player):\n  time.sleep(30)\n')
        with ProcessAgent(path, timeout=.1) as agent:
            with self.assertRaises(TimeoutError):
                agent.select_action(initial_board(), BLACK)
            self.assertFalse(agent.process.is_alive())

    def test_traceback_preserved(self):
        path = self.agent('broken', 'class Agent:\n def select_action(self, board, player):\n  raise ValueError("student error")\n')
        with ProcessAgent(path) as agent:
            with self.assertRaisesRegex(RuntimeError, 'student error') as error:
                agent.select_action(initial_board(), BLACK)
            self.assertIn('Traceback', str(error.exception))

    def test_state_persists_and_resets(self):
        path = self.agent('state', 'class Agent:\n def __init__(self): self.n = 0\n def select_action(self, board, player):\n  self.n += 1\n  return self.n\n')
        with ProcessAgent(path) as agent:
            self.assertEqual(agent.select_action([], BLACK), 1)
            self.assertEqual(agent.select_action([], BLACK), 2)
        with ProcessAgent(path) as agent:
            self.assertEqual(agent.select_action([], BLACK), 1)


if __name__ == '__main__':
    unittest.main()

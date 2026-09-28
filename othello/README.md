# オセロ AI 演習

`teams/my_agent.py` の `WEIGHT_MAP` と `choose()` を編集し、強いエージェントを作ります。

## ファイル構成（編集するのは ★ だけ）

```
othello/                ← コマンドはすべてここで実行
├── README.md
├── pyproject.toml      # 依存ライブラリの定義
├── teams/
│   └── my_agent.py     # ★ 自分たちのエージェント（WEIGHT_MAP と choose()）
├── agents/             # 対戦相手: random / greedy / strong（strong は探索の参考実装）
├── othello/            # ゲームエンジン（engine.py に提供関数）
├── scripts/            # demo.py（対戦）
└── tests/              # 提供コードのテスト
```

`teams/my_agent.py` 以外は変更しないでください。提出時もこのファイルだけを使います。

## インストール

### 1. uv を入れる（初回のみ）

uv は Python 本体とライブラリをまとめて用意するツールです。ターミナルで次を実行します。

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```powershell
# Windows（PowerShell）
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

実行後にターミナルを開き直し、`uv --version` でバージョンが表示されれば完了です。
うまくいかない場合は https://docs.astral.sh/uv/getting-started/installation/ を参照してください。

### 2. 環境を作る

ターミナルでこの README があるフォルダに移動して実行します。

```bash
cd othello
uv sync
```

Python 3.11以上が無ければ uv が自動でダウンロードします。必要なライブラリは `rich` のみです。

### 3. 動作確認

```bash
uv run python scripts/demo.py --black mine --white random
```

盤面が表示され、1試合が最後まで進めば準備完了です。

## 実行方法

```bash
# 合法手をドット表示し、1手1秒でゆっくり観戦
uv run python scripts/demo.py --black mine --white random --hints --delay 1

# 黒白の両方で比較（合計40試合）
uv run python scripts/demo.py --black mine --white random --games 20
uv run python scripts/demo.py --black random --white mine --games 20

# 提供コードのテスト
uv run python -m unittest discover -s tests -v
```

| オプション | 意味 | 既定値 |
|---|---|---|
| `--black` / `--white` | 黒番・白番のエージェント | `random` |
| `--games` | 試合数。2以上で盤面を出さず勝敗だけ集計 | `1` |
| `--hints` | 合法手をドット表示（1試合のときのみ） | なし |
| `--delay` | 手と手の間隔（秒、1試合のときのみ） | `0.3` |

エージェント名: `random`（ランダム）、`greedy`（石数最大化）、`strong`（α-β探索）、`mine`（`teams/my_agent.py`）。
ランダムな相手との勝率にはばらつきがあるため、同じ試合数・両方の色で変更前後を比較してください。

## 実装の約束

- 盤面と `WEIGHT_MAP` は8×8の二重リストです。NumPy は不要です。
- `board[row][col]` は `0`=空、`1`=黒、`-1`=白。`player` は自分の色、`-player` は相手の色です。
- 座標は `(行, 列)`、どちらも `0〜7`。左上の a1 は `(0, 0)` です。
- `choose(board, player, legal)` は `legal` の中の座標タプルを1つ返してください。
- `choose()` が呼ばれるとき、`legal` は必ず空ではありません。実際の対戦でのパス・終局はエンジンが処理します。
- 盤面を直接書き換えず、`apply_move()` で次の盤面を作ってください。
- 1手の制限は5秒。実行スクリプトは別プロセスを使い、時間超過時は終了します。初期化は別枠で60秒です。
- エージェントは試合ごとに初期化され、同じ試合中は状態を保持します。
- demo は例外・不正な手・時間超過で停止し、原因を表示します。ランダム手への置き換えはしません。

## 課題

### ステップ1: マスの価値で選ぶ

`WEIGHT_MAP` の各マスに値を設定してください。正は有利、負は危険という意味です。
まずは「角を高くする」「角の隣を低くする」など、理由を考えましょう。
`choose()` で `WEIGHT_MAP[r][c]` が最大になる合法手を選びます。同点時の選び方も決めてください。

### ステップ2: 着手後の盤面全体を評価する

各合法手について `after = apply_move(board, player, move)` を作り、
自分の石の重みの合計から相手の石の重みの合計を引いて比較します。
「置いた場所だけを見る場合」と結果がどう違うか調べてください。
余裕があれば、相手と自分の合法手数の差も評価に加えてみましょう。

### ステップ3: 相手の応手まで読む

自分の各候補の後に、相手の合法手をすべて試します。
相手は自分にとって最も評価が低くなる手を選ぶと仮定し、その最悪値が一番高い候補を選びます。
評価は常に自分の色を基準にしてください。
探索内では、相手に手がなければパス、双方に手がなければ終局を扱う必要があります。

### 発展: 数手先を読む

ステップ3を再帰にし、ミニマックス探索、さらにα-β枝刈りに拡張します。
`agents/strong_agent.py` が参考実装です。終局では石数による勝敗を最優先に評価します。
探索の深さと実行時間の関係も調べてください。

## 提出物

- `teams/チーム名.py`：引数なしで作成できるクラスを1つ定義し、`select_action(board, player)` を持たせてください。`my_agent.py` を改名して提出できます。
- 短いレポート：戦略の仮説と理由、変更前後の対戦相手・試合数・黒白別の勝敗、結果の考察と残った課題。

## 提供関数

`from othello.engine import ...` で利用できます。

```python
get_legal_moves(board, player)      # 合法手 [(row, col), ...]。パスなら []
apply_move(board, player, move)     # 合法手を渡す。元を変更せず新しい盤面を返す
count_stones(board, player)         # 指定色の石数
initial_board()                    # 初期盤面
is_game_over(board)                # 双方が打てなければ True
play_game(agent_black, agent_white)  # 黒勝ち1、白勝ち-1、引き分け0
```

`play_game()` 自体には時間制限がありません。実行スクリプトでは `ProcessAgent` と組み合わせています。

import chess
import chess.engine

from app.core.config import find_stockfish


def _engine_path() -> str:
    path = find_stockfish()
    if not path:
        raise RuntimeError("Stockfish engine not found. Set STOCKFISH_PATH.")
    return path


def analyze_position(fen: str):
    board = chess.Board(fen)
    engine = chess.engine.SimpleEngine.popen_uci(_engine_path())
    try:
        result = engine.analyse(board, chess.engine.Limit(depth=15))
        best_move = result["pv"][0]
        score = result["score"].pov(chess.WHITE)
    finally:
        engine.quit()

    return {
        "evaluation": score.score(mate_score=10000) / 100,
        "best_move": board.san(best_move),
        "uci_move": best_move.uci(),
    }
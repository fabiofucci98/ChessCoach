
import os
import chess
import chess.engine


STOCKFISH_PATH = os.getenv(
    "STOCKFISH_PATH",
    "/usr/games/stockfish"
)


def analyze_position(fen: str):

    board = chess.Board(fen)

    engine = chess.engine.SimpleEngine.popen_uci(
        STOCKFISH_PATH
    )

    result = engine.analyse(
        board,
        chess.engine.Limit(
            depth=15
        )
    )

    best_move = result["pv"][0]

    score = result["score"].pov(
        chess.WHITE
    )

    engine.quit()


    return {
        "evaluation": score.score(
            mate_score=10000
        ) / 100,

        "best_move": board.san(best_move),

        "uci_move": best_move.uci(),
    }
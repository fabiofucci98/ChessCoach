"""Integration tests against a real Stockfish engine (skipped if not installed)."""
import uuid

import chess
import pytest

from app.core.config import find_stockfish
from app.core.stockfish import analyze_position
from app.routers.analysis import analyze_game_moves
from app.routers.play import _evaluate_after_player_move

STOCKFISH = find_stockfish()

pytestmark = pytest.mark.skipif(STOCKFISH is None, reason="Stockfish not installed on this machine")


def test_analyze_position_returns_eval_and_best_move():
    res = analyze_position(chess.Board().fen())
    assert "evaluation" in res
    assert "best_move" in res
    assert "uci_move" in res
    # Best move must be legal from the start position
    assert chess.Move.from_uci(res["uci_move"]) in chess.Board().legal_moves


def test_evaluate_after_player_move_returns_legal_stockfish_reply():
    start = chess.Board().fen()
    board_after = chess.Board(start)
    board_after.push_san("e4")

    a = _evaluate_after_player_move(start, board_after.fen())

    assert a["is_mistake"] is False
    assert a["sf_uci"] is not None
    reply = chess.Move.from_uci(a["sf_uci"])
    # The reply must be legal on the position AFTER the player's move
    assert reply in board_after.legal_moves


def test_analyze_game_moves_returns_list():
    pgn = "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6"
    result = analyze_game_moves(pgn, "white", uuid.uuid4(), uuid.uuid4())
    assert isinstance(result, list)

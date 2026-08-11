"""Unit tests for chess.com game parsing (games.py)."""
from app.routers.games import parse_chess_com_game


def test_parse_when_user_is_white_and_wins():
    data = {
        "uuid": "abc-123",
        "pgn": "",
        "time_control": "600",
        "white": {"username": "Me", "rating": 1500, "result": "win"},
        "black": {"username": "Rival", "rating": 1400, "result": "checkmated"},
    }
    g = parse_chess_com_game(data, "Me")
    assert g["external_game_id"] == "abc-123"
    assert g["player_color"] == "white"
    assert g["user_rating"] == 1500
    assert g["opponent_rating"] == 1400
    assert g["result"] == "win"


def test_parse_when_user_is_black_and_loses():
    data = {
        "uuid": "x",
        "pgn": "",
        "time_control": "300",
        "white": {"username": "Rival", "rating": 1600, "result": "win"},
        "black": {"username": "me", "rating": 1500, "result": "checkmated"},
    }
    g = parse_chess_com_game(data, "me")
    assert g["player_color"] == "black"
    assert g["user_rating"] == 1500
    assert g["opponent_rating"] == 1600
    assert g["result"] == "loss"


def test_parse_unknown_result_is_treated_as_loss():
    data = {
        "uuid": "y",
        "pgn": "",
        "white": {"username": "Me", "rating": 1500, "result": "something_weird"},
        "black": {"username": "R", "rating": 1400, "result": "win"},
    }
    g = parse_chess_com_game(data, "Me")
    assert g["player_color"] == "white"
    assert g["result"] == "loss"

"""Unit tests for the mistake classification helper (play.py)."""
from app.routers.play import classify_eval_drop


def test_good_moves_are_not_mistakes():
    assert classify_eval_drop(0.0) == (False, None)
    assert classify_eval_drop(2.0) == (False, None)
    assert classify_eval_drop(-0.4) == (False, None)


def test_inaccuracy():
    assert classify_eval_drop(-0.5) == (True, "inaccuracy")
    assert classify_eval_drop(-0.99) == (True, "inaccuracy")


def test_mistake():
    assert classify_eval_drop(-1.0) == (True, "mistake")
    assert classify_eval_drop(-2.4) == (True, "mistake")


def test_blunder():
    assert classify_eval_drop(-2.5) == (True, "blunder")
    assert classify_eval_drop(-5.0) == (True, "blunder")

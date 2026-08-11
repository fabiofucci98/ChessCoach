"""Unit tests for the SM-2 spaced-repetition scheduler (puzzles.py)."""
from app.routers.puzzles import sm2_update


def test_sm2_fail_resets_repetitions_and_interval():
    ef, reps, interval = sm2_update(2.5, 3, 20, quality=1)
    assert reps == 0
    assert interval == 1
    assert ef == 2.5  # easiness unchanged on failure


def test_sm2_first_correct():
    ef, reps, interval = sm2_update(2.5, 0, 0, quality=5)
    assert reps == 1
    assert interval == 1
    assert ef == 2.6


def test_sm2_second_correct():
    ef, reps, interval = sm2_update(2.5, 1, 1, quality=5)
    assert reps == 2
    assert interval == 6
    assert ef == 2.6


def test_sm2_subsequent_correct_scales_interval():
    ef, reps, interval = sm2_update(2.6, 2, 6, quality=5)
    assert reps == 3
    assert interval == round(6 * 2.6)  # 16
    assert ef == 2.7


def test_sm2_low_quality_makes_grade():
    ef, reps, interval = sm2_update(2.5, 1, 6, quality=2)  # quality < 3
    assert reps == 0
    assert interval == 1

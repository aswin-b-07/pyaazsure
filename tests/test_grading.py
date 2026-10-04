import pytest
from backend.services.grading import calculate_lot_grade


def test_grading_engine_calculations():
    """
    Tests grading engine logic with known sample predictions.
    """
    # Sample predictions: 7 Healthy, 2 Undersized, 1 Damaged = 10 total
    predictions = [
        {"predicted_class": "Healthy", "confidence": 92.0},
        {"predicted_class": "Healthy", "confidence": 90.0},
        {"predicted_class": "Healthy", "confidence": 88.0},
        {"predicted_class": "Healthy", "confidence": 95.0},
        {"predicted_class": "Healthy", "confidence": 91.0},
        {"predicted_class": "Healthy", "confidence": 89.0},
        {"predicted_class": "Healthy", "confidence": 93.0},
        {"predicted_class": "Undersized", "confidence": 85.0},
        {"predicted_class": "Undersized", "confidence": 87.0},
        {"predicted_class": "Damaged", "confidence": 90.0},
    ]

    res = calculate_lot_grade(predictions)

    assert res["total_analyzed"] == 10
    assert res["healthy_count"] == 7
    assert res["undersized_count"] == 2
    assert res["damaged_count"] == 1

    assert res["grade_a_pct"] == 70.0
    assert res["urs_pct"] == 20.0
    assert res["defective_pct"] == 10.0
    assert res["avg_confidence"] == 90.0
    assert res["needs_review"] is False
    assert res["status"] == "AI Assessment Complete"


def test_grading_engine_human_review_flag():
    """
    Verifies that low average AI confidence (< 80%) triggers the Human Review flag.
    """
    predictions = [
        {"predicted_class": "Healthy", "confidence": 72.0},
        {"predicted_class": "Healthy", "confidence": 75.0},
        {"predicted_class": "Healthy", "confidence": 78.0},
    ]

    res = calculate_lot_grade(predictions)

    assert res["avg_confidence"] == 75.0
    assert res["needs_review"] is True
    assert res["status"] == "Needs Human Review"

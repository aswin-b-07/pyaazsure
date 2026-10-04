import pytest
from backend.ml.mock_inference import mock_inference, CLASSES


def test_mock_inference_output():
    """
    Verifies that mock_inference returns a valid dictionary
    containing expected keys, valid predicted classes, and confidence between 70% and 99%.
    """
    result = mock_inference("uploads/test_sample.png")

    assert isinstance(result, dict)
    assert "predicted_class" in result
    assert "confidence" in result

    assert result["predicted_class"] in CLASSES
    assert 70.0 <= result["confidence"] <= 99.0
    assert result["is_mock"] is True

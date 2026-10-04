"""
=============================================================================
PYAAZSURE GRADING ENGINE
=============================================================================
This module is responsible for converting image-level predictions into
lot-level quality results based on official procurement and quality standards.

Grading Rules:
- Grade A %: Percentage of Healthy onions.
- URS % (Under Size / Minor Defect): Percentage of Undersized onions.
- Defective %: Combined percentage of Damaged, Rotten, and Sprouted onions.
- Human Review Flag: Triggered if average AI confidence < 80.0%.

This business logic is strictly decoupled from the ML inference layer.
=============================================================================
"""

from typing import List, Dict, Any


def calculate_lot_grade(predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes lot-level quality metrics from a list of image-level predictions.

    Args:
        predictions (list[dict]): List of dicts containing 'predicted_class' and 'confidence'.

    Returns:
        dict: Aggregated grading metrics including Grade A %, URS %, Defective %,
              average confidence, defect counts, and review status flag.
    """
    total = len(predictions)
    if total == 0:
        return {
            "total_analyzed": 0,
            "grade_a_pct": 0.0,
            "urs_pct": 0.0,
            "defective_pct": 0.0,
            "avg_confidence": 0.0,
            "needs_review": True,
            "status": "Needs Human Review (No Images Analyzed)",
            "healthy_count": 0,
            "damaged_count": 0,
            "rotten_count": 0,
            "sprouted_count": 0,
            "undersized_count": 0,
        }

    healthy_count = 0
    damaged_count = 0
    rotten_count = 0
    sprouted_count = 0
    undersized_count = 0
    confidence_sum = 0.0

    for pred in predictions:
        cls = pred.get("predicted_class", "").strip()
        conf = float(pred.get("confidence", 0.0))
        confidence_sum += conf

        if cls == "Healthy":
            healthy_count += 1
        elif cls == "Damaged":
            damaged_count += 1
        elif cls == "Rotten":
            rotten_count += 1
        elif cls == "Sprouted":
            sprouted_count += 1
        elif cls == "Undersized":
            undersized_count += 1
        else:
            # Fallback for unknown classes
            damaged_count += 1

    # Aggregations
    defective_count = damaged_count + rotten_count + sprouted_count

    grade_a_pct = round((healthy_count / total) * 100.0, 2)
    urs_pct = round((undersized_count / total) * 100.0, 2)
    defective_pct = round((defective_count / total) * 100.0, 2)
    avg_confidence = round(confidence_sum / total, 2)

    # Human Review Rule
    # Flag lot as "Needs Human Review" if average AI confidence is under 80%
    needs_review = avg_confidence < 80.0
    status = "Needs Human Review" if needs_review else "AI Assessment Complete"

    return {
        "total_analyzed": total,
        "grade_a_pct": grade_a_pct,
        "urs_pct": urs_pct,
        "defective_pct": defective_pct,
        "avg_confidence": avg_confidence,
        "needs_review": needs_review,
        "status": status,
        "healthy_count": healthy_count,
        "damaged_count": damaged_count,
        "rotten_count": rotten_count,
        "sprouted_count": sprouted_count,
        "undersized_count": undersized_count,
    }
